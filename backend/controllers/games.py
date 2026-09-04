"""Games API Blueprint - Handles game session-related routes"""

from flask import Blueprint, request, abort, jsonify
from services import GameSessionService, UserService, CategoryService, QuestionService

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
        
        # Validate category exists (if provided)
        if category_id is not None:
            CategoryService.get_category(category_id)
        
        # Validate number_of_questions
        if not isinstance(number_of_questions, int) or number_of_questions < 1 or number_of_questions > 20:
            raise ValueError("number_of_questions must be between 1 and 20")
        
        # Create game session with initial score 0
        game_session = GameSessionService.create_game_session(
            user_id=user_id,
            score=0,
            category_id=category_id
        )
        
        # Get first question - use random selection for variety
        if category_id is not None:
            # Get random question from category
            first_question = QuestionService.get_random_question_by_category(category_id)
        else:
            # Get random question from any category
            # For simplicity, get first available question (in production, would be random)
            questions = QuestionService.get_all_questions()
            if not questions:
                raise ValueError("No questions available")
            first_question = questions[0]
        
        if not first_question:
            raise ValueError("No questions available for this category")
        
        return jsonify({
            'game_session_id': game_session.id,
            'question_number': 1,
            'current_score': {
                'correct': 0,
                'total_answered': 0,
                'total_questions': number_of_questions
            },
            'question': first_question.format(),
            'success': True
        }), 201
    except ValueError as e:
        error_msg = str(e).lower()
        if 'not found' in error_msg or 'not available' in error_msg:
            abort(404)
        else:
            abort(422)
    except Exception as e:
        abort(500)


@games_bp.route('/<int:game_session_id>', methods=['GET'])
def get_game(game_session_id):
    """
    Get current game session state and next unanswered question
    
    Returns: game session state with next question or completion status
    Errors: 404 (game session not found)
    """
    try:
        game_session = GameSessionService.get_game_session(game_session_id)
        
        # For now, return basic game session info
        # In a full implementation, track which questions have been answered
        return jsonify({
            'game_session_id': game_session.id,
            'user_id': game_session.user_id,
            'category_id': game_session.category_id,
            'score': game_session.score,
            'date_played': game_session.date_played.isoformat() if game_session.date_played else None,
            'success': True
        }), 200
    except ValueError:
        abort(404)
    except Exception:
        abort(500)


@games_bp.route('/<int:game_session_id>/<int:question_number>', methods=['POST'])
def answer_question(game_session_id, question_number):
    """
    Answer a question in an active game session
    
    Request body: {"user_answer": string}
    Returns: answer feedback and next question or completion status
    Errors: 400 (bad request), 404 (not found)
    """
    body = request.get_json()

    if not body or 'user_answer' not in body:
        abort(400)
    
    user_answer = body.get('user_answer')

    try:
        game_session = GameSessionService.get_game_session(game_session_id)
        
        # For now, return a placeholder response
        # In a full implementation, validate the answer, update score, and return next question
        return jsonify({
            'game_session_id': game_session.id,
            'question_number': question_number,
            'correct': False,
            'correct_answer': 'Answer placeholder',
            'current_score': {
                'correct': game_session.score,
                'total_answered': question_number,
                'total_questions': 5
            },
            'success': True
        }), 200
    except ValueError:
        abort(404)
    except Exception:
        abort(500)
