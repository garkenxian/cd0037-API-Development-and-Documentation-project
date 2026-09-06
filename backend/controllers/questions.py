"""Questions API Blueprint - Handles question-related routes"""

from flask import Blueprint, request, abort, jsonify
from services import QuestionService, CategoryService

questions_bp = Blueprint('questions', __name__, url_prefix='/questions')


def _is_constraint_violation(error_text):
    """Return True when an error message indicates DB/domain constraint violation."""
    text = error_text.lower()
    return any(token in text for token in [
        'already exists',
        'foreign key',
        'not found',
        'unique constraint',
        'integrityerror',
        'constraint failed'
    ])


@questions_bp.route('', methods=['GET'])
def get_questions():
    """
    Get paginated questions with optional search filter
    
    Query parameters:
    - page: int (default 1)
    - search: string (optional, case-insensitive substring match)
    
    Returns: {questions, total_questions, current_page, total_pages, categories, success: true}
    Errors: 404 (page out of range), 400 (invalid page)
    """
    try:
        try:
            page = request.args.get('page', 1, type=int)
        except (ValueError, TypeError):
            abort(400, description="Page parameter must be an integer")
        
        search = request.args.get('search', None, type=str)
        
        if page < 1:
            abort(400, description="Page number must be >= 1")
        
        if search:
            # Search questions
            questions_page = QuestionService.search_questions(search, page=page)
        else:
            # Get all questions
            questions_page = QuestionService.get_all_questions(page=page)
        
        if page > questions_page.pages and questions_page.total > 0:
            abort(404, description=f"Page {page} out of range. Total pages: {questions_page.pages}")
        
        # Get all categories for response
        all_categories = CategoryService.get_all_categories_list()
        categories_dict = {str(cat.id): cat.type for cat in all_categories}
        
        return jsonify({
            'questions': [q.format() for q in questions_page.items],
            'total_questions': questions_page.total,
            'current_page': page,
            'total_pages': questions_page.pages,
            'categories': categories_dict,
            'success': True
        }), 200
    except Exception as e:
        if hasattr(e, 'code') and 400 <= e.code < 500:
            raise
        abort(500, description="Internal server error while retrieving questions")


@questions_bp.route('/<int:question_id>', methods=['GET'])
def get_question(question_id):
    """
    Get a single question by ID
    
    Returns: question object
    Errors: 404 (not found)
    """
    try:
        question = QuestionService.get_question(question_id)
        return jsonify(question.format()), 200
    except ValueError:
        abort(404, description=f"Question with id {question_id} not found")
    except Exception as e:
        abort(500, description="Internal server error while retrieving question")


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
        abort(400, description="Request body must be JSON")
    
    question_text = body.get('question')
    answer = body.get('answer')
    category = body.get('category')
    difficulty = body.get('difficulty')
    rating = body.get('rating', 0)

    if not question_text or not answer or category is None or difficulty is None:
        abort(400, description="Missing required fields: 'question', 'answer', 'category', 'difficulty'")

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
        if _is_constraint_violation(error_msg):
            # Conflict or referential integrity issue
            abort(422, description=str(e))
        else:
            # Bad request - invalid data
            abort(400, description=str(e))
    except Exception as e:
        if _is_constraint_violation(str(e)):
            abort(422, description="Question data violates validation constraints")
        abort(500, description="Internal server error while creating question")


@questions_bp.route('/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    """
    Delete a question by ID
    
    Returns: {deleted: id, success: true}
    Errors: 404 (not found)
    """
    try:
        question = QuestionService.get_question(question_id)
        from data_access import db
        db.session.delete(question)
        db.session.commit()
        
        return jsonify({
            'deleted': question_id,
            'success': True
        }), 200
    except ValueError:
        abort(404, description=f"Question with id {question_id} not found")
    except Exception as e:
        abort(500, description="Internal server error while deleting question")
