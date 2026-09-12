"""Games API Blueprint - Handles game session and question answering routes"""

from flask import Blueprint, request, abort, jsonify
from werkzeug.exceptions import BadRequest
from services import QuestionService, CategoryService, UserService, GameSessionService, GameSessionAnswerService
from data_access import db, GameSessionAnswerRepository, GameSessionRepository
from models import GameSession, Question
from utils import rate_limit

games_bp = Blueprint('games', __name__, url_prefix='')


def _get_request_json():
    """
    Safely get JSON from request, handling parsing errors gracefully.
    
    Returns:
        dict: Parsed JSON body, or None if body is empty/not JSON
        
    Raises:
        BadRequest: If JSON parsing fails
    """
    try:
        # Try to get JSON with force=False to get proper error on invalid JSON
        return request.get_json(force=False)
    except BadRequest as e:
        # Re-raise with a descriptive message containing 'JSON'
        abort(400, description="Request body must be valid JSON")


@games_bp.route('/games', methods=['POST'])
def create_game():
    """
    Create a new game session and return the first question
    
    Request body: {
        "user_id": int,
        "category_id": int (0 for all categories),
        "number_of_questions": int (optional, default=5)
    }
    
    Returns: {game_session_id, current_question_number, current_score, question, success}
    Errors: 400 (missing fields), 404 (user/category not found), 422 (invalid data)
    """
    try:
        body = _get_request_json()
        
        # Validate body exists
        if not body:
            abort(400, description="Request body must be JSON")
        
        user_id = body.get('user_id')
        category_id = body.get('category_id')
        number_of_questions = body.get('number_of_questions', 5)
        
        # Validate required fields
        if user_id is None or category_id is None:
            abort(400, description="Missing required fields: 'user_id', 'category_id'")
        
        # Validate user exists
        try:
            user = UserService.get_user(user_id)
        except ValueError:
            abort(404, description=f"User with id {user_id} not found")
        
        # Validate category exists (if not 0 for all)
        if category_id != 0:
            try:
                CategoryService.get_category(category_id)
            except ValueError:
                abort(404, description=f"Category with id {category_id} not found")
        
        # Validate number_of_questions
        if not isinstance(number_of_questions, int) or number_of_questions < 1 or number_of_questions > 20:
            abort(422, description="number_of_questions must be an integer between 1 and 20")
        
        # Validate capacity: ensure enough unique questions exist for requested count
        if category_id == 0:
            available_questions = QuestionService.count_total_questions()
        else:
            available_questions = QuestionService.count_questions_by_category(category_id)
        
        if available_questions < number_of_questions:
            abort(422, description=f'Insufficient unique questions available. Requested: {number_of_questions}, Available: {available_questions}')
        
        # Get first question - deterministically selected
        if category_id == 0:
            question = QuestionService.get_random_question()
        else:
            question = QuestionService.get_random_question_by_category(category_id)
        
        if not question:
            abort(404)
        
        # Create game session + record first question atomically
        try:
            game_session, first_answer = GameSessionService.create_game_session_with_first_question(
                user_id=user_id,
                score=0,
                first_question=question,
                category_id=category_id if category_id != 0 else None,
                number_of_questions=number_of_questions
            )
        except ValueError as e:
            abort(400, description=str(e))
        except Exception as e:
            abort(500, description="Internal server error while creating game")
        
        # Return game session with first question (no answer field)
        question_data = {
            'id': question.id,
            'question': question.question,
            'category': question.category,
            'difficulty': question.difficulty,
            'rating': question.rating
        }
        
        return jsonify({
            'game_session_id': game_session.id,
            'current_question_number': 1,
            'current_score': {
                'correct': 0,
                'total_answered': 0,
                'total_questions': number_of_questions
            },
            'question': question_data,
            'success': True
        }), 201
    except ValueError:
        abort(400, description="Invalid request parameters")
    except Exception as e:
        # Re-raise HTTPException for 4xx errors, otherwise 500
        if hasattr(e, 'code') and 400 <= e.code < 500:
            raise
        abort(500, description="Internal server error while processing game creation")


