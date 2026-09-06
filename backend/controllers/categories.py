"""Categories API Blueprint - Handles category-related routes"""

from flask import Blueprint, request, abort, jsonify
from services import CategoryService, QuestionService

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')


def _is_constraint_violation(error_text):
    """Return True when an error message indicates DB/domain constraint violation."""
    text = error_text.lower()
    return any(token in text for token in [
        'already exists',
        'unique constraint',
        'integrityerror',
        'constraint failed',
        'must be between'
    ])


@categories_bp.route('', methods=['GET'])
def get_categories():
    """
    Get all categories
    
    Returns: {categories: {id: type, ...}, success: true}
    """
    try:
        categories = CategoryService.get_all_categories_list()
        # Format as dictionary {id: type}
        categories_dict = {str(cat.id): cat.type for cat in categories}
        return jsonify({
            'categories': categories_dict,
            'success': True
        }), 200
    except Exception as e:
        abort(500, description="Internal server error while retrieving categories")


@categories_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """
    Get single category by ID
    
    Returns: {id, type, success: true}
    Errors: 404 (not found)
    """
    try:
        category = CategoryService.get_category(category_id)
        return jsonify(category.format()), 200
    except ValueError:
        abort(404, description=f"Category with id {category_id} not found")
    except Exception as e:
        abort(500)


@categories_bp.route('', methods=['POST'])
def create_category():
    """
    Create a new category
    
    Request body: {"type": string}
    Returns: category object with 201 status
    Errors: 400 (bad request), 422 (duplicate/constraint violation)
    """
    body = request.get_json()

    # Validate required fields
    if not body:
        abort(400, description="Request body must be JSON")
    
    category_type = body.get('type')

    if not category_type:
        abort(400, description="Missing required field: 'type'")

    try:
        category = CategoryService.create_category(category_type)
        return jsonify(category.format()), 201
    except ValueError as e:
        error_msg = str(e).lower()
        # Distinguish between missing/invalid fields (400) and constraint violations (422)
        if _is_constraint_violation(error_msg):
            if 'already exists' in error_msg:
                abort(422, description=f"Category type '{category_type}' already exists")
            abort(422, description=str(e))
        else:
            # Bad request - invalid data
            abort(400, description=str(e))
    except Exception as e:
        if _is_constraint_violation(str(e)):
            abort(422, description="Category data violates validation constraints")
        abort(500, description="Internal server error while creating category")


@categories_bp.route('/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """
    Update a category
    
    Request body: {"type": string}
    Returns: updated category object
    Errors: 404 (not found), 400 (bad request), 422 (duplicate)
    """
    body = request.get_json()

    if not body:
        abort(400, description="Request body must be JSON")
    
    category_type = body.get('type')

    if not category_type:
        abort(400, description="Missing required field: 'type'")

    try:
        category = CategoryService.get_category(category_id)
        # Update the category
        category.type = category_type
        from data_access import db
        db.session.commit()
        return jsonify(category.format()), 200
    except ValueError:
        abort(404, description=f"Category with id {category_id} not found")
    except Exception as e:
        error_msg = str(e).lower()
        if _is_constraint_violation(error_msg):
            if 'already exists' in error_msg or 'unique constraint' in error_msg:
                abort(422, description=f"Category type '{category_type}' already exists")
            abort(422, description="Category data violates validation constraints")
        abort(500, description="Internal server error while updating category")


@categories_bp.route('/<int:category_id>/questions', methods=['GET'])
def get_category_questions(category_id):
    """
    Get questions filtered by category (paginated)
    
    Query parameters:
    - page: int (default 1)
    
    Returns: {questions, total_questions, current_page, total_pages, current_category, success: true}
    Errors: 404 (category not found), 400 (invalid page parameter)
    """
    try:
        # Verify category exists
        category = CategoryService.get_category(category_id)
        
        try:
            page = request.args.get('page', 1, type=int)
        except (ValueError, TypeError):
            abort(400, description="Page parameter must be an integer")
        
        if page < 1:
            abort(400, description="Page number must be >= 1")
        
        # Get questions for this category
        questions_page = QuestionService.get_questions_by_category(category_id, page=page)
        
        # Check if page is out of range (200 if category exists but has no questions)
        if page > questions_page.pages and questions_page.total > 0:
            abort(404, description=f"Page {page} out of range. Total pages: {questions_page.pages}")
        
        return jsonify({
            'questions': [q.format() for q in questions_page.items],
            'total_questions': questions_page.total,
            'current_page': page,
            'total_pages': questions_page.pages,
            'current_category': category.type,
            'success': True
        }), 200
    except ValueError:
        abort(404, description=f"Category with id {category_id} not found")
    except Exception as e:
        if hasattr(e, 'code') and 400 <= e.code < 500:
            raise
        abort(500, description="Internal server error while retrieving category questions")


@categories_bp.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    """
    Delete a category (only if no associated questions)
    
    Returns: {deleted: id, success: true}
    Errors: 404 (not found), 422 (has questions)
    """
    try:
        category = CategoryService.get_category(category_id)
        
        # Check if category has any questions
        questions = QuestionService.get_questions_by_category(category_id)
        if questions.total > 0:
            # Category has questions, cannot delete
            abort(422, description=f"Cannot delete category with id {category_id}. It has {questions.total} associated question(s)")
        
        from data_access import db
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'deleted': category_id,
            'success': True
        }), 200
    except ValueError:
        abort(404, description=f"Category with id {category_id} not found")
    except Exception as e:
        if hasattr(e, 'code') and 400 <= e.code < 500:
            raise
        abort(500, description="Internal server error while deleting category")
