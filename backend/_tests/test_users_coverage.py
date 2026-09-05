"""Comprehensive tests for users controller to reach 80% coverage"""

import unittest
from unittest.mock import patch
from flaskr import create_app
from data_access import db
from data_access.user_repository import UserRepository
from data_access.category_repository import CategoryRepository


class UsersLeaderboardTests(unittest.TestCase):
    """Test leaderboard endpoint"""

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

    def test_leaderboard_default_parameters(self):
        """Test leaderboard with default parameters"""
        # Create some users
        for i in range(15):
            self.client.post('/users', json={'username': f'user{i}'})
        
        response = self.client.get('/users/leaderboard')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('leaderboard', data)
        self.assertLessEqual(len(data['leaderboard']), 10)  # Default limit is 10
        self.assertIn('total_users', data)

    def test_leaderboard_with_limit(self):
        """Test leaderboard with custom limit"""
        for i in range(20):
            self.client.post('/users', json={'username': f'user{i}'})
        
        response = self.client.get('/users/leaderboard?limit=5')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['leaderboard']), 5)

    def test_leaderboard_with_offset(self):
        """Test leaderboard with offset for pagination"""
        for i in range(20):
            self.client.post('/users', json={'username': f'user{i}'})
        
        response = self.client.get('/users/leaderboard?limit=5&offset=5')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['leaderboard']), 5)
        # First item should have rank 6 (offset+1)
        self.assertEqual(data['leaderboard'][0]['rank'], 6)

    def test_leaderboard_ranking(self):
        """Test that leaderboard has correct ranking"""
        for i in range(5):
            self.client.post('/users', json={'username': f'user{i}'})
        
        response = self.client.get('/users/leaderboard?limit=10')
        data = response.get_json()
        
        # Verify ranks are sequential
        for idx, entry in enumerate(data['leaderboard'], start=1):
            self.assertEqual(entry['rank'], idx)
            self.assertIn('id', entry)
            self.assertIn('username', entry)
            self.assertIn('total_score', entry)
            self.assertIn('games_played', entry)

    def test_leaderboard_invalid_limit(self):
        """Test leaderboard with invalid limit"""
        response = self.client.get('/users/leaderboard?limit=0')
        self.assertEqual(response.status_code, 400)

    def test_leaderboard_negative_limit(self):
        """Test leaderboard with negative limit"""
        response = self.client.get('/users/leaderboard?limit=-1')
        self.assertEqual(response.status_code, 400)

    def test_leaderboard_negative_offset(self):
        """Test leaderboard with negative offset"""
        response = self.client.get('/users/leaderboard?offset=-1')
        self.assertEqual(response.status_code, 400)

    def test_leaderboard_empty_database(self):
        """Test leaderboard with no users"""
        response = self.client.get('/users/leaderboard')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['leaderboard']), 0)
        self.assertEqual(data['total_users'], 0)

    def test_leaderboard_large_limit(self):
        """Test leaderboard with large limit"""
        for i in range(5):
            self.client.post('/users', json={'username': f'user{i}'})
        
        response = self.client.get('/users/leaderboard?limit=100')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['leaderboard']), 5)


class UsersParameterValidationTests(unittest.TestCase):
    """Test parameter validation for users endpoints"""

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

    def test_get_users_invalid_sort_parameter(self):
        """Test GET /users with invalid sort parameter"""
        response = self.client.get('/users?sort=invalid_sort')
        self.assertEqual(response.status_code, 400)

    def test_get_users_invalid_order_parameter(self):
        """Test GET /users with invalid order parameter"""
        response = self.client.get('/users?order=invalid_order')
        self.assertEqual(response.status_code, 400)

    def test_get_users_both_parameters_invalid(self):
        """Test GET /users with both invalid parameters"""
        response = self.client.get('/users?sort=invalid&order=invalid')
        self.assertEqual(response.status_code, 400)

    def test_get_users_valid_sort_parameters(self):
        """Test GET /users with all valid sort parameters"""
        for i in range(3):
            self.client.post('/users', json={'username': f'user{i}'})
        
        for sort_param in ['created_at', 'total_score', 'games_played']:
            response = self.client.get(f'/users?sort={sort_param}')
            self.assertEqual(response.status_code, 200)

    def test_get_users_valid_order_parameters(self):
        """Test GET /users with all valid order parameters"""
        for i in range(3):
            self.client.post('/users', json={'username': f'user{i}'})
        
        for order_param in ['asc', 'desc']:
            response = self.client.get(f'/users?order={order_param}')
            self.assertEqual(response.status_code, 200)

    def test_get_users_default_sort_and_order(self):
        """Test GET /users uses defaults when parameters omitted"""
        for i in range(3):
            self.client.post('/users', json={'username': f'user{i}'})
        
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['users']), 3)

    def test_create_user_no_json_body(self):
        """Test POST /users with no JSON body"""
        response = self.client.post('/users', json={})
        self.assertEqual(response.status_code, 400)

    def test_create_user_null_username(self):
        """Test POST /users with null username"""
        response = self.client.post('/users', json={'username': None})
        self.assertEqual(response.status_code, 400)

    def test_create_user_empty_string_username(self):
        """Test POST /users with empty string username"""
        response = self.client.post('/users', json={'username': ''})
        self.assertEqual(response.status_code, 400)

    def test_get_user_not_found(self):
        """Test GET /users/<id> with nonexistent user"""
        response = self.client.get('/users/99999')
        self.assertEqual(response.status_code, 404)

    def test_get_user_success(self):
        """Test GET /users/<id> with valid user"""
        create_response = self.client.post('/users', json={'username': 'testuser'})
        user_id = create_response.get_json()['id']
        
        response = self.client.get(f'/users/{user_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['id'], user_id)
        self.assertEqual(data['username'], 'testuser')


class UsersExceptionHandlingTests(unittest.TestCase):
    """Test exception handling in users controller"""

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

    @patch('controllers.users.UserService.get_all_users')
    def test_get_users_service_exception(self, mock_service):
        """Test GET /users when service raises exception"""
        mock_service.side_effect = Exception("Database error")
        
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 500)

    @patch('controllers.users.UserService.get_user')
    def test_get_user_service_exception(self, mock_service):
        """Test GET /users/<id> when service raises exception"""
        mock_service.side_effect = Exception("Database error")
        
        response = self.client.get('/users/1')
        self.assertEqual(response.status_code, 500)

    @patch('controllers.users.UserService.create_user')
    def test_create_user_service_exception(self, mock_service):
        """Test POST /users when service raises exception"""
        mock_service.side_effect = Exception("Database error")
        
        response = self.client.post('/users', json={'username': 'testuser'})
        self.assertEqual(response.status_code, 500)

    @patch('controllers.users.UserService.get_leaderboard')
    def test_get_leaderboard_service_exception(self, mock_service):
        """Test leaderboard when service raises exception"""
        mock_service.side_effect = Exception("Database error")
        
        response = self.client.get('/users/leaderboard')
        self.assertEqual(response.status_code, 500)


if __name__ == '__main__':
    unittest.main()
