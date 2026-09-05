"""GameSession repository - read/write operations only"""

from models import db, GameSession
from sqlalchemy import func


class GameSessionRepository:
    """Repository for GameSession model"""

    @staticmethod
    def create(user_id, score, category_id=None, number_of_questions=5):
        """Create a new game session (no commit)"""
        session = GameSession(
            user_id=user_id,
            score=score,
            category_id=category_id,
            number_of_questions=number_of_questions
        )
        db.session.add(session)
        return session

    @staticmethod
    def get_by_id(session_id):
        """Get game session by ID"""
        return db.session.get(GameSession, session_id)

    @staticmethod
    def get_by_user(user_id, page=1, per_page=50):
        """Get all game sessions for a user"""
        return GameSession.query.filter_by(user_id=user_id).order_by(
            GameSession.date_played.desc()
        ).paginate(page=page, per_page=per_page)

    @staticmethod
    def get_all(page=1, per_page=50):
        """Get all game sessions"""
        return GameSession.query.order_by(
            GameSession.date_played.desc()
        ).paginate(page=page, per_page=per_page)

    @staticmethod
    def get_by_category(category_id, page=1, per_page=50):
        """Get game sessions for a category"""
        return GameSession.query.filter_by(category_id=category_id).order_by(
            GameSession.date_played.desc()
        ).paginate(page=page, per_page=per_page)

    @staticmethod
    def update(game_session, **kwargs):
        """Update game session attributes (no commit)"""
        for key, value in kwargs.items():
            if hasattr(game_session, key):
                setattr(game_session, key, value)
        return game_session

    @staticmethod
    def delete(game_session):
        """Delete game session from database (no commit)"""
        db.session.delete(game_session)

    @staticmethod
    def get_user_stats(user_id):
        """
        Get statistics for a user using SQL aggregation
        Single query instead of fetching all sessions and computing in Python
        """
        result = db.session.query(
            func.count(GameSession.id).label('total_games'),
            func.sum(GameSession.score).label('total_score'),
            func.avg(GameSession.score).label('average_score')
        ).filter(GameSession.user_id == user_id).first()
        
        return {
            'total_games': result.total_games or 0,
            'total_score': result.total_score or 0,
            'average_score': float(result.average_score or 0)
        }

    @staticmethod
    def get_leaderboard(limit=10):
        """Get top users by total score"""
        from models import User
        
        results = db.session.query(
            User.id,
            User.username,
            func.sum(GameSession.score).label('total_score'),
            func.count(GameSession.id).label('games_played')
        ).join(GameSession).group_by(User.id).order_by(
            func.sum(GameSession.score).desc()
        ).limit(limit).all()
        
        return results

    @staticmethod
    def get_by_user_with_details(user_id, page=1, per_page=50):
        """
        Get user's game sessions WITH User and Category details
        Uses JOINs to avoid N+1 lazy loading problem
        
        Args:
            user_id: User ID to filter by
            page: Pagination page
            per_page: Results per page
            
        Returns:
            Paginated GameSession results with related data loaded
        """
        from models import User, Category
        
        return GameSession.query.join(User).outerjoin(Category).filter(
            GameSession.user_id == user_id
        ).order_by(GameSession.date_played.desc()).paginate(
            page=page, per_page=per_page
        )
