"""Users API Blueprint - Handles user-related routes"""

from flask import Blueprint, request, abort, jsonify
from services import UserService

users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('', methods=['POST'])
def create_user():
    """
    Create a new user
    
    Request body: {"username": string, "email": string}
    Returns: user object with 201 status
    Errors: 400 (bad request), 422 (duplicate/constraint violation)
    """
    body = request.get_json()

    # Validate required fields
    if not body:
        abort(400)
    
    username = body.get('username')
    email = body.get('email')

    if not username or not email:
        abort(400)

    try:
        user = UserService.create_user(username, email)
        return jsonify(user.format()), 201
    except ValueError as e:
        error_msg = str(e).lower()
        # Distinguish between missing/invalid fields (400) and constraint violations (422)
        if 'already exists' in error_msg or 'already registered' in error_msg:
            # Conflict - duplicate username or email
            abort(422)
        else:
            # Bad request - invalid data
            abort(400)
    except Exception as e:
        # Database or other unexpected errors
        abort(500)
