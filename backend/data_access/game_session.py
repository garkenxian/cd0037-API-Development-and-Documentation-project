from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from . import db


class GameSession(db.Model):
    """
    GameSession model for tracking individual quiz game results
    """
    __tablename__ = 'game_sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    score = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    date_played = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, user_id, score, category_id=None):
        self.user_id = user_id
        self.score = score
        self.category_id = category_id

    def insert(self):
        """Insert this game session into the database"""
        db.session.add(self)
        db.session.commit()

    def update(self):
        """Update this game session in the database"""
        db.session.commit()

    def delete(self):
        """Delete this game session from the database"""
        db.session.delete(self)
        db.session.commit()

    def format(self):
        """Return formatted game session as dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'score': self.score,
            'category_id': self.category_id,
            'date_played': self.date_played.isoformat()
        }

    def __repr__(self):
        return f'<GameSession {self.id}: user={self.user_id}, score={self.score}>'
