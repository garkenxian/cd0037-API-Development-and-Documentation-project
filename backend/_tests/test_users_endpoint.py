"""
Test cases for POST /users endpoint
Tests user creation, validation, and error handling
"""

import os
import sys
import unittest
from dotenv import load_dotenv

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flaskr import create_app
from data_access import db

# Load environment variables
load_dotenv()


class UsersEndpointTestCase(unittest.TestCase):
    """Test cases for user creation endpoint"""

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

    # ==================== POST /users Tests ====================

    def test_create_user_success(self):
        """Test successful user creation"""
        response = self.client.post(
            '/users',
            json={'username': 'testuser', 'email': 'test@example.com'}
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['total_score'], 0)
        self.assertEqual(data['games_played'], 0)

    def test_create_user_missing_username(self):
        """Test creation fails with missing username"""
        response = self.client.post(
            '/users',
            json={'email': 'test@example.com'}
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)

    def test_create_user_missing_email(self):
        """Test creation succeeds with missing email (email now optional)"""
        response = self.client.post(
            '/users',
            json={'username': 'testuser'}
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['username'], 'testuser')
        self.assertIsNone(data.get('email'))

    def test_create_user_empty_request(self):
        """Test creation fails with empty request body"""
        response = self.client.post('/users', json={})
        self.assertEqual(response.status_code, 400)

    def test_create_user_short_username(self):
        """Test creation succeeds with short username (no length validation)"""
        response = self.client.post(
            '/users',
            json={'username': 'ab', 'email': 'test@example.com'}
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['username'], 'ab')

    def test_create_user_invalid_email(self):
        """Test creation succeeds with invalid email format (no email validation)"""
        response = self.client.post(
            '/users',
            json={'username': 'testuser', 'email': 'notanemail'}
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['email'], 'notanemail')

    def test_create_user_duplicate_username(self):
        """Test creation fails with duplicate username"""
        # Create first user
        response1 = self.client.post(
            '/users',
            json={'username': 'duplicate', 'email': 'email1@example.com'}
        )
        self.assertEqual(response1.status_code, 201)

        # Try to create second user with same username
        response2 = self.client.post(
            '/users',
            json={'username': 'duplicate', 'email': 'email2@example.com'}
        )
        self.assertEqual(response2.status_code, 422)
        data = response2.get_json()
        self.assertIn('error', data)

    def test_create_user_duplicate_email(self):
        """Test creation succeeds with duplicate email (no email uniqueness check)"""
        # Create first user
        response1 = self.client.post(
            '/users',
            json={'username': 'user1', 'email': 'duplicate@example.com'}
        )
        self.assertEqual(response1.status_code, 201)

        # Create second user with same email - should succeed since email not unique
        response2 = self.client.post(
            '/users',
            json={'username': 'user2', 'email': 'duplicate@example.com'}
        )
        self.assertEqual(response2.status_code, 201)

    def test_create_multiple_users_success(self):
        """Test creating multiple users successfully"""
        users = [
            {'username': 'alice', 'email': 'alice@example.com'},
            {'username': 'bob', 'email': 'bob@example.com'},
            {'username': 'charlie', 'email': 'charlie@example.com'},
        ]
        
        for user_data in users:
            response = self.client.post('/users', json=user_data)
            self.assertEqual(response.status_code, 201)
            data = response.get_json()
            self.assertEqual(data['username'], user_data['username'])


if __name__ == '__main__':
    unittest.main()