@games_bp.route('/games/<int:game_session_id>/<int:question_number>', methods=['POST'])
@rate_limit(limit=30, window_seconds=60)
def answer_question(game_session_id, question_number):
    """
    Answer a game question and get the next question
    
    Enforces sequence - only accepts answers for the next expected question.
    Uses deterministic stored question snapshots, not random question fetching.
    Rejects duplicate answers with 422. Rejects out-of-order with 422.
    
    Request body: {
        "user_answer": string
    }
    
    Returns: {game_session_id, answered_question_number, correct, correct_answer,
              current_score, current_question_number, question, status, success}
    Errors: 400 (missing fields), 404 (game not found), 422 (out-of-order/duplicate answer/out of range)
    """
    try:
        body = _get_request_json()
        
        # Validate body and user_answer
        if not body or 'user_answer' not in body:
            abort(400, description="Request body must contain 'user_answer' field")
        
        user_answer = body.get('user_answer')
        
        if not isinstance(user_answer, str) or not user_answer.strip():
            abort(400, description="user_answer must be a non-empty string")
        
        # Get game session
        game_session = db.session.query(GameSession).get(game_session_id)
        if not game_session:
            abort(404)
        
        # Validate question_number is in range [1..N]
        if question_number < 1 or question_number > game_session.number_of_questions:
            abort(422, description=f"question_number must be between 1 and {game_session.number_of_questions}")
        
        # SEQUENCE VALIDATION: Enforce that this is the next expected question
        next_expected = GameSessionAnswerService.get_next_question_number(
            game_session_id,
            game_session.number_of_questions
        )
        
        if next_expected is None:
            # All questions already answered - reject
            abort(422, description="All questions for this game have already been answered")
        
        if question_number != next_expected:
            # Out-of-order answer - reject with 422
            abort(422, description=f"Expected answer for question {next_expected}, but received answer for question {question_number}")
        
        # Get the existing answer record (should exist and have empty user_answer)
        existing_answer = GameSessionAnswerRepository.get_by_game_and_question(game_session_id, question_number)
        
        if not existing_answer:
            # Record should exist (question was pre-served at game creation)
            # If missing, this indicates legacy/corrupt session data inconsistency
            # Return 409 Conflict to indicate state machine violation
            abort(409, description=f'Session conflict: Expected answer record for question {question_number} not found in audit trail. This may indicate a corrupted or legacy session.')
        
        # Verify it's not already answered
        if existing_answer.user_answer and existing_answer.user_answer.strip():
            # Already answered - reject as duplicate
            abort(422, description=f"Question {question_number} has already been answered")
        
        # Get the question object for this answer record
        from models import Question
        question_obj = db.session.query(Question).get(existing_answer.question_id)
        if not question_obj:
            abort(404, description=f"Question with id {existing_answer.question_id} not found")
        
        # Update the existing record with the user's answer
        try:
            GameSessionAnswerService.record_answer(
                game_session_id=game_session_id,
                question_number=question_number,
                question=question_obj,
                user_answer=user_answer.strip()
            )
            db.session.commit()
        except ValueError as e:
            db.session.rollback()
            abort(400, description=str(e))
        except Exception as e:
            db.session.rollback()
            abort(500, description="Internal server error while recording answer")
        
        # Get the updated answer record
        answer_record = GameSessionAnswerRepository.get_by_game_and_question(game_session_id, question_number)
        is_correct = answer_record.is_correct
        correct_answer = answer_record.answer_snapshot
        
        # Compute current game state
        game_state = GameSessionAnswerService.get_game_state_summary(game_session_id)
        correct_count = game_state['correct']
        total_answered = game_state['total_answered']
        total_questions = game_state['total_questions']
        
        # Check if game is complete
        is_complete = GameSessionAnswerService.is_game_complete(game_session_id, total_questions)
        
        response = {
            'game_session_id': game_session_id,
            'answered_question_number': question_number,
            'correct': is_correct,
            'correct_answer': correct_answer,
            'current_score': {
                'correct': correct_count,
                'total_answered': total_answered,
                'total_questions': total_questions
            },
            'success': True
        }
        
        if is_complete:
            # Game is complete - update user stats idempotently
            response['status'] = 'completed'
            response['current_question_number'] = None
            response['question'] = None
            
            # Atomically mark completion and only award score once per game session
            try:
                rows_affected = GameSessionRepository.atomic_mark_completed(
                    game_session_id, 
                    correct_count
                )
                
                # If rows_affected == 1, this request won the race and should update user stats
                # If rows_affected == 0, another request already marked it completed (idempotent success)
                if rows_affected == 1:
                    # Refresh game session to get updated is_completed flag
                    game_session = GameSessionRepository.get_by_id(game_session_id)
                    # Update user stats
                    game_session.user.total_score += correct_count
                    game_session.user.games_played += 1
                    db.session.commit()
                # else: already completed by another request, don't update stats again
            except Exception as e:
                db.session.rollback()
                abort(500)
        else:
            # Get next question number
            next_question_number = GameSessionAnswerService.get_next_question_number(
                game_session_id, 
                total_questions
            )
            
            if next_question_number:
                # Build exclude_ids from persisted answers to prevent duplicates
                persisted_answers = GameSessionAnswerRepository.get_by_game(game_session_id)
                exclude_ids = [ans.question_id for ans in persisted_answers if ans.question_id]
                
                # Check if next question is already recorded
                next_answer_record = GameSessionAnswerRepository.get_by_game_and_question(
                    game_session_id, 
                    next_question_number
                )
                
                if next_answer_record:
                    # Already recorded, fetch the question
                    next_question = db.session.query(Question).get(next_answer_record.question_id)
                else:
                    # Create the next question record with exclusion list
                    if game_session.category_id:
                        next_question = QuestionService.get_random_question_by_category(
                            game_session.category_id,
                            exclude_ids=exclude_ids
                        )
                    else:
                        next_question = QuestionService.get_random_question(exclude_ids=exclude_ids)
                    
                    if next_question:
                        # Record this question in audit trail with empty user_answer
                        # Treat persistence failure as hard error - don't return question if we can't persist it
                        try:
                            GameSessionAnswerService.record_answer(
                                game_session_id=game_session_id,
                                question_number=next_question_number,
                                question=next_question,
                                user_answer=''
                            )
                            db.session.commit()
                        except Exception as e:
                            # Next-question persistence failure is a hard failure
                            db.session.rollback()
                            abort(500, description="Internal server error while preparing next question")
                
                # Only set current_question_number if we successfully have a question
                # This prevents partial-success responses with null question
                if next_question:
                    response['current_question_number'] = next_question_number
                    response['question'] = {
                        'id': next_question.id,
                        'question': next_question.question,
                        'category': next_question.category,
                        'difficulty': next_question.difficulty,
                        'rating': next_question.rating
                    }
                else:
                    # Cannot select next question - this should not happen in normal flow
                    # but if it does, treat as error condition
                    db.session.rollback()
                    abort(500, description="Unable to select next question. Database may be empty or no questions available.")
            else:
                response['current_question_number'] = None
                response['question'] = None
        
        return jsonify(response), 200
    except Exception as e:
        if hasattr(e, 'code') and 400 <= e.code < 500:
            raise
        abort(500, description="Internal server error while processing answer")


