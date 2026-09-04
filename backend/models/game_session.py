"""GameSession model - Pure ORM definition"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from . import db


class GameSession(db.Model):
    """
    GameSession model for tracking individual quiz game results
    Use GameSessionRepository and GameSessionService for persistence operations.
    """
    __tablename__ = 'game_sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    score = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    number_of_questions = Column(Integer, nullable=False, default=5)
    date_played = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def __init__(self, user_id, score, category_id=None, number_of_questions=5):
        self.user_id = user_id
        self.score = score
        self.category_id = category_id
        self.number_of_questions = number_of_questions

    def insert(self):
        """DEPRECATED: Use GameSessionRepository.create() instead"""
        db.session.add(self)
        db.session.commit()

    def update(self):
        """DEPRECATED: Use GameSessionRepository.update() instead"""
        db.session.commit()

    def delete(self):
        """DEPRECATED: Use GameSessionRepository.delete() instead"""
        db.session.delete(self)
        db.session.commit()

    def format(self):
        """Return formatted game session as dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'score': self.score,
            'category_id': self.category_id,
            'number_of_questions': self.number_of_questions,
            'date_played': self.date_played.isoformat()
        }

    def __repr__(self):
        return f'<GameSession {self.id}: user={self.user_id}, score={self.score}>'
