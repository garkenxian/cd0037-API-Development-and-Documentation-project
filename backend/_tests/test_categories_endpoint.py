"""
Test cases for POST /categories endpoint
Tests category creation, validation, and error handling
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


class CategoriesEndpointTestCase(unittest.TestCase):
    """Test cases for category creation endpoint"""

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

    # ==================== POST /categories Tests ====================

    def test_create_category_success(self):
        """Test successful category creation"""
        response = self.client.post(
            '/categories',
            json={'type': 'Science'}
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['type'], 'Science')
        self.assertIn('id', data)

    def test_create_category_missing_type(self):
        """Test creation fails with missing type"""
        response = self.client.post(
            '/categories',
            json={}
        )
        
        self.assertEqual(response.status_code, 400)

    def test_create_category_null_type(self):
        """Test creation fails with null type"""
        response = self.client.post(
            '/categories',
            json={'type': None}
        )
        
        self.assertEqual(response.status_code, 400)

    def test_create_category_empty_request(self):
        """Test creation fails with empty request body"""
        response = self.client.post('/categories', json={})
        self.assertEqual(response.status_code, 400)

    def test_create_category_duplicate(self):
        """Test creation fails with duplicate category"""
        # Create first category
        response1 = self.client.post(
            '/categories',
            json={'type': 'History'}
        )
        self.assertEqual(response1.status_code, 201)

        # Try to create second category with same type
        response2 = self.client.post(
            '/categories',
            json={'type': 'History'}
        )
        self.assertEqual(response2.status_code, 422)

    def test_create_multiple_categories_success(self):
        """Test creating multiple categories successfully"""
        categories = [
            {'type': 'Science'},
            {'type': 'History'},
            {'type': 'Geography'},
            {'type': 'Sports'},
            {'type': 'Entertainment'},
        ]
        
        for category_data in categories:
            response = self.client.post('/categories', json=category_data)
            self.assertEqual(response.status_code, 201)
            data = response.get_json()
            self.assertEqual(data['type'], category_data['type'])


if __name__ == '__main__':
    unittest.main()
