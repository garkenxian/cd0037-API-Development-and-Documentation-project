"""Tests for users controller coverage improvement"""

import unittest
from flaskr import create_app
from data_access import db
from data_access.user_repository import UserRepository


class UsersControllerDetailedTests(unittest.TestCase):
    """Detailed tests for users controller endpoints"""

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

    def test_create_user_basic(self):
        """Test basic user creation"""
        response = self.client.post('/users', json={'username': 'alice'})
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['username'], 'alice')

    def test_create_user_with_email(self):
        """Test user creation with email"""
        response = self.client.post('/users', json={
            'username': 'alice',
            'email': 'alice@example.com'
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['email'], 'alice@example.com')

    def test_create_user_duplicate_fails(self):
        """Test duplicate username fails"""
        # Create first user
        self.client.post('/users', json={'username': 'alice'})
        
        # Try to create duplicate
        response = self.client.post('/users', json={'username': 'alice'})
        self.assertEqual(response.status_code, 422)

    def test_get_all_users(self):
        """Test getting all users"""
        # Create multiple users
        for i in range(5):
            self.client.post('/users', json={'username': f'user{i}'})
        
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['users']), 5)
        self.assertEqual(data['total_users'], 5)

    def test_get_all_users_sorted_by_created_at(self):
        """Test sorting by created_at (default)"""
        for i in range(3):
            self.client.post('/users', json={'username': f'user{i}'})
        
        response = self.client.get('/users?sort_by=created_at&order=asc')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['users']), 3)

    def test_get_all_users_sorted_by_score(self):
        """Test sorting by total_score"""
        for i in range(3):
            self.client.post('/users', json={'username': f'user{i}'})
        
        response = self.client.get('/users?sort_by=total_score&order=desc')
        self.assertEqual(response.status_code, 200)

    def test_get_all_users_sorted_by_games(self):
        """Test sorting by games_played"""
        for i in range(3):
            self.client.post('/users', json={'username': f'user{i}'})
        
        response = self.client.get('/users?sort_by=games_played&order=asc')
        self.assertEqual(response.status_code, 200)

    def test_get_user_by_id(self):
        """Test getting a specific user"""
        create_response = self.client.post('/users', json={'username': 'alice'})
        user_id = create_response.get_json()['id']
        
        response = self.client.get(f'/users/{user_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['username'], 'alice')
        self.assertTrue(data['success'])

    def test_get_user_with_game_sessions(self):
        """Test user details include game_sessions"""
        create_response = self.client.post('/users', json={'username': 'alice'})
        user_id = create_response.get_json()['id']
        
        response = self.client.get(f'/users/{user_id}')
        data = response.get_json()
        self.assertIn('game_sessions', data)
        self.assertIsInstance(data['game_sessions'], list)

    def test_get_user_not_found(self):
        """Test getting nonexistent user"""
        response = self.client.get('/users/999')
        self.assertEqual(response.status_code, 404)

    def test_get_users_empty_database(self):
        """Test getting users from empty database"""
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['users']), 0)

    def test_user_stats_initialization(self):
        """Test that user stats are initialized correctly"""
        response = self.client.post('/users', json={'username': 'alice'})
        data = response.get_json()
        self.assertEqual(data['total_score'], 0)
        self.assertEqual(data['games_played'], 0)

    def test_user_has_created_at_timestamp(self):
        """Test that user has created_at timestamp"""
        response = self.client.post('/users', json={'username': 'alice'})
        data = response.get_json()
        self.assertIn('created_at', data)
        self.assertIsNotNone(data['created_at'])

    def test_get_users_with_order_asc(self):
        """Test sorting with explicit asc order"""
        for i in range(3):
            self.client.post('/users', json={'username': f'user{i}'})
        
        response = self.client.get('/users?order=asc')
        self.assertEqual(response.status_code, 200)

    def test_get_users_with_order_desc(self):
        """Test sorting with desc order"""
        for i in range(3):
            self.client.post('/users', json={'username': f'user{i}'})
        
        response = self.client.get('/users?sort_by=total_score&order=desc')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
