"""
Unit tests for repository layer
Tests CRUD logic in isolation with mocked db.session
"""

import unittest
from unittest.mock import Mock, MagicMock, patch

import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flaskr import create_app
from data_access.user_repository import UserRepository
from data_access.category_repository import CategoryRepository
from data_access.question_repository import QuestionRepository
from models import User, Category, Question
from data_access import db


class UserRepositoryUnitTests(unittest.TestCase):
    """Unit tests for UserRepository - mock db.session"""

    def setUp(self):
        """Set up test fixtures with Flask app context"""
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "TESTING": True
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.mock_session = MagicMock()

    def tearDown(self):
        """Cleanup"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('data_access.user_repository.db')
    def test_create_user_calls_session_add(self, mock_db):
        """Test that create() calls db.session.add"""
        mock_db.session = self.mock_session
        mock_user = Mock(spec=User)
        
        with patch('data_access.user_repository.User', return_value=mock_user):
            UserRepository.create('testuser', 'test@example.com')
        
        # Verify db.session.add was called
        mock_db.session.add.assert_called_once_with(mock_user)

    @patch('data_access.user_repository.db')
    def test_create_user_returns_user_object(self, mock_db):
        """Test that create() returns the user object"""
        mock_db.session = self.mock_session
        mock_user = Mock(spec=User)
        
        with patch('data_access.user_repository.User', return_value=mock_user):
            result = UserRepository.create('testuser', 'test@example.com')
        
        self.assertEqual(result, mock_user)

    def test_get_by_username_queries_database(self):
        """Test that get_by_username() queries the database"""
        # Create a real user first
        user = User('testuser', 'test@example.com')
        db.session.add(user)
        db.session.commit()
        
        # Query via repository
        result = UserRepository.get_by_username('testuser')
        
        self.assertIsNotNone(result)
        self.assertEqual(result.username, 'testuser')

    def test_exists_by_username_returns_boolean(self):
        """Test that exists_by_username() returns a boolean"""
        user = User('testuser', 'test@example.com')
        db.session.add(user)
        db.session.commit()
        
        result = UserRepository.exists_by_username('testuser')
        
        self.assertTrue(result)

    def test_exists_by_username_returns_false_when_not_found(self):
        """Test that exists_by_username() returns False when user doesn't exist"""
        result = UserRepository.exists_by_username('nonexistent')
        
        self.assertFalse(result)

    @patch('data_access.user_repository.db')
    def test_update_user_modifies_attributes(self, mock_db):
        """Test that update() modifies user attributes"""
        mock_db.session = self.mock_session
        mock_user = Mock()
        
        UserRepository.update(mock_user, total_score=100, games_played=5)
        
        # Verify attributes were set
        self.assertEqual(mock_user.total_score, 100)
        self.assertEqual(mock_user.games_played, 5)

    @patch('data_access.user_repository.db')
    def test_delete_user_calls_session_delete(self, mock_db):
        """Test that delete() calls db.session.delete"""
        mock_db.session = self.mock_session
        mock_user = Mock()
        
        UserRepository.delete(mock_user)
        
        # Verify db.session.delete was called
        mock_db.session.delete.assert_called_once_with(mock_user)


class CategoryRepositoryUnitTests(unittest.TestCase):
    """Unit tests for CategoryRepository - mock db.session"""

    def setUp(self):
        """Set up test fixtures with Flask app context"""
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "TESTING": True
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.mock_session = MagicMock()

    def tearDown(self):
        """Cleanup"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('data_access.category_repository.db')
    def test_create_category_calls_session_add(self, mock_db):
        """Test that create() calls db.session.add"""
        mock_db.session = self.mock_session
        mock_category = Mock(spec=Category)
        
        with patch('data_access.category_repository.Category', return_value=mock_category):
            CategoryRepository.create('Science')
        
        mock_db.session.add.assert_called_once_with(mock_category)

    def test_get_by_type_queries_database(self):
        """Test that get_by_type() queries the database"""
        category = Category('Science')
        db.session.add(category)
        db.session.commit()
        
        result = CategoryRepository.get_by_type('Science')
        
        self.assertIsNotNone(result)
        self.assertEqual(result.type, 'Science')

    def test_exists_by_type_returns_boolean(self):
        """Test that exists_by_type() returns a boolean"""
        category = Category('Science')
        db.session.add(category)
        db.session.commit()
        
        result = CategoryRepository.exists_by_type('Science')
        
        self.assertTrue(result)

    @patch('data_access.category_repository.db')
    def test_delete_category_calls_session_delete(self, mock_db):
        """Test that delete() calls db.session.delete"""
        mock_db.session = self.mock_session
        mock_category = Mock()
        
        CategoryRepository.delete(mock_category)
        
        mock_db.session.delete.assert_called_once_with(mock_category)


class QuestionRepositoryUnitTests(unittest.TestCase):
    """Unit tests for QuestionRepository - mock db.session"""

    def setUp(self):
        """Set up test fixtures with Flask app context"""
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "TESTING": True
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.mock_session = MagicMock()

    def tearDown(self):
        """Cleanup"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('data_access.question_repository.db')
    def test_create_question_calls_session_add(self, mock_db):
        """Test that create() calls db.session.add"""
        mock_db.session = self.mock_session
        mock_question = Mock(spec=Question)
        
        with patch('data_access.question_repository.Question', return_value=mock_question):
            QuestionRepository.create('What?', 'Answer', 1, 1)
        
        mock_db.session.add.assert_called_once_with(mock_question)

    def test_get_by_id_queries_database(self):
        """Test that get_by_id() queries the database"""
        category = Category('Science')
        db.session.add(category)
        db.session.commit()
        
        question = Question('What is H2O?', 'Water', category.id, 1)
        db.session.add(question)
        db.session.commit()
        
        result = QuestionRepository.get_by_id(question.id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.question, 'What is H2O?')

    def test_search_uses_ilike(self):
        """Test that search() uses ILIKE for case-insensitive search"""
        category = Category('Science')
        db.session.add(category)
        db.session.commit()
        
        question = Question('What is water?', 'H2O', category.id, 1)
        db.session.add(question)
        db.session.commit()
        
        # Search with different case - returns pagination object
        result = QuestionRepository.search('WATER')
        
        self.assertIsNotNone(result)
        # Verify at least one result in the items
        self.assertTrue(len(result.items) > 0)

    @patch('data_access.question_repository.db')
    def test_delete_question_calls_session_delete(self, mock_db):
        """Test that delete() calls db.session.delete"""
        mock_db.session = self.mock_session
        mock_question = Mock()
        
        QuestionRepository.delete(mock_question)
        
        mock_db.session.delete.assert_called_once_with(mock_question)


if __name__ == '__main__':
    unittest.main()
