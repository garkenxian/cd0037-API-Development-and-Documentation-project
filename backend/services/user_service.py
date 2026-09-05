"""
User Service - Business logic for user operations
Handles validation, transaction boundaries, and coordination
"""

from data_access import db, UserRepository


class UserService:
    """Service layer for user operations"""

    @staticmethod
    def create_user(username, email):
        """
        Create a new user with validation
        
        Args:
            username: Unique username string
            email: User email address
            
        Returns:
            Created user object
            
        Raises:
            ValueError: If validation fails
        """
        # Validation
        if not username or len(username.strip()) == 0:
            raise ValueError("Username cannot be empty")
        
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        
        if not email or '@' not in email:
            raise ValueError("Invalid email address")
        
        # Check uniqueness
        if UserRepository.exists_by_username(username):
            raise ValueError(f"Username '{username}' already exists")
        
        if UserRepository.exists_by_email(email):
            raise ValueError(f"Email '{email}' already registered")
        
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
