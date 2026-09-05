"""
Additional endpoint tests to increase coverage
Tests for GET, PUT, DELETE operations that aren't fully covered
"""

import os
import sys
import unittest
from dotenv import load_dotenv

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flaskr import create_app
from data_access import db, UserRepository, CategoryRepository, QuestionRepository

# Load environment variables
load_dotenv()


class CategoriesAdditionalTestCase(unittest.TestCase):
    """Additional tests for categories endpoints"""

    def setUp(self):
        """Set up test database and app context"""
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
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_single_category(self):
        """Test GET /categories/<id>"""
        # Create via API
        response = self.client.post('/categories', json={'type': 'Science'})
        cat_id = response.get_json()['id']
        
        # Get the category
        response = self.client.get(f'/categories/{cat_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['type'], 'Science')
        self.assertEqual(data['id'], cat_id)

    def test_get_nonexistent_category(self):
        """Test GET /categories/<id> with invalid ID"""
        response = self.client.get('/categories/999')
        self.assertEqual(response.status_code, 404)

    def test_update_category(self):
        """Test PUT /categories/<id>"""
        # Create via API
        response = self.client.post('/categories', json={'type': 'Old Name'})
        cat_id = response.get_json()['id']
        
        # Update it
        response = self.client.put(
            f'/categories/{cat_id}',
            json={'type': 'New Name'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['type'], 'New Name')

    def test_update_nonexistent_category(self):
        """Test PUT /categories/<id> with invalid ID"""
        response = self.client.put(
            '/categories/999',
            json={'type': 'New Name'}
        )
        self.assertEqual(response.status_code, 404)

    def test_update_category_bad_request(self):
        """Test PUT /categories/<id> with missing type"""
        response = self.client.post('/categories', json={'type': 'Test'})
        cat_id = response.get_json()['id']
        
        response = self.client.put(
            f'/categories/{cat_id}',
            json={}
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_category(self):
        """Test DELETE /categories/<id>"""
        response = self.client.post('/categories', json={'type': 'To Delete'})
        cat_id = response.get_json()['id']
        
        response = self.client.delete(f'/categories/{cat_id}')
        self.assertEqual(response.status_code, 200)

    def test_delete_nonexistent_category(self):
        """Test DELETE /categories/<id> with invalid ID"""
        response = self.client.delete('/categories/999')
        self.assertEqual(response.status_code, 404)


class QuestionsAdditionalTestCase(unittest.TestCase):
    """Additional tests for questions endpoints"""

    def setUp(self):
        """Set up test database and app context"""
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
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_all_questions(self):
        """Test GET /questions"""
        # Create category and questions via API
        cat_response = self.client.post('/categories', json={'type': 'Science'})
        cat_id = cat_response.get_json()['id']
        
        for i in range(3):
            self.client.post('/questions', json={
                'question': f'Q{i}?',
                'answer': f'A{i}',
                'category': cat_id,
                'difficulty': 1
            })
        
        # Get all questions
        response = self.client.get('/questions')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('questions', data)
        self.assertGreaterEqual(len(data['questions']), 3)

    def test_get_question_by_id(self):
        """Test GET /questions/<id>"""
        # Create category and question
        cat_response = self.client.post('/categories', json={'type': 'Science'})
        cat_id = cat_response.get_json()['id']
        
        q_response = self.client.post('/questions', json={
            'question': 'Test Question?',
            'answer': 'Test Answer',
            'category': cat_id,
            'difficulty': 2
        })
        q_id = q_response.get_json()['id']
        
        # Get it
        response = self.client.get(f'/questions/{q_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['question'], 'Test Question?')
        self.assertEqual(data['answer'], 'Test Answer')

    def test_get_nonexistent_question(self):
        """Test GET /questions/<id> with invalid ID"""
        response = self.client.get('/questions/999')
        self.assertEqual(response.status_code, 404)

    def test_delete_question(self):
        """Test DELETE /questions/<id>"""
        # Create category and question
        cat_response = self.client.post('/categories', json={'type': 'Science'})
        cat_id = cat_response.get_json()['id']
        
        q_response = self.client.post('/questions', json={
            'question': 'Test Q?',
            'answer': 'Test A',
            'category': cat_id,
            'difficulty': 1
        })
        q_id = q_response.get_json()['id']
        
        # Delete it
        response = self.client.delete(f'/questions/{q_id}')
        self.assertEqual(response.status_code, 200)
        
        # Verify it's gone
        response = self.client.get(f'/questions/{q_id}')
        self.assertEqual(response.status_code, 404)

    def test_delete_nonexistent_question(self):
        """Test DELETE /questions/<id> with invalid ID"""
        response = self.client.delete('/questions/999')
        self.assertEqual(response.status_code, 404)


class UsersAdditionalTestCase(unittest.TestCase):
    """Additional tests for users endpoints"""

    def setUp(self):
        """Set up test database and app context"""
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
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_all_users(self):
        """Test GET /users"""
        # Create some users
        for i in range(3):
            self.client.post('/users', json={'username': f'user{i}'})
        
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('users', data)
        self.assertEqual(len(data['users']), 3)

    def test_get_users_sorting(self):
        """Test GET /users with sorting"""
        # Create users
        self.client.post('/users', json={'username': 'alice'})
        self.client.post('/users', json={'username': 'bob'})
        
        # Test default sort (by created_at asc)
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        
        # Test sort by username (doesn't exist but should not crash)
        response = self.client.get('/users?sort=created_at&order=desc')
        self.assertEqual(response.status_code, 200)

    def test_get_user_by_id(self):
        """Test GET /users/<id>"""
        # Create a user
        u_response = self.client.post('/users', json={'username': 'testuser'})
        u_id = u_response.get_json()['id']
        
        # Get it
        response = self.client.get(f'/users/{u_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['username'], 'testuser')
        self.assertIn('game_sessions', data)

    def test_get_nonexistent_user(self):
        """Test GET /users/<id> with invalid ID"""
        response = self.client.get('/users/999')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
