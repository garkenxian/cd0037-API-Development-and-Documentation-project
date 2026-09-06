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

    def _create_category(self, category_type='Science'):
        """Helper to create a category and return its ID."""
        response = self.client.post('/categories', json={'type': category_type})
        self.assertEqual(response.status_code, 201)
        return response.get_json()['id']

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

    # ==================== GET /categories Tests ====================

    def test_get_categories_success(self):
        """Test listing categories returns success payload."""
        self._create_category('Science')
        self._create_category('History')

        response = self.client.get('/categories')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('categories', data)
        self.assertGreaterEqual(len(data['categories']), 2)

    def test_get_category_by_id_success(self):
        """Test retrieving an existing category by id."""
        category_id = self._create_category('Art')

        response = self.client.get(f'/categories/{category_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], category_id)
        self.assertEqual(data['type'], 'Art')

    def test_get_category_by_id_not_found(self):
        """Test retrieving non-existent category returns 404."""
        response = self.client.get('/categories/9999')
        self.assertEqual(response.status_code, 404)

    # ==================== PUT /categories/<id> Tests ====================

    def test_update_category_success(self):
        """Test updating an existing category."""
        category_id = self._create_category('Entertainment')

        response = self.client.put(f'/categories/{category_id}', json={'type': 'Movies'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], category_id)
        self.assertEqual(data['type'], 'Movies')

    def test_update_category_not_found(self):
        """Test updating non-existent category returns 404."""
        response = self.client.put('/categories/9999', json={'type': 'Anything'})
        self.assertEqual(response.status_code, 404)

    def test_update_category_duplicate_type(self):
        """Test updating category to duplicate type returns 422."""
        self._create_category('Geography')
        category_id = self._create_category('Space')

        response = self.client.put(f'/categories/{category_id}', json={'type': 'Geography'})
        self.assertEqual(response.status_code, 422)

    # ==================== DELETE /categories/<id> Tests ====================

    def test_delete_category_success_when_no_questions(self):
        """Test deleting category with no linked questions succeeds."""
        category_id = self._create_category('ToDelete')

        response = self.client.delete(f'/categories/{category_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['deleted'], category_id)
        self.assertTrue(data['success'])

    def test_delete_category_not_found(self):
        """Test deleting missing category returns 404."""
        response = self.client.delete('/categories/9999')
        self.assertEqual(response.status_code, 404)

    def test_delete_category_with_questions_returns_422(self):
        """Test deleting category with linked questions returns 422."""
        category_id = self._create_category('Protected')
        question_response = self.client.post('/questions', json={
            'question': 'What is H2O?',
            'answer': 'Water',
            'category': category_id,
            'difficulty': 1,
        })
        self.assertEqual(question_response.status_code, 201)

        response = self.client.delete(f'/categories/{category_id}')
        self.assertEqual(response.status_code, 422)

    # ==================== GET /categories/<id>/questions Tests ====================

    def test_get_category_questions_success(self):
        """Test category questions endpoint returns paginated results."""
        category_id = self._create_category('Science')
        for i in range(3):
            response = self.client.post('/questions', json={
                'question': f'Science question {i}',
                'answer': f'Answer {i}',
                'category': category_id,
                'difficulty': 1,
            })
            self.assertEqual(response.status_code, 201)

        response = self.client.get(f'/categories/{category_id}/questions?page=1')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['current_category'], 'Science')
        self.assertEqual(data['total_questions'], 3)
        self.assertEqual(len(data['questions']), 3)

    def test_get_category_questions_not_found(self):
        """Test category questions endpoint returns 404 for invalid category."""
        response = self.client.get('/categories/9999/questions')
        self.assertEqual(response.status_code, 404)

    def test_get_category_questions_invalid_page(self):
        """Test category questions endpoint rejects page < 1."""
        category_id = self._create_category('Math')
        response = self.client.get(f'/categories/{category_id}/questions?page=0')
        self.assertEqual(response.status_code, 400)

    def test_get_category_questions_page_out_of_range(self):
        """Test category questions endpoint returns 404 for page out of range."""
        category_id = self._create_category('History')
        response = self.client.post('/questions', json={
            'question': 'History question',
            'answer': 'History answer',
            'category': category_id,
            'difficulty': 1,
        })
        self.assertEqual(response.status_code, 201)

        out_of_range = self.client.get(f'/categories/{category_id}/questions?page=2')
        self.assertEqual(out_of_range.status_code, 404)

    def test_get_category_questions_empty_returns_200(self):
        """Test category questions endpoint returns 200 with empty questions list."""
        category_id = self._create_category('EmptyCategory')
        response = self.client.get(f'/categories/{category_id}/questions?page=1')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(data['questions'], [])


if __name__ == '__main__':
    unittest.main()
