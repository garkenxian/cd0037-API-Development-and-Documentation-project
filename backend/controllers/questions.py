"""Questions API Blueprint - Handles question-related routes"""

from flask import Blueprint, request, abort, jsonify
from services import QuestionService, CategoryService

questions_bp = Blueprint('questions', __name__, url_prefix='/questions')


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
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', None, type=str)
        
        if page < 1:
            abort(400)
        
        if search:
            # Search questions
            questions_page = QuestionService.search_questions(search, page=page)
        else:
            # Get all questions
            questions_page = QuestionService.get_all_questions(page=page)
        
        if page > questions_page.pages and questions_page.total > 0:
            abort(404)
        
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
    except ValueError:
        abort(400)
    except Exception as e:
        abort(500)


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
        abort(404)
    except Exception as e:
        abort(500)


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
        abort(404)
    except Exception as e:
        abort(500)
