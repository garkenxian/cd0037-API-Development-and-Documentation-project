"""
Test cases for edge paths and exception handling in controllers
Tests error paths and edge cases for robustness
"""

import os
import sys
import unittest
from dotenv import load_dotenv

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flaskr import create_app
from data_access import db
from models import Category, Question, User

# Load environment variables
load_dotenv()


class EdgePathExceptionTestCase(unittest.TestCase):
    """Test exception handling and edge paths in controllers"""

    def setUp(self):
        """Set up test database and app context"""
        self.database_path = "sqlite:///:memory:"
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        # Push app context and keep it for the test
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create tables
        db.create_all()

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # ==================== Categories Edge Paths ====================

    def test_get_category_questions_invalid_page_type(self):
        """Test get category questions with invalid page parameter type (defaults to 1)"""
        # Create a category
        category = Category(type='Science')
        db.session.add(category)
        db.session.commit()
        
        # Try to fetch with non-integer page (should default to 1)
        response = self.client.get(f'/categories/{category.id}/questions?page=abc')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])

    def test_get_category_questions_negative_page(self):
        """Test get category questions with negative page number"""
        category = Category(type='Math')
        db.session.add(category)
        db.session.commit()
        
        response = self.client.get(f'/categories/{category.id}/questions?page=-1')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['error'], 400)
        self.assertIn('1', data['message'])

    def test_get_category_questions_page_out_of_range_empty_category(self):
        """Test get category questions with page 999 - empty category should return 404 for out-of-range page"""
        category = Category(type='History')
        db.session.add(category)
        db.session.commit()
        
        # Page 999 on empty category returns 404 (page out of range)
        response = self.client.get(f'/categories/{category.id}/questions?page=999')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], 404)

    def test_get_category_questions_page_out_of_range_with_questions(self):
        """Test get category questions with page 999 when category HAS questions (should return 404)"""
        # Create category via API
        cat_resp = self.client.post('/categories', json={'type': 'Geography'})
        category_id = cat_resp.get_json()['id']
        
        # Create a question via API
        self.client.post('/questions', json={
            'question': 'What is the capital of France?',
            'answer': 'Paris',
            'category': category_id,
            'difficulty': 1
        })
        
        # Category WITH questions and page out of range should return 404
        response = self.client.get(f'/categories/{category_id}/questions?page=999')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], 404)
        self.assertFalse(data['success'])

    def test_update_category_constraint_violation(self):
        """Test update category with duplicate type (constraint violation)"""
        # Create two categories
        cat1 = Category(type='Science')
        cat2 = Category(type='History')
        db.session.add(cat1)
        db.session.add(cat2)
        db.session.commit()
        
        # Try to update cat2 to have same type as cat1 (constraint violation)
        response = self.client.put(
            f'/categories/{cat2.id}',
            json={'type': 'Science'}
        )
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertEqual(data['error'], 422)
        self.assertFalse(data['success'])

    def test_delete_category_not_found(self):
        """Test delete non-existent category"""
        response = self.client.delete('/categories/99999')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], 404)

    # ==================== Questions Edge Paths ====================

    def test_get_questions_invalid_page_type(self):
        """Test get questions with invalid page parameter type (defaults to 1)"""
        response = self.client.get('/questions?page=invalid')
        # Invalid page parameter defaults to page 1
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])

    def test_get_questions_negative_page(self):
        """Test get questions with negative page number"""
        response = self.client.get('/questions?page=-5')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['error'], 400)
        self.assertIn('1', data['message'])

    def test_get_questions_page_out_of_range_empty_db(self):
        """Test get all questions with page 999 when NO questions exist (should return 404 for out-of-range)"""
        response = self.client.get('/questions?page=999')
        # Page 999 is out of range, even for empty list
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], 404)

    def test_get_questions_page_out_of_range_with_questions(self):
        """Test get all questions with page 999 when questions DO exist (should return 404)"""
        # Create category and question via API
        cat_resp = self.client.post('/categories', json={'type': 'Science'})
        category_id = cat_resp.get_json()['id']
        
        self.client.post('/questions', json={
            'question': 'What is the capital of France?',
            'answer': 'Paris',
            'category': category_id,
            'difficulty': 1
        })
        
        # Now with questions present, page 999 should return 404
        response = self.client.get('/questions?page=999')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], 404)
        self.assertFalse(data['success'])

    def test_get_nonexistent_question(self):
        """Test get question that doesn't exist"""
        response = self.client.get('/questions/99999')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], 404)
        self.assertIn('not found', data['message'].lower())

    def test_delete_nonexistent_question(self):
        """Test delete question that doesn't exist"""
        response = self.client.delete('/questions/99999')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], 404)

    # ==================== Games Edge Paths ====================

    def test_create_game_no_questions_available(self):
        """Test create game when no questions are available"""
        # Create user but no questions
        user = User(username='testplayer', email='testplayer@test.com')
        db.session.add(user)
        db.session.commit()
        
        # Try to create game
        response = self.client.post('/games', json={
            'user_id': user.id,
            'category_id': 0,
            'number_of_questions': 5
        })
        # Should fail with 422 because no questions available
        self.assertEqual(response.status_code, 422)
        data = response.get_json()
        self.assertEqual(data['error'], 422)

    def test_create_game_no_questions_in_category(self):
        """Test create game for category with no questions"""
        # Create user and category
        user = User(username='gamer1', email='gamer1@test.com')
        category = Category(type='Empty Category')
        db.session.add(user)
        db.session.add(category)
        db.session.commit()
        
        # Try to create game with category that has no questions
        response = self.client.post('/games', json={
            'user_id': user.id,
            'category_id': category.id,
            'number_of_questions': 5
        })
        self.assertEqual(response.status_code, 422)

    def test_answer_question_invalid_game_session(self):
        """Test answer submission for non-existent game"""
        response = self.client.post('/games/99999/1', json={
            'answer': 'some answer'
        })
        # Returns 400 for invalid game session
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['error'], 400)

    def test_create_game_invalid_user(self):
        """Test create game with non-existent user"""
        response = self.client.post('/games', json={
            'user_id': 99999,
            'category_id': 0,
            'number_of_questions': 5
        })
        self.assertEqual(response.status_code, 404)

    # ==================== Users Edge Paths ====================

    def test_get_nonexistent_user(self):
        """Test get user that doesn't exist"""
        response = self.client.get('/users/99999')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], 404)

    def test_create_user_duplicate_username(self):
        """Test create user with duplicate username"""
        # Create first user
        response1 = self.client.post('/users', json={
            'username': 'johndoe',
            'email': 'johndoe@test.com'
        })
        self.assertEqual(response1.status_code, 201)
        
        # Try to create second user with same username
        response2 = self.client.post('/users', json={
            'username': 'johndoe',
            'email': 'johndoe2@test.com'
        })
        self.assertEqual(response2.status_code, 422)
        data = response2.get_json()
        self.assertEqual(data['error'], 422)
        self.assertFalse(data['success'])

    def test_get_leaderboard_empty(self):
        """Test get leaderboard with no users"""
        response = self.client.get('/users/leaderboard')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['leaderboard']), 0)
        self.assertTrue(data['success'])


if __name__ == '__main__':
    unittest.main()
