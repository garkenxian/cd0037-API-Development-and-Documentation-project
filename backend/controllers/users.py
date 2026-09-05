"""Users API Blueprint - Handles user-related routes"""

from flask import Blueprint, request, abort, jsonify
from services import UserService

users_bp = Blueprint('users', __name__, url_prefix='/users')


@users_bp.route('', methods=['GET'])
def get_users():
    """
    List all users with statistics
    
    Query parameters:
    - sort: string (optional, default 'created_at') - Sort by 'created_at', 'total_score', or 'games_played'
    - order: string (optional, default 'asc') - Sort order 'asc' or 'desc'
    
    Returns: {users: [...], total_users: int, success: true}
    Errors: 400 (invalid parameters)
    """
    try:
        sort_by = request.args.get('sort', 'created_at', type=str)
        order = request.args.get('order', 'asc', type=str)
        
        # Validate sort and order parameters
        valid_sorts = {'created_at', 'total_score', 'games_played'}
        valid_orders = {'asc', 'desc'}
        
        if sort_by not in valid_sorts or order not in valid_orders:
            abort(400)
        
        users = UserService.get_all_users(sort_by=sort_by, order=order)
        
        return jsonify({
            'users': [u.format() for u in users],
            'total_users': len(users),
            'success': True
        }), 200
    except Exception as e:
        if hasattr(e, 'code') and 400 <= e.code < 500:
            raise
        abort(500)


@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get user details and game history
    
    Returns: {id, username, total_score, games_played, created_at, game_sessions: [...], success: true}
    Errors: 404 (user not found)
    """
    try:
        user = UserService.get_user(user_id)
        return jsonify({
            'id': user.id,
            'username': user.username,
            'total_score': user.total_score,
            'games_played': user.games_played,
            'created_at': user.created_at.isoformat() + 'Z' if user.created_at else None,
            'game_sessions': [gs.format() for gs in user.game_sessions] if user.game_sessions else [],
            'success': True
        }), 200
    except ValueError:
        abort(404)
    except Exception as e:
        if hasattr(e, 'code') and 400 <= e.code < 500:
            raise
        abort(500)


@users_bp.route('', methods=['POST'])
def create_user():
    """
    Create a new user
    
    Request body: {"username": string}
    Returns: user object with 201 status
    Errors: 400 (bad request), 422 (duplicate/constraint violation)
    """
    body = request.get_json()

    # Validate required fields
    if not body:
        abort(400)
    
    username = body.get('username')
    email = body.get('email')

    if not username:
        abort(400)

    try:
        user = UserService.create_user(username, email)
        return jsonify(user.format()), 201
    except ValueError as e:
        error_msg = str(e).lower()
        # Distinguish between missing/invalid fields (400) and constraint violations (422)
        if 'already exists' in error_msg or 'already registered' in error_msg:
            # Conflict - duplicate username
            abort(422)
        else:
            # Bad request - invalid data
            abort(400)
    except Exception as e:
        if hasattr(e, 'code') and 400 <= e.code < 500:
            raise
        # Database or other unexpected errors
        abort(500)


@users_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """
    Get top users ranked by total score
    
    Query parameters:
    - limit: int (optional, default 10) - Number of top users to return
    - offset: int (optional, default 0) - Pagination offset
    
    Returns: {leaderboard: [{rank, id, username, total_score, games_played}, ...], total_users: int, success: true}
    Errors: 400 (invalid parameters)
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        if limit < 1 or offset < 0:
            abort(400)
        
        users = UserService.get_leaderboard(limit=limit, offset=offset)
        
        # Add rank to each user
        leaderboard = []
        for idx, user in enumerate(users, start=offset + 1):
            leaderboard.append({
                'rank': idx,
                'id': user.id,
                'username': user.username,
                'total_score': user.total_score,
                'games_played': user.games_played
            })
        
        # Get total users count
        total_users = UserService.get_total_users_count()
        
        return jsonify({
            'leaderboard': leaderboard,
            'total_users': total_users,
            'success': True
        }), 200
    except ValueError:
        abort(400)
    except Exception as e:
        if hasattr(e, 'code') and 400 <= e.code < 500:
            raise
        abort(500)
