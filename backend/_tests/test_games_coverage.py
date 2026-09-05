"""Comprehensive tests for games controller to reach 80% coverage"""

import unittest
from unittest.mock import patch, MagicMock
from flaskr import create_app
from data_access import db
from data_access.user_repository import UserRepository
from data_access.category_repository import CategoryRepository


class GamesErrorHandlingTests(unittest.TestCase):
    """Test error handling in games controller"""

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
        self.cat1 = CategoryRepository.create('Science')
        db.session.commit()

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        self.app_context.pop()

    def test_create_game_no_json_body(self):
        """Test POST /games with no JSON body"""
        response = self.client.post('/games', json={})
        self.assertEqual(response.status_code, 400)

    def test_create_game_missing_user_id(self):
        """Test POST /games with missing user_id"""
        response = self.client.post('/games', json={
            'category_id': self.cat1.id,
            'number_of_questions': 5
        })
        self.assertEqual(response.status_code, 400)

    def test_create_game_missing_category_id(self):
        """Test POST /games with missing category_id"""
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'number_of_questions': 5
        })
        self.assertEqual(response.status_code, 400)

    def test_create_game_user_id_none(self):
        """Test POST /games with null user_id"""
        response = self.client.post('/games', json={
            'user_id': None,
            'category_id': self.cat1.id
        })
        self.assertEqual(response.status_code, 400)

    def test_create_game_category_id_none(self):
        """Test POST /games with null category_id"""
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': None
        })
        self.assertEqual(response.status_code, 400)

    def test_create_game_invalid_user(self):
        """Test POST /games with invalid user_id"""
        response = self.client.post('/games', json={
            'user_id': 99999,
            'category_id': self.cat1.id
        })
        self.assertEqual(response.status_code, 404)

    def test_create_game_invalid_category(self):
        """Test POST /games with invalid category_id"""
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': 99999
        })
        self.assertEqual(response.status_code, 404)

    def test_create_game_invalid_questions_count_string(self):
        """Test POST /games with string for number_of_questions"""
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat1.id,
            'number_of_questions': 'five'
        })
        self.assertEqual(response.status_code, 422)

    def test_create_game_invalid_questions_count_float(self):
        """Test POST /games with float for number_of_questions"""
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat1.id,
            'number_of_questions': 5.5
        })
        self.assertEqual(response.status_code, 422)

    def test_create_game_zero_questions(self):
        """Test POST /games with zero questions"""
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat1.id,
            'number_of_questions': 0
        })
        self.assertEqual(response.status_code, 422)

    def test_create_game_negative_questions(self):
        """Test POST /games with negative questions"""
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat1.id,
            'number_of_questions': -5
        })
        self.assertEqual(response.status_code, 422)

    def test_create_game_too_many_questions(self):
        """Test POST /games with more than 20 questions"""
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat1.id,
            'number_of_questions': 21
        })
        self.assertEqual(response.status_code, 422)

    def test_create_game_success(self):
        """Test successful game creation"""
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat1.id,
            'number_of_questions': 5
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('game_session_id', data)

    def test_get_game_not_found(self):
        """Test GET /games/<id> with invalid game_id"""
        response = self.client.get('/games/99999')
        self.assertEqual(response.status_code, 404)

    def test_answer_question_game_not_found(self):
        """Test POST answer with invalid game_id"""
        response = self.client.post('/games/99999/1', json={
            'user_answer': 'answer'
        })
        self.assertEqual(response.status_code, 404)

    def test_answer_question_no_json_body(self):
        """Test POST answer with no JSON body"""
        create_response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat1.id,
            'number_of_questions': 5
        })
        game_id = create_response.get_json()['game_session_id']
        
        response = self.client.post(f'/games/{game_id}/1', json={})
        self.assertEqual(response.status_code, 400)

    def test_answer_question_missing_user_answer(self):
        """Test POST answer with missing user_answer"""
        create_response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat1.id,
            'number_of_questions': 5
        })
        game_id = create_response.get_json()['game_session_id']
        
        response = self.client.post(f'/games/{game_id}/1', json={})
        self.assertEqual(response.status_code, 400)

    def test_answer_question_null_answer(self):
        """Test POST answer with null user_answer"""
        create_response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat1.id,
            'number_of_questions': 5
        })
        game_id = create_response.get_json()['game_session_id']
        
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': None
        })
        self.assertEqual(response.status_code, 400)

    def test_answer_question_empty_string_answer(self):
        """Test POST answer with empty string answer"""
        create_response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat1.id,
            'number_of_questions': 5
        })
        game_id = create_response.get_json()['game_session_id']
        
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': ''
        })
        self.assertEqual(response.status_code, 400)

    def test_answer_question_whitespace_answer(self):
        """Test POST answer with whitespace answer"""
        create_response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat1.id,
            'number_of_questions': 5
        })
        game_id = create_response.get_json()['game_session_id']
        
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': '   '
        })
        self.assertEqual(response.status_code, 400)

    def test_answer_question_answer_not_string(self):
        """Test POST answer with non-string answer"""
        create_response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat1.id,
            'number_of_questions': 5
        })
        game_id = create_response.get_json()['game_session_id']
        
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': 123
        })
        self.assertEqual(response.status_code, 400)

    def test_answer_question_invalid_question_number(self):
        """Test POST answer with invalid question number"""
        create_response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat1.id,
            'number_of_questions': 5
        })
        game_id = create_response.get_json()['game_session_id']
        
        # Question number 0 is invalid (must be 1-5)
        response = self.client.post(f'/games/{game_id}/0', json={
            'user_answer': 'answer'
        })
        self.assertEqual(response.status_code, 400)

    def test_answer_question_question_number_too_high(self):
        """Test POST answer with question number beyond game length"""
        create_response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat1.id,
            'number_of_questions': 5
        })
        game_id = create_response.get_json()['game_session_id']
        
        # Question 10 is beyond 5 questions
        response = self.client.post(f'/games/{game_id}/10', json={
            'user_answer': 'answer'
        })
        self.assertEqual(response.status_code, 400)


class GamesServiceExceptionTests(unittest.TestCase):
    """Test service exception handling in games controller"""

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

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        self.app_context.pop()

    @patch('controllers.games.UserService.get_user')
    def test_create_game_user_service_error(self, mock_user_service):
        """Test POST /games when UserService raises exception"""
        mock_user_service.side_effect = Exception("Database error")
        
        response = self.client.post('/games', json={
            'user_id': 1,
            'category_id': 1
        })
        self.assertEqual(response.status_code, 500)


if __name__ == '__main__':
    unittest.main()
