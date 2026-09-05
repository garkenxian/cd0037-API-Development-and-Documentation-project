"""Tests for exception and error handling coverage"""

import unittest
from unittest.mock import patch, MagicMock
from flaskr import create_app
from data_access import db
from data_access.category_repository import CategoryRepository
from data_access.question_repository import QuestionRepository
from data_access.user_repository import UserRepository


class CategoriesExceptionHandlingTests(unittest.TestCase):
    """Test exception handling in categories controller"""

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

    def test_get_categories_success(self):
        """Test successful GET /categories"""
        # Create some categories
        CategoryRepository.create('Science')
        CategoryRepository.create('History')
        db.session.commit()
        
        response = self.client.get('/categories')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('categories', data)

    def test_create_category_success(self):
        """Test successful POST /categories"""
        response = self.client.post('/categories', json={'type': 'Science'})
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['type'], 'Science')

    def test_create_category_duplicate(self):
        """Test POST /categories with duplicate type"""
        # Create first category
        self.client.post('/categories', json={'type': 'Science'})
        
        # Try to create duplicate
        response = self.client.post('/categories', json={'type': 'Science'})
        # Should fail with 422 or 400
        self.assertIn(response.status_code, [400, 422])

    def test_update_category_success(self):
        """Test successful PUT /categories/<id>"""
        cat = CategoryRepository.create('Science')
        db.session.commit()
        
        response = self.client.put(f'/categories/{cat.id}', json={'type': 'Biology'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['type'], 'Biology')

    def test_delete_category_success(self):
        """Test successful DELETE /categories/<id>"""
        cat = CategoryRepository.create('Science')
        db.session.commit()
        
        response = self.client.delete(f'/categories/{cat.id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], cat.id)

    def test_delete_category_with_questions(self):
        """Test DELETE /categories/<id> fails when has questions"""
        cat = CategoryRepository.create('Science')
        db.session.flush()
        
        # Add question
        QuestionRepository.create('Q1?', 'A1', cat.id, 'easy')
        db.session.commit()
        
        response = self.client.delete(f'/categories/{cat.id}')
        # Should fail - cannot delete
        self.assertIn(response.status_code, [400, 422, 500])

    def test_get_category_success(self):
        """Test GET /categories/<id>"""
        cat = CategoryRepository.create('Science')
        db.session.commit()
        
        response = self.client.get(f'/categories/{cat.id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], cat.id)
        self.assertEqual(data['type'], 'Science')


class QuestionsExceptionHandlingTests(unittest.TestCase):
    """Test exception handling in questions controller"""

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
        
        # Create test category
        self.cat = CategoryRepository.create('Test')
        db.session.commit()

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        self.app_context.pop()

    def test_create_question_missing_field(self):
        """Test POST /questions with missing required field"""
        response = self.client.post('/questions', json={
            'question': 'Q1?',
            'category': self.cat.id
        })
        self.assertEqual(response.status_code, 400)

    def test_get_questions_success(self):
        """Test GET /questions"""
        # Create some questions
        for i in range(3):
            QuestionRepository.create(f'Q{i}?', f'A{i}', self.cat.id, 'easy')
        db.session.commit()
        
        response = self.client.get('/questions')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('questions', data)
        self.assertGreaterEqual(len(data['questions']), 3)

    def test_get_question_success(self):
        """Test GET /questions/<id>"""
        q = QuestionRepository.create('Q1?', 'A1', self.cat.id, 'easy')
        db.session.commit()
        
        response = self.client.get(f'/questions/{q.id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], q.id)

    def test_delete_question_success(self):
        """Test DELETE /questions/<id>"""
        q = QuestionRepository.create('Q1?', 'A1', self.cat.id, 'easy')
        db.session.commit()
        
        response = self.client.delete(f'/questions/{q.id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])


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

    def test_create_user_success(self):
        """Test successful POST /users"""
        response = self.client.post('/users', json={'username': 'testuser'})
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['username'], 'testuser')

    def test_create_user_with_email(self):
        """Test POST /users with email"""
        response = self.client.post('/users', json={
            'username': 'testuser',
            'email': 'test@test.com'
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['email'], 'test@test.com')

    def test_create_user_duplicate(self):
        """Test POST /users with duplicate username"""
        self.client.post('/users', json={'username': 'testuser'})
        
        response = self.client.post('/users', json={'username': 'testuser'})
        self.assertEqual(response.status_code, 422)

    def test_get_users_success(self):
        """Test GET /users"""
        for i in range(3):
            self.client.post('/users', json={'username': f'user{i}'})
        
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('users', data)
        self.assertEqual(len(data['users']), 3)


    def test_get_users_valid_sort_by_score(self):
        """Test GET /users with sort_by=total_score"""
        for i in range(2):
            self.client.post('/users', json={'username': f'user{i}'})
        
        response = self.client.get('/users?sort_by=total_score&order=desc')
        self.assertEqual(response.status_code, 200)

    def test_get_users_valid_sort_by_games(self):
        """Test GET /users with sort_by=games_played"""
        response = self.client.get('/users?sort_by=games_played')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
