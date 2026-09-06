"""Category model - Pure ORM definition"""

from sqlalchemy import Column, Integer, String, CheckConstraint
from . import db


class Category(db.Model):
    """
    Category model representing a trivia question category
    Pure ORM definition - no business logic
    """
    __tablename__ = 'categories'
    
    # Table constraints
    __table_args__ = (
        CheckConstraint('length(type) >= 1 AND length(type) <= 100', name='ck_type_length'),
    )

    id = Column(Integer, primary_key=True)
    type = Column(String, unique=True, nullable=False)

    def __init__(self, type):
        self.type = type

    def format(self):
        """Return formatted category as dictionary"""
        return {
            'id': self.id,
            'type': self.type
        }

    def __repr__(self):
        return f'<Category {self.id}: {self.type}>'
