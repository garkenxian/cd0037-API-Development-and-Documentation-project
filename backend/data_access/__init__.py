"""
Data Access Layer Package
Exports models from models/ package and repositories for queries
Maintains backward compatibility with existing imports
"""

# Import db and setup from models package
from models import db, setup_db, User, Category, Question, GameSession

# Import repositories
from .user_repository import UserRepository
from .category_repository import CategoryRepository
from .question_repository import QuestionRepository
from .game_session_repository import GameSessionRepository

# Export everything for backward compatibility
__all__ = [
    'db',
    'setup_db',
    'User',
    'Category', 
    'Question',
    'GameSession',
    'UserRepository',
    'CategoryRepository',
    'QuestionRepository',
    'GameSessionRepository'
]
