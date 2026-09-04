"""Integration tests for /games endpoint"""

import unittest
from unittest.mock import Mock, patch

import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flaskr import create_app
from data_access import db
from models import User, Category, Question, GameSession


class GamesEndpointUnitTests(unittest.TestCase):
    """Integration tests for /games endpoint"""

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

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _create_test_data(self):
        """Helper to create test data"""
        # Create test user
        user = User(username='test_user', email='test@example.com')
        db.session.add(user)
        db.session.commit()
        
        # Create test category
        category = Category(type='Science')
        db.session.add(category)
        db.session.commit()
        
        # Create test question
        question = Question(
            question='What is H2O?',
            answer='Water',
            category=category.id,
            difficulty=2,
            rating=4.5
        )
        db.session.add(question)
        db.session.commit()
        
        return user, category, question

    def test_create_game_success(self):
        """Test successful game creation"""
        user, category, question = self._create_test_data()
        
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 5
            }
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('game_session_id', data)
        self.assertEqual(data['question_number'], 1)
        self.assertEqual(data['current_score']['correct'], 0)
        self.assertEqual(data['current_score']['total_questions'], 5)
        self.assertIn('question', data)
        self.assertEqual(data['question']['id'], question.id)

    def test_create_game_missing_user_id(self):
        """Test game creation fails with missing user_id"""
        response = self.client.post(
            '/games',
            json={
                'category_id': 1,
                'number_of_questions': 5
            }
        )
        
        self.assertEqual(response.status_code, 400)

    def test_create_game_invalid_user(self):
        """Test game creation fails with non-existent user"""
        response = self.client.post(
            '/games',
            json={
                'user_id': 9999,
                'category_id': 1,
                'number_of_questions': 5
            }
        )
        
        self.assertEqual(response.status_code, 404)

    def test_create_game_invalid_category(self):
        """Test game creation fails with non-existent category"""
        user, _, _ = self._create_test_data()
        
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': 9999,
                'number_of_questions': 5
            }
        )
        
        self.assertEqual(response.status_code, 404)

    def test_create_game_invalid_number_of_questions(self):
        """Test game creation fails with invalid number_of_questions"""
        user, category, _ = self._create_test_data()
        
        # Test with 0
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 0
            }
        )
        self.assertEqual(response.status_code, 422)
        
        # Test with 21 (too high)
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 21
            }
        )
        self.assertEqual(response.status_code, 422)

    def test_create_game_default_number_of_questions(self):
        """Test game creation uses default number_of_questions"""
        user, category, _ = self._create_test_data()
        
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id
            }
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['current_score']['total_questions'], 5)

    def test_get_game_success(self):
        """Test getting game session successfully"""
        user, category, _ = self._create_test_data()
        
        # Create game first
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 5
            }
        )
        game_session_id = response.get_json()['game_session_id']
        
        # Get game
        response = self.client.get(f'/games/{game_session_id}')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['game_session_id'], game_session_id)
        self.assertEqual(data['user_id'], user.id)
        self.assertEqual(data['category_id'], category.id)
        self.assertEqual(data['score'], 0)

    def test_get_game_not_found(self):
        """Test getting non-existent game"""
        response = self.client.get('/games/9999')
        
        self.assertEqual(response.status_code, 404)

    def test_answer_question_success(self):
        """Test answering a question"""
        user, category, _ = self._create_test_data()
        
        # Create game
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 5
            }
        )
        game_session_id = response.get_json()['game_session_id']
        
        # Answer question
        response = self.client.post(
            f'/games/{game_session_id}/1',
            json={'user_answer': 'Water'}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['game_session_id'], game_session_id)
        self.assertEqual(data['question_number'], 1)

    def test_answer_question_missing_answer(self):
        """Test answering question with missing user_answer"""
        user, category, _ = self._create_test_data()
        
        # Create game
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 5
            }
        )
        game_session_id = response.get_json()['game_session_id']
        
        # Try to answer without user_answer
        response = self.client.post(
            f'/games/{game_session_id}/1',
            json={}
        )
        
        self.assertEqual(response.status_code, 400)

    def test_answer_question_game_not_found(self):
        """Test answering question for non-existent game"""
        response = self.client.post(
            '/games/9999/1',
            json={'user_answer': 'Water'}
        )
        
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
