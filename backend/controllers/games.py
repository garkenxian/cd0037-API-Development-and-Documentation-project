"""Games API Blueprint - Handles game session-related routes"""

from flask import Blueprint, request, abort, jsonify
from services import GameSessionService

games_bp = Blueprint('games', __name__, url_prefix='/games')


# TODO: Implement game endpoints following persistent session architecture
# - POST /games - Create game session, return first question
# - GET /games/<id> - Get current game state (catch-up endpoint)
# - POST /games/<id>/<question_number> - Answer question, return next

@games_bp.route('', methods=['POST'])
def create_game():
    """
    Create a new game session
    
    Request body: {
        "user_id": int,
        "category_id": int,
        "number_of_questions": int (optional, default 5)
    }
    Returns: game session with first question
    Errors: 400 (bad request), 404 (not found), 422 (invalid)
    """
    # TODO: Implementation pending
    abort(501)  # Not Implemented


@games_bp.route('/<int:game_session_id>', methods=['GET'])
def get_game(game_session_id):
    """
    Get current game session state and next unanswered question
    
    Returns: game session state with next question or completion status
    Errors: 404 (game session not found)
    """
    # TODO: Implementation pending
    abort(501)  # Not Implemented


@games_bp.route('/<int:game_session_id>/<int:question_number>', methods=['POST'])
def answer_question(game_session_id, question_number):
    """
    Answer a question in an active game session
    
    Request body: {"user_answer": string}
    Returns: answer feedback and next question or completion status
    Errors: 400 (bad request), 404 (not found)
    """
    # TODO: Implementation pending
    abort(501)  # Not Implemented
