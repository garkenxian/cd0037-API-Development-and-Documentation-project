"""
Models package - Pure SQLAlchemy ORM definitions
No business logic, no session operations
"""

from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize SQLAlchemy
db = SQLAlchemy()

def setup_db(app, database_path=None):
    """Setup database for Flask app"""
    if database_path is None:
        database_path = os.getenv('SQLALCHEMY_DATABASE_URI') or os.getenv('DATABASE_URL')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()

# Import models after db is initialized
from .user import User
from .category import Category
from .question import Question
from .game_session import GameSession

# Export all models and utilities
__all__ = ['db', 'setup_db', 'User', 'Category', 'Question', 'GameSession']
