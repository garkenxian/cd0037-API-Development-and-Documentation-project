"""Games API Blueprint - Handles game session and question answering routes"""

import re
from datetime import datetime
from flask import Blueprint, request, abort, jsonify
from services import QuestionService, CategoryService, UserService, GameSessionService
from data_access import db
from models import GameSession

games_bp = Blueprint('games', __name__, url_prefix='')


@games_bp.route('/games', methods=['POST'])
def create_game():
    """
    Create a new game session and return the first question
    
    Request body: {
        "user_id": int,
        "category_id": int (0 for all categories),
        "number_of_questions": int (optional, default=5)
    }
    
    Returns: {game_session_id, question_number, current_score, question, success}
    Errors: 400 (missing fields), 404 (user/category not found), 422 (invalid data)
    """
    try:
        body = request.get_json()
        
        # Validate body exists
        if not body:
            abort(400)
        
        user_id = body.get('user_id')
        category_id = body.get('category_id')
        number_of_questions = body.get('number_of_questions', 5)
        
        # Validate required fields
        if user_id is None or category_id is None:
            abort(400)
        
        # Validate user exists
        try:
            user = UserService.get_user(user_id)
        except ValueError:
            abort(404)
        
        # Validate category exists (if not 0 for all)
        if category_id != 0:
            try:
                CategoryService.get_category(category_id)
            except ValueError:
                abort(404)
        
        # Validate number_of_questions
        if not isinstance(number_of_questions, int) or number_of_questions < 1 or number_of_questions > 20:
            abort(422)
        
        # Get first question
        if category_id == 0:
            question = QuestionService.get_random_question(exclude_ids=[])
        else:
            question = QuestionService.get_random_question_by_category(category_id, exclude_ids=[])
        
        # Create game session
        game_session = GameSessionService.create_game_session(
            user_id=user_id,
            score=0,
            category_id=category_id if category_id != 0 else None,
            number_of_questions=number_of_questions
        )
        
        # Return game session with first question (no answer field)
        question_data = None
        if question:
            question_data = {
                'id': question.id,
                'question': question.question,
                'category': question.category,
                'difficulty': question.difficulty,
                'rating': question.rating
            }
        
        return jsonify({
            'game_session_id': game_session.id,
            'question_number': 1,
            'current_score': {
                'correct': 0,
                'total_answered': 0,
                'total_questions': number_of_questions
            },
            'question': question_data,
            'success': True
        }), 201
    except ValueError:
        abort(400)
    except Exception as e:
        # Re-raise HTTPException for 4xx errors, otherwise 500
        if hasattr(e, 'code') and 400 <= e.code < 500:
            raise
        abort(500)


@games_bp.route('/games/<int:game_session_id>/<int:question_number>', methods=['POST'])
def answer_question(game_session_id, question_number):
    """
    Answer a game question and get the next question
    
    Request body: {
        "user_answer": string
    }
    
    Returns: {game_session_id, answered_question_number, correct, correct_answer,
              current_score, next_question_number, question, status, success}
    Errors: 400 (missing fields), 404 (game/question not found)
    """
    try:
        body = request.get_json()
        
        # Validate body and user_answer
        if not body or 'user_answer' not in body:
            abort(400)
        
        user_answer = body.get('user_answer')
        
        if not isinstance(user_answer, str) or not user_answer.strip():
            abort(400)
        
        # Get game session
        try:
            game_session = db.session.query(GameSession).get(game_session_id)
            if not game_session:
                abort(404)
        except Exception:
            abort(404)
        
        # Get the question for this game session
        # For now, we'll get a question by index in the category
        if question_number < 1 or question_number > game_session.number_of_questions:
            abort(400)
        
        # Get question from service (use exclude_ids to get different question each time)
        # In a real implementation, you'd store question IDs in the game_session
        if game_session.category_id:
            question = QuestionService.get_random_question_by_category(
                game_session.category_id,
                exclude_ids=[]
            )
        else:
            question = QuestionService.get_random_question(exclude_ids=[])
        
        if not question:
            abort(404)
        
        # Normalize and compare answers
        def normalize_answer(text):
            text = text.lower()
            text = re.sub(r'[^a-z0-9\s]', '', text)
            text = ' '.join(text.split())
            return text
        
        correct_answer_normalized = normalize_answer(question.answer)
        user_answer_normalized = normalize_answer(user_answer)
        
        is_correct = (
            user_answer_normalized == correct_answer_normalized or
            all(word in user_answer_normalized for word in correct_answer_normalized.split())
        )
        
        # Update game session score
        if is_correct:
            game_session.score += 1
        
        # Check if game is complete
        is_complete = question_number >= game_session.number_of_questions
        
        db.session.commit()
        
        response = {
            'game_session_id': game_session_id,
            'answered_question_number': question_number,
            'correct': is_correct,
            'correct_answer': question.answer,
            'current_score': {
                'correct': game_session.score,
                'total_answered': question_number,
                'total_questions': game_session.number_of_questions
            },
            'success': True
        }
        
        if is_complete:
            response['status'] = 'completed'
            response['next_question_number'] = None
            response['question'] = None
        else:
            # Get next question
            next_question = QuestionService.get_random_question_by_category(
                game_session.category_id,
                exclude_ids=[]
            ) if game_session.category_id else QuestionService.get_random_question(exclude_ids=[])
            
            response['next_question_number'] = question_number + 1
            if next_question:
                response['question'] = {
                    'id': next_question.id,
                    'question': next_question.question,
                    'category': next_question.category,
                    'difficulty': next_question.difficulty,
                    'rating': next_question.rating
                }
            else:
                response['question'] = None
        
        return jsonify(response), 200
    except Exception as e:
        if hasattr(e, 'code') and 400 <= e.code < 500:
            raise
        abort(500)


@games_bp.route('/games/<int:game_session_id>', methods=['GET'])
def get_game_state(game_session_id):
    """
    Get current game state and next unanswered question
    
    Returns: {game_session_id, question_number, current_score, question, status, success}
    Errors: 404 (game session not found)
    """
    try:
        # Get game session
        try:
            game_session = db.session.query(GameSession).get(game_session_id)
            if not game_session:
                abort(404)
        except Exception:
            abort(404)
        
        # For simplicity, return current state
        # In a real implementation, you'd track which questions have been asked
        question_number = game_session.score + 1  # Next unanswered question
        
        # Check if complete
        if question_number > game_session.number_of_questions:
            return jsonify({
                'game_session_id': game_session_id,
                'status': 'completed',
                'current_score': {
                    'correct': game_session.score,
                    'total_answered': game_session.number_of_questions,
                    'total_questions': game_session.number_of_questions
                },
                'message': 'Game completed',
                'success': True
            }), 200
        
        # Get next question
        if game_session.category_id:
            question = QuestionService.get_random_question_by_category(
                game_session.category_id,
                exclude_ids=[]
            )
        else:
            question = QuestionService.get_random_question(exclude_ids=[])
        
        question_data = None
        if question:
            question_data = {
                'id': question.id,
                'question': question.question,
                'category': question.category,
                'difficulty': question.difficulty,
                'rating': question.rating
            }
        
        return jsonify({
            'game_session_id': game_session_id,
            'question_number': question_number,
            'current_score': {
                'correct': game_session.score,
                'total_answered': question_number - 1,
                'total_questions': game_session.number_of_questions
            },
            'question': question_data,
            'success': True
        }), 200
    except Exception as e:
        if hasattr(e, 'code') and 400 <= e.code < 500:
            raise
        abort(500)
