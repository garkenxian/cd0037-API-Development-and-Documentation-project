"""Categories API Blueprint - Handles category-related routes"""

from flask import Blueprint, request, abort, jsonify
from services import CategoryService

categories_bp = Blueprint('categories', __name__, url_prefix='/categories')


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
