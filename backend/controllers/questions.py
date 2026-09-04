"""Questions API Blueprint - Handles question-related routes"""

from flask import Blueprint, request, abort, jsonify
from services import QuestionService, CategoryService

questions_bp = Blueprint('questions', __name__, url_prefix='/questions')


@questions_bp.route('', methods=['POST'])
def create_question():
    """
    Create a new question
    
    Request body: {
        "question": string,
        "answer": string,
        "category": int (category ID),
        "difficulty": int (1-5),
        "rating": float (optional, default 0)
    }
    Returns: question object with 201 status
    Errors: 400 (bad request), 422 (constraint violation)
    """
    body = request.get_json()

    # Validate required fields
    if not body:
        abort(400)
    
    question_text = body.get('question')
    answer = body.get('answer')
    category = body.get('category')
    difficulty = body.get('difficulty')
    rating = body.get('rating', 0)

    if not question_text or not answer or category is None or difficulty is None:
        abort(400)

    try:
        # Validate category exists (prevents orphaned questions when FK constraints aren't enforced, e.g. SQLite)
        CategoryService.get_category(category)
        
        question = QuestionService.create_question(
            question_text=question_text,
            answer=answer,
            category=category,
            difficulty=difficulty,
            rating=rating
        )
        return jsonify(question.format()), 201
    except ValueError as e:
        error_msg = str(e).lower()
        # Distinguish between missing/invalid fields (400) and constraint violations (422)
        if 'already exists' in error_msg or 'foreign key' in error_msg or 'not found' in error_msg:
            # Conflict or referential integrity issue
            abort(422)
        else:
            # Bad request - invalid data
            abort(400)
    except Exception as e:
        # Database or other unexpected errors
        abort(500)
