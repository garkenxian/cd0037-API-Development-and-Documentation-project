"""
GameSession Service - Business logic for game session operations
Handles validation, transaction boundaries, and coordination
"""

from data_access import db, GameSessionRepository


class GameSessionService:
    """Service layer for game session operations"""

    @staticmethod
    def create_game_session(user_id, score, category_id=None, number_of_questions=5):
        """
        Create a new game session
        
        Args:
            user_id: User ID (must exist)
            score: Score earned in game
            category_id: Optional category ID
            number_of_questions: Total questions in this game session (default 5, max 20)
            
        Returns:
            Created game session object
            
        Raises:
            ValueError: If validation fails
        """
        # Basic validation
        if not user_id:
            raise ValueError("User ID is required")
        
        if score is None or score < 0:
            raise ValueError("Score must be a non-negative number")
        
        if not isinstance(number_of_questions, int) or number_of_questions < 1 or number_of_questions > 20:
            raise ValueError("number_of_questions must be between 1 and 20")
        
        # Create via repository (no commit yet)
        session = GameSessionRepository.create(user_id, score, category_id, number_of_questions)
        
        # Transaction boundary - commit here
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Failed to create game session: {str(e)}")
        
        return session

    @staticmethod
    def get_game_session(session_id):
        """Get game session by ID"""
        session = GameSessionRepository.get_by_id(session_id)
        if not session:
            raise ValueError(f"Game session {session_id} not found")
        return session

    @staticmethod
    def get_user_sessions(user_id, page=1, per_page=50):
        """Get all game sessions for a user"""
        return GameSessionRepository.get_by_user(user_id, page=page, per_page=per_page)

    @staticmethod
    def get_user_sessions_with_details(user_id, page=1, per_page=50):
        """
        Get user's game sessions WITH User and Category details
        Optimized: Avoids N+1 lazy loading of related data
        
        Args:
            user_id: User ID to filter by
            page: Pagination page
            per_page: Results per page
            
        Returns:
            Paginated GameSession results with related data loaded
        """
        return GameSessionRepository.get_by_user_with_details(user_id, page=page, per_page=per_page)

    @staticmethod
    def get_all_sessions(page=1, per_page=50):
        """Get all game sessions"""
        return GameSessionRepository.get_all(page=page, per_page=per_page)

    @staticmethod
    def get_category_sessions(category_id, page=1, per_page=50):
        """Get game sessions for a category"""
        return GameSessionRepository.get_by_category(category_id, page=page, per_page=per_page)

    @staticmethod
    def get_user_stats(user_id):
        """
        Get statistics for a user
        Optimized: Uses SQL aggregation instead of Python computation
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with total_games, total_score, average_score
        """
        return GameSessionRepository.get_user_stats(user_id)

    @staticmethod
    def get_leaderboard(limit=10):
        """
        Get top users by total score
        
        Args:
            limit: Number of top users to return
            
        Returns:
            List of (user_id, username, total_score, games_played) tuples
        """
        return GameSessionRepository.get_leaderboard(limit=limit)

    @staticmethod
    def update_game_session(session_id, **kwargs):
        """Update game session fields"""
        session = GameSessionRepository.get_by_id(session_id)
        if not session:
            raise ValueError(f"Game session {session_id} not found")
        
        try:
            GameSessionRepository.update(session, **kwargs)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Failed to update game session: {str(e)}")
        
        return session

    @staticmethod
    def delete_game_session(session_id):
        """Delete a game session"""
        session = GameSessionRepository.get_by_id(session_id)
        if not session:
            raise ValueError(f"Game session {session_id} not found")
        
        try:
            GameSessionRepository.delete(session)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Failed to delete game session: {str(e)}")
