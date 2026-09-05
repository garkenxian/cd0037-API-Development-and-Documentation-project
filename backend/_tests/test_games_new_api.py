"""Tests for the new /games endpoints with proper error handling"""

import unittest
import json
from unittest.mock import patch
from flaskr import create_app
from data_access import db
from data_access.category_repository import CategoryRepository
from data_access.question_repository import QuestionRepository
from data_access.user_repository import UserRepository


class GamesEndpointTests(unittest.TestCase):
    """Test the new /games endpoints"""

    def setUp(self):
        """Set up test database and app context"""
        self.database_path = "sqlite:///:memory:"
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        # Push app context
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create tables
        db.create_all()
        
        # Create test data
        self.user = UserRepository.create('testuser', None)
        db.session.flush()
        
        self.cat_science = CategoryRepository.create('Science')
        db.session.flush()
        
        self.q1 = QuestionRepository.create('Q1?', 'Water', self.cat_science.id, 'easy')
        self.q2 = QuestionRepository.create('Q2?', 'Answer2', self.cat_science.id, 'medium')
        db.session.commit()

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        self.app_context.pop()

    # ==================== POST /games Tests ====================

    def test_create_game_success(self):
        """Test successful game creation"""
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 5
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('game_session_id', data)
        self.assertIn('question', data)
        self.assertIsNotNone(data['question'])

    def test_create_game_missing_user_id(self):
        """Test POST /games with missing user_id"""
        response = self.client.post('/games', json={
            'category_id': self.cat_science.id
        })
        self.assertEqual(response.status_code, 400)

    def test_create_game_missing_category_id(self):
        """Test POST /games with missing category_id"""
        response = self.client.post('/games', json={
            'user_id': self.user.id
        })
        self.assertEqual(response.status_code, 400)

    def test_create_game_invalid_user(self):
        """Test POST /games with invalid user"""
        response = self.client.post('/games', json={
            'user_id': 999,
            'category_id': self.cat_science.id
        })
        self.assertEqual(response.status_code, 404)

    def test_create_game_invalid_category(self):
        """Test POST /games with invalid category"""
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': 999
        })
        self.assertEqual(response.status_code, 404)

    def test_create_game_invalid_questions_count(self):
        """Test POST /games with invalid number_of_questions"""
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 25  # Invalid: > 20
        })
        self.assertEqual(response.status_code, 422)

    def test_create_game_zero_questions(self):
        """Test POST /games with zero questions"""
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 0
        })
        self.assertEqual(response.status_code, 422)

    def test_create_game_with_all_categories(self):
        """Test POST /games with category_id=0 (all categories)"""
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': 0  # All categories
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])

    # ==================== GET /games/:id Tests ====================

    def test_get_game_success(self):
        """Test getting game state"""
        # Create a game first
        create_response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 5
        })
        game_id = create_response.get_json()['game_session_id']
        
        # Get game state
        response = self.client.get(f'/games/{game_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['game_session_id'], game_id)
        self.assertIn('question_number', data)

    def test_get_game_not_found(self):
        """Test getting nonexistent game"""
        response = self.client.get('/games/999')
        self.assertEqual(response.status_code, 404)

    # ==================== POST /games/:id/:question_number Tests ====================

    def test_answer_question_correct(self):
        """Test answering a question correctly"""
        # Create a game first
        create_response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 5
        })
        response_data = create_response.get_json()
        game_id = response_data['game_session_id']
        
        # Mock QuestionService to return q1 with known answer 'Water'
        with patch('controllers.games.QuestionService.get_random_question_by_category') as mock_get:
            mock_get.return_value = self.q1
            
            # Answer a question with the correct answer for q1
            response = self.client.post(f'/games/{game_id}/1', json={
                'user_answer': 'Water'
            })
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['success'])
            self.assertTrue(data['correct'])
            self.assertIn('correct_answer', data)

    def test_answer_question_incorrect(self):
        """Test answering a question incorrectly"""
        # Create a game first
        create_response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 5
        })
        game_id = create_response.get_json()['game_session_id']
        
        # Answer incorrectly
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': 'Wrong'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data['correct'])

    def test_answer_question_missing_answer(self):
        """Test POST answer with missing user_answer"""
        # Create a game first
        create_response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 5
        })
        game_id = create_response.get_json()['game_session_id']
        
        # Answer without user_answer
        response = self.client.post(f'/games/{game_id}/1', json={})
        self.assertEqual(response.status_code, 400)

    def test_answer_question_invalid_game(self):
        """Test POST answer for nonexistent game"""
        response = self.client.post('/games/999/1', json={
            'user_answer': 'Answer'
        })
        self.assertEqual(response.status_code, 404)

    def test_answer_question_invalid_question_number(self):
        """Test POST answer with invalid question number"""
        # Create a game first
        create_response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 5
        })
        game_id = create_response.get_json()['game_session_id']
        
        # Answer question 10 (game only has 5)
        response = self.client.post(f'/games/{game_id}/10', json={
            'user_answer': 'Answer'
        })
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
