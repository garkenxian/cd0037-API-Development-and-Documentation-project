"""User model - Pure ORM definition"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from . import db


class User(db.Model):
    """
    User model for tracking player profiles and scores
    Pure ORM definition - no business logic
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=True)
    total_score = Column(Integer, default=0, nullable=False)
    games_played = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to game sessions
    game_sessions = relationship('GameSession', backref='user', lazy=True, foreign_keys='GameSession.user_id')

    def __init__(self, username, email=None):
        self.username = username
        self.email = email
        self.total_score = 0
        self.games_played = 0

    def format(self):
        """Return formatted user as dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'total_score': self.total_score,
            'games_played': self.games_played,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<User {self.id}: {self.username}>'
