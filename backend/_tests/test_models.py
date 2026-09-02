import os
import sys
import unittest
from datetime import datetime
from dotenv import load_dotenv

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flaskr import create_app
from data_access import db, Question, Category, User, GameSession

# Load environment variables
load_dotenv()


class ModelTestCase(unittest.TestCase):
    """Test cases for all database models"""

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

    # ==================== Category Model Tests ====================

    def test_category_create(self):
        """Test creating a category"""
        category = Category('Science')
        self.assertEqual(category.type, 'Science')

    def test_category_insert(self):
        """Test inserting a category into database"""
        category = Category('Art')
        category.insert()

        retrieved = db.session.query(Category).filter_by(type='Art').first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.type, 'Art')

    def test_category_format(self):
        """Test category format method"""
        category = Category('History')
        category.insert()

        formatted = category.format()
        self.assertIn('id', formatted)
        self.assertIn('type', formatted)
        self.assertEqual(formatted['type'], 'History')

    def test_category_update(self):
        """Test updating a category"""
        category = Category('Sports')
        category.insert()
        original_id = category.id

        category.type = 'Sports Updated'
        category.update()

        retrieved = db.session.query(Category).filter_by(id=original_id).first()
        self.assertEqual(retrieved.type, 'Sports Updated')

    def test_category_delete(self):
        """Test deleting a category"""
        category = Category('Entertainment')
        category.insert()
        category_id = category.id

        category.delete()

        retrieved = db.session.query(Category).filter_by(id=category_id).first()
        self.assertIsNone(retrieved)

    # ==================== Question Model Tests ====================

    def test_question_create(self):
        """Test creating a question"""
        question = Question(
            question='What is 2+2?',
            answer='4',
            category=1,
            difficulty=1,
            rating=5.0
        )
        self.assertEqual(question.question, 'What is 2+2?')
        self.assertEqual(question.answer, '4')
        self.assertEqual(question.category, 1)
        self.assertEqual(question.difficulty, 1)
        self.assertEqual(question.rating, 5.0)

    def test_question_create_default_rating(self):
        """Test question creation with default rating"""
        question = Question(
            question='What is the capital of France?',
            answer='Paris',
            category=1,
            difficulty=2
        )
        self.assertEqual(question.rating, 0)

    def test_question_insert(self):
        """Test inserting a question into database"""
        # First create a category
        category = Category('Science')
        category.insert()

        question = Question(
            question='What is H2O?',
            answer='Water',
            category=category.id,
            difficulty=2
        )
        question.insert()

        retrieved = db.session.query(Question).filter_by(
            question='What is H2O?'
        ).first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.answer, 'Water')

    def test_question_format(self):
        """Test question format method"""
        category = Category('Geography')
        category.insert()

        question = Question(
            question='What is the largest ocean?',
            answer='Pacific',
            category=category.id,
            difficulty=1,
            rating=4.5
        )
        question.insert()

        formatted = question.format()
        self.assertIn('id', formatted)
        self.assertIn('question', formatted)
        self.assertIn('answer', formatted)
        self.assertIn('category', formatted)
        self.assertIn('difficulty', formatted)
        self.assertIn('rating', formatted)
        self.assertEqual(formatted['rating'], 4.5)

    def test_question_update(self):
        """Test updating a question"""
        category = Category('History')
        category.insert()

        question = Question(
            question='When was the Titanic built?',
            answer='1912',
            category=category.id,
            difficulty=2
        )
        question.insert()
        question_id = question.id

        question.rating = 3.5
        question.update()

        retrieved = db.session.query(Question).filter_by(id=question_id).first()
        self.assertEqual(retrieved.rating, 3.5)

    def test_question_delete(self):
        """Test deleting a question"""
        category = Category('Entertainment')
        category.insert()

        question = Question(
            question='Who directed Titanic?',
            answer='James Cameron',
            category=category.id,
            difficulty=2
        )
        question.insert()
        question_id = question.id

        question.delete()

        retrieved = db.session.query(Question).filter_by(id=question_id).first()
        self.assertIsNone(retrieved)

    # ==================== User Model Tests ====================

    def test_user_create(self):
        """Test creating a user"""
        user = User(username='john_doe', email='john@example.com')
        self.assertEqual(user.username, 'john_doe')
        self.assertEqual(user.email, 'john@example.com')
        self.assertEqual(user.total_score, 0)
        self.assertEqual(user.games_played, 0)

    def test_user_insert(self):
        """Test inserting a user into database"""
        user = User(username='jane_smith', email='jane@example.com')
        user.insert()

        retrieved = db.session.query(User).filter_by(username='jane_smith').first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.email, 'jane@example.com')

    def test_user_unique_username(self):
        """Test that usernames must be unique"""
        user1 = User(username='duplicate', email='user1@example.com')
        user1.insert()

        user2 = User(username='duplicate', email='user2@example.com')
        with self.assertRaises(Exception):  # Should raise IntegrityError
            user2.insert()

    def test_user_unique_email(self):
        """Test that emails must be unique"""
        user1 = User(username='user1', email='duplicate@example.com')
        user1.insert()

        user2 = User(username='user2', email='duplicate@example.com')
        with self.assertRaises(Exception):  # Should raise IntegrityError
            user2.insert()

    def test_user_format(self):
        """Test user format method"""
        user = User(username='alice', email='alice@example.com')
        user.insert()

        formatted = user.format()
        self.assertIn('id', formatted)
        self.assertIn('username', formatted)
        self.assertIn('email', formatted)
        self.assertIn('total_score', formatted)
        self.assertIn('games_played', formatted)
        self.assertIn('created_at', formatted)
        self.assertEqual(formatted['username'], 'alice')
        self.assertEqual(formatted['total_score'], 0)
        self.assertEqual(formatted['games_played'], 0)

    def test_user_update_scores(self):
        """Test updating user scores"""
        user = User(username='bob', email='bob@example.com')
        user.insert()
        user_id = user.id

        user.total_score = 100
        user.games_played = 5
        user.update()

        retrieved = db.session.query(User).filter_by(id=user_id).first()
        self.assertEqual(retrieved.total_score, 100)
        self.assertEqual(retrieved.games_played, 5)

    def test_user_delete(self):
        """Test deleting a user"""
        user = User(username='charlie', email='charlie@example.com')
        user.insert()
        user_id = user.id

        user.delete()

        retrieved = db.session.query(User).filter_by(id=user_id).first()
        self.assertIsNone(retrieved)

    # ==================== GameSession Model Tests ====================

    def test_game_session_create(self):
        """Test creating a game session"""
        session = GameSession(user_id=1, score=85, category_id=2)
        self.assertEqual(session.user_id, 1)
        self.assertEqual(session.score, 85)
        self.assertEqual(session.category_id, 2)

    def test_game_session_create_without_category(self):
        """Test creating a game session without category"""
        session = GameSession(user_id=1, score=90)
        self.assertEqual(session.user_id, 1)
        self.assertEqual(session.score, 90)
        self.assertIsNone(session.category_id)

    def test_game_session_insert(self):
        """Test inserting a game session"""
        user = User(username='player1', email='player1@example.com')
        user.insert()

        category = Category('Science')
        category.insert()

        session = GameSession(user_id=user.id, score=75, category_id=category.id)
        session.insert()

        retrieved = db.session.query(GameSession).filter_by(
            user_id=user.id
        ).first()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.score, 75)

    def test_game_session_format(self):
        """Test game session format method"""
        user = User(username='player2', email='player2@example.com')
        user.insert()

        session = GameSession(user_id=user.id, score=95)
        session.insert()

        formatted = session.format()
        self.assertIn('id', formatted)
        self.assertIn('user_id', formatted)
        self.assertIn('score', formatted)
        self.assertIn('category_id', formatted)
        self.assertIn('date_played', formatted)
        self.assertEqual(formatted['user_id'], user.id)
        self.assertEqual(formatted['score'], 95)

    def test_game_session_update(self):
        """Test updating a game session"""
        user = User(username='player3', email='player3@example.com')
        user.insert()

        session = GameSession(user_id=user.id, score=80)
        session.insert()
        session_id = session.id

        session.score = 88
        session.update()

        retrieved = db.session.query(GameSession).filter_by(id=session_id).first()
        self.assertEqual(retrieved.score, 88)

    def test_game_session_delete(self):
        """Test deleting a game session"""
        user = User(username='player4', email='player4@example.com')
        user.insert()

        session = GameSession(user_id=user.id, score=70)
        session.insert()
        session_id = session.id

        session.delete()

        retrieved = db.session.query(GameSession).filter_by(id=session_id).first()
        self.assertIsNone(retrieved)

    # ==================== Relationship Tests ====================

    def test_foreign_key_question_category(self):
        """Test foreign key relationship between Question and Category"""
        category = Category('Sports')
        category.insert()

        question = Question(
            question='How many players on a football team?',
            answer='11',
            category=category.id,
            difficulty=1
        )
        question.insert()

        # Verify the relationship works
        retrieved_q = db.session.query(Question).filter_by(
            question='How many players on a football team?'
        ).first()
        self.assertEqual(retrieved_q.category, category.id)

    def test_foreign_key_game_session_user(self):
        """Test foreign key relationship between GameSession and User"""
        user = User(username='gamer1', email='gamer1@example.com')
        user.insert()

        session = GameSession(user_id=user.id, score=100)
        session.insert()

        retrieved_s = db.session.query(GameSession).filter_by(
            user_id=user.id
        ).first()
        self.assertEqual(retrieved_s.user_id, user.id)

    def test_foreign_key_game_session_category(self):
        """Test foreign key relationship between GameSession and Category"""
        user = User(username='gamer2', email='gamer2@example.com')
        user.insert()

        category = Category('History')
        category.insert()

        session = GameSession(user_id=user.id, score=92, category_id=category.id)
        session.insert()

        retrieved_s = db.session.query(GameSession).filter_by(
            id=session.id
        ).first()
        self.assertEqual(retrieved_s.category_id, category.id)


if __name__ == '__main__':
    unittest.main()
