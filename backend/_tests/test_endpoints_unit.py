"""
Unit tests for endpoint layer
Tests HTTP request/response handling in isolation with mocked services
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json

import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flaskr import create_app
from data_access import db


class UsersEndpointUnitTests(unittest.TestCase):
    """Unit tests for /users endpoint - mock UserService"""

    def setUp(self):
        """Set up test app"""
        self.database_path = "sqlite:///:memory:"
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clean up"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('controllers.users.UserService')
    def test_create_user_returns_201_on_success(self, mock_service):
        """Test endpoint returns 201 on successful user creation"""
        mock_user = Mock()
        mock_user.format.return_value = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'total_score': 0,
            'games_played': 0,
            'created_at': '2026-09-04T16:00:00'
        }
        mock_service.create_user.return_value = mock_user
        
        response = self.client.post(
            '/users',
            json={'username': 'testuser', 'email': 'test@example.com'}
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['username'], 'testuser')

    @patch('controllers.users.UserService')
    def test_create_user_calls_service(self, mock_service):
        """Test endpoint calls UserService.create_user"""
        mock_user = Mock()
        mock_user.format.return_value = {}
        mock_service.create_user.return_value = mock_user
        
        self.client.post(
            '/users',
            json={'username': 'testuser', 'email': 'test@example.com'}
        )
        
        mock_service.create_user.assert_called_once_with('testuser', 'test@example.com')

    @patch('controllers.users.UserService')
    def test_create_user_returns_400_for_missing_username(self, mock_service):
        """Test endpoint returns 400 when username is missing"""
        response = self.client.post(
            '/users',
            json={'email': 'test@example.com'}
        )
        
        self.assertEqual(response.status_code, 400)

    @patch('controllers.users.UserService')
    def test_create_user_returns_400_for_missing_email(self, mock_service):
        """Test endpoint returns 400 when email is missing"""
        response = self.client.post(
            '/users',
            json={'username': 'testuser'}
        )
        
        self.assertEqual(response.status_code, 400)

    @patch('controllers.users.UserService')
    def test_create_user_returns_400_for_empty_request(self, mock_service):
        """Test endpoint returns 400 for empty request body"""
        response = self.client.post('/users', json={})
        self.assertEqual(response.status_code, 400)

    @patch('controllers.users.UserService')
    def test_create_user_returns_400_for_validation_error(self, mock_service):
        """Test endpoint returns 400 for validation errors"""
        mock_service.create_user.side_effect = ValueError("Username too short")
        
        response = self.client.post(
            '/users',
            json={'username': 'ab', 'email': 'test@example.com'}
        )
        
        self.assertEqual(response.status_code, 400)

    @patch('controllers.users.UserService')
    def test_create_user_returns_422_for_duplicate_username(self, mock_service):
        """Test endpoint returns 422 for duplicate username"""
        mock_service.create_user.side_effect = ValueError("Username 'testuser' already exists")
        
        response = self.client.post(
            '/users',
            json={'username': 'testuser', 'email': 'test@example.com'}
        )
        
        self.assertEqual(response.status_code, 422)

    @patch('controllers.users.UserService')
    def test_create_user_returns_422_for_duplicate_email(self, mock_service):
        """Test endpoint returns 422 for duplicate email"""
        mock_service.create_user.side_effect = ValueError("Email 'test@example.com' already registered")
        
        response = self.client.post(
            '/users',
            json={'username': 'user2', 'email': 'test@example.com'}
        )
        
        self.assertEqual(response.status_code, 422)


class CategoriesEndpointUnitTests(unittest.TestCase):
    """Unit tests for /categories endpoint - mock CategoryService"""

    def setUp(self):
        """Set up test app"""
        self.database_path = "sqlite:///:memory:"
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clean up"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('controllers.categories.CategoryService')
    def test_create_category_returns_201_on_success(self, mock_service):
        """Test endpoint returns 201 on successful category creation"""
        mock_category = Mock()
        mock_category.format.return_value = {'id': 1, 'type': 'Science'}
        mock_service.create_category.return_value = mock_category
        
        response = self.client.post(
            '/categories',
            json={'type': 'Science'}
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['type'], 'Science')

    @patch('controllers.categories.CategoryService')
    def test_create_category_calls_service(self, mock_service):
        """Test endpoint calls CategoryService.create_category"""
        mock_category = Mock()
        mock_category.format.return_value = {}
        mock_service.create_category.return_value = mock_category
        
        self.client.post(
            '/categories',
            json={'type': 'Science'}
        )
        
        mock_service.create_category.assert_called_once_with('Science')

    @patch('controllers.categories.CategoryService')
    def test_create_category_returns_400_for_missing_type(self, mock_service):
        """Test endpoint returns 400 when type is missing"""
        response = self.client.post('/categories', json={})
        self.assertEqual(response.status_code, 400)

    @patch('controllers.categories.CategoryService')
    def test_create_category_returns_422_for_duplicate(self, mock_service):
        """Test endpoint returns 422 for duplicate category"""
        mock_service.create_category.side_effect = ValueError("Category 'Science' already exists")
        
        response = self.client.post(
            '/categories',
            json={'type': 'Science'}
        )
        
        self.assertEqual(response.status_code, 422)


class QuestionsEndpointUnitTests(unittest.TestCase):
    """Unit tests for /questions endpoint - mock QuestionService"""

    def setUp(self):
        """Set up test app"""
        self.database_path = "sqlite:///:memory:"
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clean up"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('controllers.questions.CategoryService')
    @patch('controllers.questions.QuestionService')
    def test_create_question_returns_201_on_success(self, mock_service, mock_category_service):
        """Test endpoint returns 201 on successful question creation"""
        mock_question = Mock()
        mock_question.format.return_value = {
            'id': 1,
            'question': 'What is H2O?',
            'answer': 'Water',
            'category': 1,
            'difficulty': 1,
            'rating': 4.5
        }
        mock_service.create_question.return_value = mock_question
        mock_category_service.get_category.return_value = Mock(id=1)
        
        response = self.client.post(
            '/questions',
            json={
                'question': 'What is H2O?',
                'answer': 'Water',
                'category': 1,
                'difficulty': 1,
                'rating': 4.5
            }
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['question'], 'What is H2O?')

    @patch('controllers.questions.CategoryService')
    @patch('controllers.questions.QuestionService')
    def test_create_question_calls_service_with_correct_args(self, mock_service, mock_category_service):
        """Test endpoint calls QuestionService with correct arguments"""
        mock_question = Mock()
        mock_question.format.return_value = {}
        mock_service.create_question.return_value = mock_question
        mock_category_service.get_category.return_value = Mock(id=1)
        
        self.client.post(
            '/questions',
            json={
                'question': 'What is H2O?',
                'answer': 'Water',
                'category': 1,
                'difficulty': 1,
                'rating': 4.5
            }
        )
        
        mock_service.create_question.assert_called_once_with(
            question_text='What is H2O?',
            answer='Water',
            category=1,
            difficulty=1,
            rating=4.5
        )

    @patch('controllers.questions.QuestionService')
    def test_create_question_returns_400_for_missing_question(self, mock_service):
        """Test endpoint returns 400 when question is missing"""
        response = self.client.post(
            '/questions',
            json={
                'answer': 'Water',
                'category': 1,
                'difficulty': 1
            }
        )
        
        self.assertEqual(response.status_code, 400)

    @patch('controllers.questions.QuestionService')
    def test_create_question_returns_400_for_missing_answer(self, mock_service):
        """Test endpoint returns 400 when answer is missing"""
        response = self.client.post(
            '/questions',
            json={
                'question': 'What is H2O?',
                'category': 1,
                'difficulty': 1
            }
        )
        
        self.assertEqual(response.status_code, 400)

    @patch('controllers.questions.QuestionService')
    def test_create_question_returns_400_for_missing_category(self, mock_service):
        """Test endpoint returns 400 when category is missing"""
        response = self.client.post(
            '/questions',
            json={
                'question': 'What is H2O?',
                'answer': 'Water',
                'difficulty': 1
            }
        )
        
        self.assertEqual(response.status_code, 400)

    @patch('controllers.questions.QuestionService')
    def test_create_question_returns_400_for_missing_difficulty(self, mock_service):
        """Test endpoint returns 400 when difficulty is missing"""
        response = self.client.post(
            '/questions',
            json={
                'question': 'What is H2O?',
                'answer': 'Water',
                'category': 1
            }
        )
        
        self.assertEqual(response.status_code, 400)

    @patch('controllers.questions.CategoryService')
    @patch('controllers.questions.QuestionService')
    def test_create_question_uses_default_rating(self, mock_service, mock_category_service):
        """Test endpoint uses default rating of 0"""
        mock_question = Mock()
        mock_question.format.return_value = {}
        mock_service.create_question.return_value = mock_question
        mock_category_service.get_category.return_value = Mock(id=1)
        
        self.client.post(
            '/questions',
            json={
                'question': 'What is H2O?',
                'answer': 'Water',
                'category': 1,
                'difficulty': 1
            }
        )
        
        # Verify rating was passed as 0 (default)
        call_kwargs = mock_service.create_question.call_args[1]
        self.assertEqual(call_kwargs['rating'], 0)

    @patch('controllers.questions.CategoryService')
    @patch('controllers.questions.QuestionService')
    def test_create_question_returns_400_for_validation_error(self, mock_service, mock_category_service):
        """Test endpoint returns 422 for category validation errors"""
        mock_category_service.get_category.side_effect = ValueError("Category not found")
        
        response = self.client.post(
            '/questions',
            json={
                'question': 'Q?',
                'answer': 'A',
                'category': 9999,
                'difficulty': 1
            }
        )
        
        self.assertEqual(response.status_code, 422)


if __name__ == '__main__':
    unittest.main()
