"""Categories API Blueprint - Handles category-related routes"""

from flask import Blueprint, request, abort, jsonify
from services import CategoryService, QuestionService

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')


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
        abort(500)


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
        abort(404)
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
        abort(400)
    
    category_type = body.get('type')

    if not category_type:
        abort(400)

    try:
        category = CategoryService.create_category(category_type)
        return jsonify(category.format()), 201
    except ValueError as e:
        error_msg = str(e).lower()
        # Distinguish between missing/invalid fields (400) and constraint violations (422)
        if 'already exists' in error_msg:
            # Conflict - duplicate category
            abort(422)
        else:
            # Bad request - invalid data
            abort(400)
    except Exception as e:
        # Database or other unexpected errors
        abort(500)


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
        abort(400)
    
    category_type = body.get('type')

    if not category_type:
        abort(400)

    try:
        category = CategoryService.get_category(category_id)
        # Update the category
        category.type = category_type
        from data_access import db
        db.session.commit()
        return jsonify(category.format()), 200
    except ValueError:
        abort(404)
    except Exception as e:
        error_msg = str(e).lower()
        if 'unique constraint' in error_msg or 'already exists' in error_msg:
            abort(422)
        abort(500)


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
            abort(422)
        
        from data_access import db
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'deleted': category_id,
            'success': True
        }), 200
    except ValueError:
        abort(404)
    except Exception as e:
        abort(500)
