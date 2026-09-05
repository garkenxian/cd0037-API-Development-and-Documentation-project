"""
Data Access Layer - Repository pattern
Queries and basic CRUD operations, NO transaction management
Transactions are managed by service layer
"""

from models import db, User


class UserRepository:
    """Repository for User model - read/write operations only"""

    @staticmethod
    def create(username, email=None):
        """
        Create a new user (no commit)
        
        Args:
            username: Unique username string
            email: User email address (optional)
            
        Returns:
            User object (not yet persisted)
        """
        user = User(username=username, email=email)
        db.session.add(user)
        return user

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        return db.session.get(User, user_id)

    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_all(page=1, per_page=50):
        """Get all users with pagination"""
        return User.query.paginate(page=page, per_page=per_page)

    @staticmethod
    def update(user, **kwargs):
        """
        Update user attributes (no commit)
        
        Args:
            user: User object
            **kwargs: Fields to update (total_score, games_played, etc.)
        """
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return user

    @staticmethod
    def delete(user):
        """Delete user from database (no commit)"""
        db.session.delete(user)

    @staticmethod
    def exists_by_username(username):
        """Check if username already exists"""
        return User.query.filter_by(username=username).first() is not None

    @staticmethod
    def exists_by_email(email):
        """Check if email already exists"""
        return User.query.filter_by(email=email).first() is not None
