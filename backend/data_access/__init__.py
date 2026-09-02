import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

# Load environment variables from .env file
load_dotenv()

# Build database URL from environment variables or use DATABASE_URL if provided
database_path = os.getenv('DATABASE_URL')

# Initialize SQLAlchemy
db = SQLAlchemy()

"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""
def setup_db(app, database_path=database_path):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()

# Import models after db is initialized
from .question import Question
from .category import Category
from .user import User
from .game_session import GameSession

# Export all models and utilities
__all__ = ['db', 'setup_db', 'Question', 'Category', 'User', 'GameSession']
