"""
Test error response schema compliance for all endpoints.

Validates that all error responses conform to the standardized schema:
{
    "error": <status_code>,
    "message": "<descriptive_message>",
    "success": false
}
"""

import unittest
import json
from unittest.mock import patch
from flaskr import create_app
from data_access import db


class ErrorSchemaComplianceTests(unittest.TestCase):
    """Test that all error responses conform to the API specification schema."""
    
    def setUp(self):
        """Set up test client and database."""
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        with self.app.app_context():
            db.create_all()
        
        self.client = self.app.test_client()
    
    def tearDown(self):
        """Clean up after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        
        self.app_context.pop()
    
    def assert_error_schema(self, response, expected_status_code, contains_message=None):
        """
        Assert that response conforms to standardized error schema.
        
        Args:
            response: Flask test client response
            expected_status_code: Expected HTTP status code
            contains_message: If provided, assert message contains this substring
        """
        self.assertEqual(response.status_code, expected_status_code)
        
        data = response.get_json()
        
        # Validate schema structure
        self.assertIsNotNone(data, "Response body should be JSON")
        self.assertIn('error', data, "Error response must contain 'error' field")
        self.assertIn('message', data, "Error response must contain 'message' field")
        self.assertIn('success', data, "Error response must contain 'success' field")
        
        # Validate field values
        self.assertEqual(data['error'], expected_status_code, 
                        f"error field should match status code {expected_status_code}")
        self.assertFalse(data['success'], "success field should be False for error responses")
        
        # Validate message is a string
        self.assertIsInstance(data['message'], str, "message should be a string")
        self.assertGreater(len(data['message']), 0, "message should not be empty")
        
        # Validate message content if specified
        if contains_message:
            self.assertIn(contains_message, data['message'],
                         f"Message should contain '{contains_message}'")
    
    # ==================== 400 Bad Request Tests ====================
    
    def test_error_400_missing_json_body_categories(self):
        """Test 400 error when POST /categories with no JSON body."""
        response = self.client.post('/categories',
                                   data='',
                                   content_type='application/json')
        self.assert_error_schema(response, 400, 'JSON')
    
    def test_error_400_missing_required_field_users(self):
        """Test 400 error when POST /users without username."""
        response = self.client.post('/users',
                                   json={'email': 'test@example.com'},
                                   content_type='application/json')
        self.assert_error_schema(response, 400, 'username')
    
    def test_error_400_missing_required_field_questions(self):
        """Test 400 error when POST /questions without answer."""
        response = self.client.post('/questions',
                                   json={
                                       'question': 'What is 2+2?',
                                       'category': 1,
                                       'difficulty': 1
                                   },
                                   content_type='application/json')
        self.assert_error_schema(response, 400, 'answer')
    
    def test_error_400_invalid_page_parameter(self):
        """Test 400 error when GET /questions with invalid page."""
        response = self.client.get('/questions?page=0')
        self.assert_error_schema(response, 400, 'Page')
    
    def test_error_400_empty_user_answer_in_game(self):
        """Test 400 error when POST /games/<id>/<q> with empty user_answer."""
        response = self.client.post('/games/1/1',
                                   json={'user_answer': ''},
                                   content_type='application/json')
        self.assert_error_schema(response, 400, 'user_answer')
    
    # ==================== 404 Not Found Tests ====================
    
    def test_error_404_category_not_found(self):
        """Test 404 error when GET /categories/<invalid_id>."""
        response = self.client.get('/categories/99999')
        self.assert_error_schema(response, 404, 'not found')
    
    def test_error_404_user_not_found(self):
        """Test 404 error when GET /users/<invalid_id>."""
        response = self.client.get('/users/99999')
        self.assert_error_schema(response, 404, 'not found')
    
    def test_error_404_question_not_found(self):
        """Test 404 error when GET /questions/<invalid_id>."""
        response = self.client.get('/questions/99999')
        self.assert_error_schema(response, 404, 'not found')
    
    def test_error_404_game_not_found(self):
        """Test 404 error when GET /games/<invalid_id>."""
        response = self.client.get('/games/99999')
        self.assert_error_schema(response, 404, 'not found')
    
    def test_error_404_page_out_of_range(self):
        """Test 404 error when GET /questions?page=9999 when page is out of range."""
        # Create some questions first
        from services import CategoryService, QuestionService
        cat = CategoryService.create_category('Test Category')
        for i in range(5):
            QuestionService.create_question(
                question_text=f'Question {i}',
                answer=f'Answer {i}',
                category=cat.id,
                difficulty=1
            )
        
        # Try to access a page that's out of range
        response = self.client.get('/questions?page=9999')
        self.assert_error_schema(response, 404)
    
    # ==================== 422 Unprocessable Entity Tests ====================
    
    def test_error_422_duplicate_category(self):
        """Test 422 error when creating duplicate category."""
        from services import CategoryService
        CategoryService.create_category('Test Category')
        
        # Try to create duplicate
        response = self.client.post('/categories',
                                   json={'type': 'Test Category'},
                                   content_type='application/json')
        self.assert_error_schema(response, 422, 'exists')
    
    def test_error_422_duplicate_username(self):
        """Test 422 error when creating duplicate user."""
        from services import UserService
        UserService.create_user('testuser')
        
        # Try to create duplicate
        response = self.client.post('/users',
                                   json={'username': 'testuser'},
                                   content_type='application/json')
        self.assert_error_schema(response, 422, 'exists')

    def test_error_422_username_validation_constraints(self):
        """Test 422 error when username violates length constraints."""
        response = self.client.post('/users',
                                   json={'username': 'ab'},
                                   content_type='application/json')
        self.assert_error_schema(response, 422, 'between 3 and 50')
    
    def test_error_422_invalid_number_of_questions(self):
        """Test 422 error when number_of_questions is out of range."""
        from services import UserService, CategoryService
        user = UserService.create_user('testuser')
        cat = CategoryService.create_category('Test Category')
        
        # Try to create game with invalid number_of_questions
        response = self.client.post('/games',
                                   json={
                                       'user_id': user.id,
                                       'category_id': cat.id,
                                       'number_of_questions': 99
                                   },
                                   content_type='application/json')
        self.assert_error_schema(response, 422, 'number_of_questions')
    
    def test_error_422_delete_category_with_questions(self):
        """Test 422 error when deleting category that has questions."""
        from services import CategoryService, QuestionService
        cat = CategoryService.create_category('Test Category')
        QuestionService.create_question(
            question_text='Test Question',
            answer='Test Answer',
            category=cat.id,
            difficulty=1
        )
        
        # Try to delete category
        response = self.client.delete(f'/categories/{cat.id}')
        self.assert_error_schema(response, 422, 'Cannot delete')
    
    def test_error_422_insufficient_questions_in_category(self):
        """Test 422 error when creating game with more questions than exist in category."""
        from services import UserService, CategoryService, QuestionService
        user = UserService.create_user('testuser')
        cat = CategoryService.create_category('Test Category')
        
        # Create only 2 questions
        for i in range(2):
            QuestionService.create_question(
                question_text=f'Question {i}',
                answer=f'Answer {i}',
                category=cat.id,
                difficulty=1
            )
        
        # Try to create game requesting 5 questions from category with only 2
        response = self.client.post('/games',
                                   json={
                                       'user_id': user.id,
                                       'category_id': cat.id,
                                       'number_of_questions': 5
                                   },
                                   content_type='application/json')
        self.assert_error_schema(response, 422, 'Insufficient')
    
    # ==================== 409 Conflict Tests ====================
    
    def test_error_409_session_inconsistency_missing_answer_record(self):
        """Test 409 error when game session state is inconsistent (missing answer record)."""
        from services import UserService, CategoryService, QuestionService, GameSessionService
        
        # Setup: Create a user, category, questions, and game session
        user = UserService.create_user('testuser')
        cat = CategoryService.create_category('Test Category')
        
        questions = []
        for i in range(3):
            q = QuestionService.create_question(
                question_text=f'Question {i}',
                answer=f'Answer {i}',
                category=cat.id,
                difficulty=1
            )
            questions.append(q)
        
        # Create a game session with 3 questions (score=0 initially)
        game_session = GameSessionService.create_game_session(
            user_id=user.id,
            score=0,
            category_id=cat.id,
            number_of_questions=3
        )
        
        # Manually delete the answer records to simulate corruption/inconsistency
        from data_access import db
        from models.game_session_answer import GameSessionAnswer
        GameSessionAnswer.query.filter_by(game_session_id=game_session.id).delete()
        db.session.commit()
        
        # Now try to submit an answer - this should fail with 409 Conflict
        # because the audit trail entry should exist (was pre-created at game start)
        response = self.client.post(f'/games/{game_session.id}/1',
                                   json={'user_answer': 'Answer 0'},
                                   content_type='application/json')
        self.assert_error_schema(response, 409, 'conflict')
    
    # ==================== 500 Internal Server Error Tests ====================
    
    def test_error_500_returns_correct_schema(self):
        """Test 500 error returns standardized schema via forced controller failure."""
        with patch('controllers.categories.CategoryService.get_all_categories_list', side_effect=Exception('forced failure')):
            response = self.client.get('/categories')
            self.assert_error_schema(response, 500, 'Internal server error')


class SuccessResponseSchemaTests(unittest.TestCase):
    """Test that success responses include 'success' field."""
    
    def setUp(self):
        """Set up test client and database."""
        self.app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        with self.app.app_context():
            db.create_all()
        
        self.client = self.app.test_client()
    
    def tearDown(self):
        """Clean up after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        
        self.app_context.pop()
    
    def test_success_200_get_categories(self):
        """Test 200 success response for GET /categories."""
        response = self.client.get('/categories')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertNotIn('error', data)  # Error field should not be in success responses
    
    def test_success_201_create_user(self):
        """Test 201 success response for POST /users."""
        response = self.client.post('/users',
                                   json={'username': 'testuser'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        
        # Check that required user fields are present
        self.assertIn('id', data)
        self.assertIn('username', data)
        self.assertEqual(data['username'], 'testuser')
        
        # Check that error fields are NOT present
        self.assertNotIn('error', data)
    
    def test_success_200_get_leaderboard(self):
        """Test 200 success response for GET /users/leaderboard."""
        response = self.client.get('/users/leaderboard')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('success', data)
        self.assertTrue(data['success'])
        self.assertNotIn('error', data)


if __name__ == '__main__':
    unittest.main()
