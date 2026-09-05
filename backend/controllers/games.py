"""Games API Blueprint - Handles game session-related routes"""

from flask import Blueprint, request, abort, jsonify
from werkzeug.exceptions import HTTPException
from services import GameSessionService, UserService, CategoryService, QuestionService

# Phase 1b: Import GameSessionAnswerService for audit table integration
# This service ensures questions are tracked and validated deterministically
# TODO: Implement GameSessionAnswerService once Phase 1b model/repository are complete
try:
    from services.game_session_answer_service import GameSessionAnswerService
    PHASE_1B_AVAILABLE = True
except ImportError:
    PHASE_1B_AVAILABLE = False

games_bp = Blueprint('games', __name__, url_prefix='/games')


@games_bp.route('', methods=['POST'])
def create_game():
    """
    Create a new game session
    
    Request body: {
        "user_id": int,
        "category_id": int (optional, default all categories),
        "number_of_questions": int (optional, default 5)
    }
    Returns: game session with first question
    Errors: 400 (bad request), 404 (not found), 422 (invalid)
    """
    body = request.get_json()

    # Validate required fields
    if not body:
        abort(400)
    
    user_id = body.get('user_id')
    category_id = body.get('category_id')
    number_of_questions = body.get('number_of_questions', 5)

    if user_id is None:
        abort(400)

    try:
        # Validate user exists
        UserService.get_user(user_id)

        # Normalize category_id: 0 means "all categories" (store as NULL in DB)
        normalized_category_id = None if category_id in (None, 0) else category_id

        # Validate category exists (if provided)
        if normalized_category_id is not None:
            CategoryService.get_category(normalized_category_id)

        # Validate number_of_questions
        if not isinstance(number_of_questions, int) or number_of_questions < 1 or number_of_questions > 20:
            raise ValueError("number_of_questions must be between 1 and 20")

        # Create game session with initial score 0 and number of questions
        # Use normalized_category_id to persist NULL in DB (not 0)
        game_session = GameSessionService.create_game_session(
            user_id=user_id,
            score=0,
            category_id=normalized_category_id,
            number_of_questions=number_of_questions
        )

        # Get first question for the game
        if normalized_category_id is not None:
            # Get random question from category
            first_question = QuestionService.get_random_question_by_category(normalized_category_id)
        else:
            # Get first available question from all categories (deterministic: gets first from first page)
            # Note: In a production scenario with large datasets, consider implementing random selection
            questions_page = QuestionService.get_all_questions()
            if not questions_page.items:
                raise ValueError("No questions available")
            first_question = questions_page.items[0]
        
        if not first_question:
            raise ValueError("No questions available for this category")
        
        # Phase 1b: Store the initial question in game_session_answer audit table
        # This ensures question_number=1 is deterministically linked to this specific question
        # When answer_question() is called, it validates against this stored question
        if PHASE_1B_AVAILABLE:
            GameSessionAnswerService.store_initial_question(
                game_session_id=game_session.id,
                question_number=1,
                question=first_question
            )
        # Note: If Phase 1b not available, answer_question endpoint returns 501 (Not Implemented)
        # to prevent nondeterministic scoring bugs. The endpoint is gated until Phase 1b is ready.
        
        return jsonify({
            'game_session_id': game_session.id,
            'question_number': 1,
            'current_score': {
                'correct': 0,
                'total_answered': 0,
                'total_questions': number_of_questions
            },
            'question': {
                'id': first_question.id,
                'question': first_question.question,
                'category': first_question.category,
                'difficulty': first_question.difficulty,
                'rating': first_question.rating
            },
            'success': True
        }), 201
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg:
            # Resource (user/category) not found
            abort(404)
        elif 'not available' in error_msg:
            # No questions available - valid request but can't be fulfilled (422)
            abort(422)
        else:
            # Other validation errors
            abort(422)
    except Exception as e:
        abort(500)


