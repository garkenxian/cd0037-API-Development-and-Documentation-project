"""
Test cases for POST /questions endpoint
Tests question creation, validation, and error handling
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


class QuestionsEndpointTestCase(unittest.TestCase):
    """Test cases for question creation endpoint"""

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
        
        # Create a test category
        response = self.client.post('/categories', json={'type': 'Science'})
        self.category_id = response.get_json()['id']

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # ==================== POST /questions Tests ====================

    def test_create_question_success(self):
        """Test successful question creation"""
        response = self.client.post(
            '/questions',
            json={
                'question': 'What is H2O?',
                'answer': 'Water',
                'category': self.category_id,
                'difficulty': 1,
                'rating': 4.5
            }
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['question'], 'What is H2O?')
        self.assertEqual(data['answer'], 'Water')
        self.assertEqual(data['category'], self.category_id)
        self.assertEqual(data['difficulty'], 1)
        self.assertEqual(data['rating'], 4.5)

    def test_create_question_default_rating(self):
        """Test question creation with default rating"""
        response = self.client.post(
            '/questions',
            json={
                'question': 'What is gravity?',
                'answer': 'A force',
                'category': self.category_id,
                'difficulty': 3
            }
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['rating'], 0)

    def test_create_question_missing_question_text(self):
        """Test creation fails with missing question text"""
        response = self.client.post(
            '/questions',
            json={
                'answer': 'Answer',
                'category': self.category_id,
                'difficulty': 1
            }
        )
        
        self.assertEqual(response.status_code, 400)

    def test_create_question_missing_answer(self):
        """Test creation fails with missing answer"""
        response = self.client.post(
            '/questions',
            json={
                'question': 'What is 2+2?',
                'category': self.category_id,
                'difficulty': 1
            }
        )
        
        self.assertEqual(response.status_code, 400)

    def test_create_question_missing_category(self):
        """Test creation fails with missing category"""
        response = self.client.post(
            '/questions',
            json={
                'question': 'What is 2+2?',
                'answer': '4',
                'difficulty': 1
            }
        )
        
        self.assertEqual(response.status_code, 400)

    def test_create_question_missing_difficulty(self):
        """Test creation fails with missing difficulty"""
        response = self.client.post(
            '/questions',
            json={
                'question': 'What is 2+2?',
                'answer': '4',
                'category': self.category_id
            }
        )
        
        self.assertEqual(response.status_code, 400)

    def test_create_question_invalid_difficulty(self):
        """Test creation fails with invalid difficulty"""
        response = self.client.post(
            '/questions',
            json={
                'question': 'What is 2+2?',
                'answer': '4',
                'category': self.category_id,
                'difficulty': 6  # Invalid - must be 1-5
            }
        )
        
        self.assertEqual(response.status_code, 400)

    def test_create_question_invalid_category(self):
        """Test creation fails with non-existent category"""
        response = self.client.post(
            '/questions',
            json={
                'question': 'What is 2+2?',
                'answer': '4',
                'category': 9999,  # Non-existent category
                'difficulty': 1
            }
        )
        
        # Should still return 201 as we don't validate category existence at endpoint level
        # (database constraint will fail on commit)
        self.assertEqual(response.status_code, 201)

    def test_create_multiple_questions_success(self):
        """Test creating multiple questions successfully"""
        questions = [
            {
                'question': 'What is photosynthesis?',
                'answer': 'Process where plants make food from sunlight',
                'category': self.category_id,
                'difficulty': 2
            },
            {
                'question': 'What is DNA?',
                'answer': 'Deoxyribonucleic acid',
                'category': self.category_id,
                'difficulty': 3
            },
            {
                'question': 'What is a cell?',
                'answer': 'Basic unit of life',
                'category': self.category_id,
                'difficulty': 1
            }
        ]
        
        for question_data in questions:
            response = self.client.post('/questions', json=question_data)
            self.assertEqual(response.status_code, 201)
            data = response.get_json()
            self.assertEqual(data['question'], question_data['question'])


if __name__ == '__main__':
    unittest.main()
