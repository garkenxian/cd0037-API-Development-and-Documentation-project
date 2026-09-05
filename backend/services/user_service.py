"""
User Service - Business logic for user operations
Handles validation, transaction boundaries, and coordination
"""

from data_access import db, UserRepository
from models import User


class UserService:
    """Service layer for user operations"""

    @staticmethod
    def create_user(username, email=None):
        """
        Create a new user with validation
        
        Args:
            username: Unique username string
            email: User email address (optional)
            
        Returns:
            Created user object
            
        Raises:
            ValueError: If validation fails
        """
        # Validation
        if not username or len(username.strip()) == 0:
            raise ValueError("Username cannot be empty")
        
        # Check uniqueness
        if UserRepository.exists_by_username(username):
            raise ValueError(f"Username '{username}' already exists")
        
        # Create via repository (no commit yet)
        user = UserRepository.create(username, email)
        
        # Transaction boundary - commit here
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise  # Re-raise DB error so it surfaces as 500, not client error
        
        return user

    @staticmethod
    def get_user(user_id):
        """Get user by ID"""
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        return user

    @staticmethod
    def get_user_by_username(username):
        """Get user by username"""
        user = UserRepository.get_by_username(username)
        if not user:
            raise ValueError(f"User '{username}' not found")
        return user

    @staticmethod
    def get_all_users(page=1, per_page=50):
        """Get all users with pagination"""
        return UserRepository.get_all(page=page, per_page=per_page)

    @staticmethod
    def update_user_score(user_id, score_increment):
        """
        Update user's total score
        
        Args:
            user_id: User ID
            score_increment: Points to add to total score
        """
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        user.total_score += score_increment
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Failed to update user score: {str(e)}")
        
        return user

    @staticmethod
    def increment_games_played(user_id):
        """Increment games_played counter"""
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        user.games_played += 1
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Failed to update games played: {str(e)}")
        
        return user

    @staticmethod
    def delete_user(user_id):
        """Delete a user"""
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        UserRepository.delete(user)
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Failed to delete user: {str(e)}")

    @staticmethod
    def get_all_users(sort_by='created_at', order='asc'):
        """
        Get all users (non-paginated) with optional sorting
        
        Args:
            sort_by: Field to sort by ('created_at', 'total_score', 'games_played')
            order: Sort order ('asc', 'desc')
            
        Returns:
            List of all users
        """
        query = User.query
        
        if sort_by == 'created_at':
            query = query.order_by(User.created_at.desc() if order == 'desc' else User.created_at)
        elif sort_by == 'total_score':
            query = query.order_by(User.total_score.desc() if order == 'desc' else User.total_score)
        elif sort_by == 'games_played':
            query = query.order_by(User.games_played.desc() if order == 'desc' else User.games_played)
        
        return query.all()

    @staticmethod
    def get_leaderboard(limit=10, offset=0):
        """
        Get top users ranked by total_score (descending)
        
        Args:
            limit: Number of users to return
            offset: Pagination offset
            
        Returns:
            List of users sorted by total_score (highest first)
        """
        from models import User
        users = User.query.order_by(User.total_score.desc()).offset(offset).limit(limit).all()
        return users

    @staticmethod
    def get_total_users_count():
        """Get total number of users in database"""
        from models import User
        return User.query.count()

