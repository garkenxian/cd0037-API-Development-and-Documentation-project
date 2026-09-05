"""User model - Pure ORM definition"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from . import db


class User(db.Model):
    """
    User model for tracking player profiles and scores
    Pure ORM definition - no business logic
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    total_score = Column(Integer, default=0, nullable=False)
    games_played = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __init__(self, username, email):
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