@games_bp.route('/games/<int:game_session_id>', methods=['GET'])
def get_game_state(game_session_id):
    """
    Get current game state and next unanswered question (resume/catch-up endpoint)
    
    Uses persisted GameSessionAnswer records to determine actual state,
    not calculated assumptions.
    
    Returns: {game_session_id, current_question_number, current_score, question, status, success}
    Errors: 404 (game session not found)
    """
    try:
        # Get game session
        game_session = db.session.query(GameSession).get(game_session_id)
        if not game_session:
            abort(404)
        
        # Use GameSessionAnswerService to find next unanswered question
        next_question_number = GameSessionAnswerService.get_next_question_number(
            game_session_id,
            game_session.number_of_questions
        )
        
        # Get game state summary
        game_state = GameSessionAnswerService.get_game_state_summary(game_session_id)
        
        # Check if game is complete
        if next_question_number is None:
            # All questions answered
            return jsonify({
                'game_session_id': game_session_id,
                'status': 'completed',
                'current_score': {
                    'correct': game_state['correct'],
                    'total_answered': game_state['total_answered'],
                    'total_questions': game_state['total_questions']
                },
                'message': 'Game completed',
                'success': True
            }), 200
        
        # Get the stored question snapshot for next question
        stored_answers = GameSessionAnswerService.get_game_answers(game_session_id)
        next_answer_record = None
        for ans in stored_answers:
            if ans.question_number == next_question_number:
                next_answer_record = ans
                break
        
        if not next_answer_record:
            abort(404, description=f"Question record for game {game_session_id} question {next_question_number} not found")
        
        # Fetch the actual Question object
        from models import Question
        question = db.session.query(Question).get(next_answer_record.question_id)
        if not question:
            abort(404, description=f"Question with id {next_answer_record.question_id} not found")
        
        question_data = {
            'id': question.id,
            'question': question.question,
            'category': question.category,
            'difficulty': question.difficulty,
            'rating': question.rating
        }
        
        return jsonify({
            'game_session_id': game_session_id,
            'current_question_number': next_question_number,
            'current_score': {
                'correct': game_state['correct'],
                'total_answered': game_state['total_answered'],
                'total_questions': game_state['total_questions']
            },
            'question': question_data,
            'success': True
        }), 200
    except Exception as e:
        if hasattr(e, 'code') and 400 <= e.code < 500:
            raise
        abort(500, description="Internal server error while retrieving game state")