@games_bp.route('/<int:game_session_id>', methods=['GET'])
def get_game(game_session_id):
    """
    Get current game session state and next unanswered question (Catch-Up Endpoint)
    
    Returns:
    - In-progress: {game_session_id, question_number, current_score, question, success: true}
    - Completed: {game_session_id, status: "completed", current_score, success: true}
    
    Errors: 404 (game session not found)
    """
    try:
        game_session = GameSessionService.get_game_session(game_session_id)
        
        # Phase 1b: Query game_session_answer audit table to find next unanswered question
        if PHASE_1B_AVAILABLE:
            # Get the next unanswered question number
            next_question_number = GameSessionAnswerService.get_next_question_number(game_session_id)
            
            # Retrieve the next question that was prepared for this game
            next_answer_record = GameSessionAnswerService.get_by_game_and_question_number(
                game_session_id=game_session_id,
                question_number=next_question_number
            )
            
            if next_answer_record:
                # Game is in-progress, return next question
                return jsonify({
                    'game_session_id': game_session.id,
                    'question_number': next_question_number,
                    'current_score': {
                        'correct': GameSessionAnswerService.get_correct_count(game_session_id),
                        'total_answered': next_question_number - 1,
                        'total_questions': GameSessionAnswerService.get_total_questions(game_session_id)
                    },
                    'question': next_answer_record.get_question_format(),
                    'success': True
                }), 200
            else:
                # All questions answered, game completed
                # Calculate total_answered from next_question_number (which is now beyond the last question)
                total_answered = next_question_number - 1
                return jsonify({
                    'game_session_id': game_session.id,
                    'status': 'completed',
                    'current_score': {
                        'correct': GameSessionAnswerService.get_correct_count(game_session_id),
                        'total_answered': total_answered,
                        'total_questions': GameSessionAnswerService.get_total_questions(game_session_id)
                    },
                    'success': True
                }), 200
        else:
            # Phase 1b not available - return basic info only (temporary fallback)
            return jsonify({
                'game_session_id': game_session.id,
                'user_id': game_session.user_id,
                'category_id': game_session.category_id,
                'score': game_session.score,
                'date_played': game_session.date_played.isoformat() if game_session.date_played else None,
                'success': True,
                'note': 'Full game state requires Phase 1b implementation'
            }), 200
    except ValueError:
        abort(404)
    except Exception:
        abort(500)


@games_bp.route('/<int:game_session_id>/<int:question_number>', methods=['POST'])
def answer_question(game_session_id, question_number):
    """
    Answer a question in an active game session
    
    CRITICAL: This endpoint requires Phase 1b (game_session_answer audit table) to work correctly.
    If Phase 1b is unavailable, this endpoint returns 501 (Not Implemented) to avoid nondeterministic scoring.
    
    Request body: {"user_answer": string}
    Returns: answer feedback with score update
    Errors: 400 (bad request), 404 (not found), 501 (Phase 1b not implemented), 422 (duplicate/out-of-sequence)
    """
    body = request.get_json()

    if not body or 'user_answer' not in body:
        abort(400)
    
    user_answer = body.get('user_answer')
    
    # Validate user_answer is a non-empty string (prevent AttributeError on .lower()/.strip())
    if not isinstance(user_answer, str) or not user_answer.strip():
        abort(400)  # Bad request: user_answer must be non-empty string
    
    try:
        # Validate game session exists (this check is independent of Phase 1b)
        game_session = GameSessionService.get_game_session(game_session_id)
        
        # Phase 1b GATE: Block this endpoint if Phase 1b is not available
        # Prevents nondeterministic scoring bug
        if not PHASE_1B_AVAILABLE:
            abort(501)  # Not Implemented - waiting for Phase 1b
        
        # Phase 1b INTEGRATION: Retrieve the ORIGINAL question that was served for this question_number
        # This ensures answers are validated against the same question the user saw
        answer_record = GameSessionAnswerService.get_by_game_and_question_number(
            game_session_id=game_session_id,
            question_number=question_number
        )
        
        if not answer_record:
            # Invalid question_number for this session (not served / out of sequence)
            abort(422)  # Unprocessable: question_number invalid for this game session
        
        # Check if already answered (prevent duplicates)
        if answer_record.is_already_answered():
            abort(422)  # Unprocessable: question already answered in this session
        
        # Validate against the STORED question, not a random one
        # This ensures deterministic, repeatable scoring
        correct_answer = answer_record.correct_answer.lower().strip()
        user_ans = user_answer.lower().strip()
        is_correct = user_ans == correct_answer
        
        # Record the answer in the audit table (Phase 1b)
        answer_record.record_user_answer(
            user_answer=user_answer,
            is_correct=is_correct
        )
        
        # Update game session score if correct (transaction managed by service layer)
        if is_correct:
            game_session = GameSessionService.update_game_session(
                game_session_id, score=game_session.score + 10
            )
        
        # Determine next question
        next_question_number = question_number + 1
        next_answer_record = GameSessionAnswerService.get_by_game_and_question_number(
            game_session_id=game_session_id,
            question_number=next_question_number
        )
        
        # Build response with answered_question_number and next_question_number for clarity
        response = {
            'game_session_id': game_session.id,
            'answered_question_number': question_number,
            'correct': is_correct,
            'correct_answer': answer_record.correct_answer,
            'current_score': {
                'correct': GameSessionAnswerService.get_correct_count(game_session_id),
                'total_answered': question_number,
                'total_questions': GameSessionAnswerService.get_total_questions(game_session_id)
            },
            'success': True
        }
        
        # Add next question info if available
        if next_answer_record:
            response['next_question_number'] = next_question_number
            response['question'] = next_answer_record.get_question_format()
        else:
            # Game is complete
            response['status'] = 'completed'
            response['next_question_number'] = None
            response['question'] = None
        
        return jsonify(response), 200
    except HTTPException:
        # Re-raise HTTPException (from abort()) so it propagates correctly
        raise
    except ValueError:
        abort(404)
    except Exception:
        abort(500)
