from sqlalchemy import Column, Integer, String
from . import db


class Category(db.Model):
    """
    Category model representing a trivia question category
    """
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)

    def __init__(self, type):
        self.type = type

    def insert(self):
        """Insert this category into the database"""
        db.session.add(self)
        db.session.commit()

    def update(self):
        """Update this category in the database"""
        db.session.commit()

    def delete(self):
        """Delete this category from the database"""
        db.session.delete(self)
        db.session.commit()

    def format(self):
        """Return formatted category as dictionary"""
        return {
            'id': self.id,
            'type': self.type
        }

    def __repr__(self):
        return f'<Category {self.id}: {self.type}>'
