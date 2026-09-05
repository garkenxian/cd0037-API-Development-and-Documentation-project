"""Additional tests for Questions controller to achieve 80%+ coverage"""

import unittest
from flaskr import create_app
from data_access import db
from services import CategoryService, QuestionService


class QuestionsControllerCoverageTests(unittest.TestCase):
    """Additional tests for questions controller coverage"""

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
        
        # Create test categories
        self.cat1 = CategoryService.create_category('Science')
        self.cat2 = CategoryService.create_category('History')
        db.session.commit()
        
        # Create test questions
        self.q1 = QuestionService.create_question('Q1?', 'Answer1', self.cat1.id, 1)
        self.q2 = QuestionService.create_question('Q2?', 'Answer2', self.cat2.id, 2)
        self.q3 = QuestionService.create_question('Search test Q3?', 'Answer3', self.cat1.id, 3)
        db.session.commit()

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        self.app_context.pop()

    # ==================== GET /questions Tests ====================

    def test_get_questions_all(self):
        """Test GET /questions returns all questions"""
        response = self.client.get('/questions')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['total_questions'], 3)
        self.assertEqual(data['current_page'], 1)
        self.assertIn('categories', data)
        self.assertEqual(len(data['questions']), 3)

    def test_get_questions_with_search(self):
        """Test GET /questions with search parameter"""
        response = self.client.get('/questions?search=Search')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['questions']), 1)
        self.assertEqual(data['questions'][0]['question'], 'Search test Q3?')

    def test_get_questions_with_search_no_results(self):
        """Test GET /questions with search that has no results"""
        response = self.client.get('/questions?search=NonExistentQuery')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['total_questions'], 0)
    def test_get_questions_multiple_pages(self):
        """Test GET /questions returns categories dict"""
        response = self.client.get('/questions?page=1')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('categories', data)
        self.assertTrue(isinstance(data['categories'], dict))
        # Check that category IDs are strings
        for cat_id, cat_type in data['categories'].items():
            self.assertTrue(isinstance(cat_id, str))

    def test_get_questions_with_search_no_results(self):
        """Test GET /questions with search that has no results"""
        response = self.client.get('/questions?search=NonExistentQuery')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['total_questions'], 0)

    def test_get_single_question(self):
        """Test GET /questions/<id> returns single question"""
        response = self.client.get(f'/questions/{self.q1.id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['question'], 'Q1?')
        self.assertEqual(data['answer'], 'Answer1')

    def test_get_single_question_not_found(self):
        """Test GET /questions/<id> with non-existent ID"""
        response = self.client.get('/questions/99999')
        self.assertEqual(response.status_code, 404)

    # ==================== POST /questions Tests ====================

    def test_create_question_success(self):
        """Test successful question creation"""
        response = self.client.post(
            '/questions',
            json={
                'question': 'New Q?',
                'answer': 'New Answer',
                'category': self.cat1.id,
                'difficulty': 2
            }
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['question'], 'New Q?')

    def test_create_question_no_json_body(self):
        """Test POST /questions with no JSON body"""
        response = self.client.post('/questions', json={})
        self.assertEqual(response.status_code, 400)

    def test_create_question_missing_question(self):
        """Test POST /questions missing question field"""
        response = self.client.post(
            '/questions',
            json={
                'answer': 'Answer',
                'category': self.cat1.id,
                'difficulty': 1
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_create_question_missing_answer(self):
        """Test POST /questions missing answer field"""
        response = self.client.post(
            '/questions',
            json={
                'question': 'Q?',
                'category': self.cat1.id,
                'difficulty': 1
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_create_question_missing_category(self):
        """Test POST /questions missing category field"""
        response = self.client.post(
            '/questions',
            json={
                'question': 'Q?',
                'answer': 'Answer',
                'difficulty': 1
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_create_question_missing_difficulty(self):
        """Test POST /questions missing difficulty field"""
        response = self.client.post(
            '/questions',
            json={
                'question': 'Q?',
                'answer': 'Answer',
                'category': self.cat1.id
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_create_question_invalid_category(self):
        """Test POST /questions with invalid category"""
        response = self.client.post(
            '/questions',
            json={
                'question': 'Q?',
                'answer': 'Answer',
                'category': 99999,
                'difficulty': 1
            }
        )
        self.assertEqual(response.status_code, 422)

    def test_create_question_with_rating(self):
        """Test POST /questions with rating"""
        response = self.client.post(
            '/questions',
            json={
                'question': 'Q?',
                'answer': 'Answer',
                'category': self.cat1.id,
                'difficulty': 1,
                'rating': 4.5
            }
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['rating'], 4.5)

    # ==================== DELETE /questions Tests ====================

    def test_delete_question_success(self):
        """Test successful question deletion"""
        q_id = self.q1.id
        response = self.client.delete(f'/questions/{q_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['deleted'], q_id)
        self.assertTrue(data['success'])
        
        # Verify deleted
        response = self.client.get(f'/questions/{q_id}')
        self.assertEqual(response.status_code, 404)

    def test_delete_question_not_found(self):
        """Test DELETE /questions/<id> with non-existent ID"""
        response = self.client.delete('/questions/99999')
        self.assertEqual(response.status_code, 404)

    # ==================== Exception Path Tests ====================

    def test_get_questions_empty_database(self):
        """Test GET /questions with empty database"""
        # Create new app with empty database
        app = create_app({
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        client = app.test_client()
        
        with app.app_context():
            db.create_all()
            response = client.get('/questions')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['total_questions'], 0)
            self.assertEqual(len(data['questions']), 0)


if __name__ == '__main__':
    unittest.main()
