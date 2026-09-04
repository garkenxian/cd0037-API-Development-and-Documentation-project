"""Question model - Pure ORM definition"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey
from . import db


class Question(db.Model):
    """
    Question model representing a trivia question with rating support
    Pure ORM definition - no business logic
    """
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    category = Column(Integer, ForeignKey('categories.id'), nullable=False)
    difficulty = Column(Integer, nullable=False)
    rating = Column(Float, nullable=True, default=0)

    def __init__(self, question, answer, category, difficulty, rating=0):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty
        self.rating = rating

    def format(self):
        """Return formatted question as dictionary"""
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty,
            'rating': self.rating
        }

    def __repr__(self):
        return f'<Question {self.id}: {self.question[:50]}...>'
