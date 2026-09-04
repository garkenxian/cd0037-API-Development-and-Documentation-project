"""Unit tests for optimized repository methods with JOINs"""

import unittest
from unittest.mock import patch, MagicMock
from flaskr import create_app
from models import db, Category, Question, GameSession, User


class CategoryRepositoryOptimizedTests(unittest.TestCase):
    """Unit tests for optimized CategoryRepository methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "TESTING": True
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Cleanup"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_all_with_question_counts_returns_categories_with_count(self):
        """Test that get_all_with_question_counts returns categories with counts"""
        from data_access import CategoryRepository
        
        # Create test data
        cat1 = Category('Science')
        cat2 = Category('History')
        db.session.add(cat1)
        db.session.add(cat2)
        db.session.commit()
        
        # Add questions to category 1
        q1 = Question('What is H2O?', 'Water', cat1.id, 1)
        q2 = Question('What is CO2?', 'Carbon Dioxide', cat1.id, 2)
        db.session.add(q1)
        db.session.add(q2)
        db.session.commit()
        
        # Get categories with counts
        result = CategoryRepository.get_all_with_question_counts(page=1, per_page=50)
        
        # Verify structure
        self.assertIsNotNone(result)
        self.assertEqual(len(result.items), 2)
        
        # Check first category has 2 questions
        cat1_result, count1 = result.items[0]
        self.assertEqual(cat1_result.type, 'Science')
        self.assertEqual(count1, 2)
        
        # Check second category has 0 questions
        cat2_result, count2 = result.items[1]
        self.assertEqual(cat2_result.type, 'History')
        self.assertEqual(count2, 0)


class QuestionRepositoryOptimizedTests(unittest.TestCase):
    """Unit tests for optimized QuestionRepository methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "TESTING": True
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Cleanup"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_all_with_categories_eagerly_loads_category(self):
        """Test that get_all_with_categories loads category relationship"""
        from data_access import QuestionRepository
        
        # Create test data
        category = Category('Science')
        db.session.add(category)
        db.session.commit()
        
        question = Question('What is H2O?', 'Water', category.id, 1)
        db.session.add(question)
        db.session.commit()
        
        # Get questions with categories
        result = QuestionRepository.get_all_with_categories(page=1, per_page=50)
        
        self.assertEqual(len(result.items), 1)
        q = result.items[0]
        self.assertEqual(q.question, 'What is H2O?')
        # Category should be available without lazy loading
        self.assertEqual(q.category, category.id)

    def test_get_by_category_with_details_returns_questions_with_category(self):
        """Test that get_by_category_with_details filters by category"""
        from data_access import QuestionRepository
        
        # Create test data
        cat1 = Category('Science')
        cat2 = Category('History')
        db.session.add(cat1)
        db.session.add(cat2)
        db.session.commit()
        
        q1 = Question('What is H2O?', 'Water', cat1.id, 1)
        q2 = Question('What is CO2?', 'Carbon Dioxide', cat1.id, 2)
        q3 = Question('When was 1776?', 'American Independence', cat2.id, 1)
        db.session.add(q1)
        db.session.add(q2)
        db.session.add(q3)
        db.session.commit()
        
        # Get questions from category 1
        result = QuestionRepository.get_by_category_with_details(cat1.id, page=1, per_page=50)
        
        self.assertEqual(len(result.items), 2)
        self.assertEqual(result.items[0].question, 'What is H2O?')
        self.assertEqual(result.items[1].question, 'What is CO2?')


class GameSessionRepositoryOptimizedTests(unittest.TestCase):
    """Unit tests for optimized GameSessionRepository methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "TESTING": True
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Cleanup"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_user_stats_uses_sql_aggregation(self):
        """Test that get_user_stats uses SQL aggregation"""
        from data_access import GameSessionRepository
        
        # Create test data
        user = User('testuser', 'test@example.com')
        db.session.add(user)
        db.session.commit()
        
        # Add game sessions
        session1 = GameSession(user.id, 100)
        session2 = GameSession(user.id, 150)
        session3 = GameSession(user.id, 200)
        db.session.add(session1)
        db.session.add(session2)
        db.session.add(session3)
        db.session.commit()
        
        # Get stats
        stats = GameSessionRepository.get_user_stats(user.id)
        
        self.assertEqual(stats['total_games'], 3)
        self.assertEqual(stats['total_score'], 450)
        self.assertEqual(stats['average_score'], 150.0)

    def test_get_user_stats_returns_zeros_for_no_sessions(self):
        """Test that get_user_stats returns zeros when user has no sessions"""
        from data_access import GameSessionRepository
        
        # Create user but no sessions
        user = User('testuser', 'test@example.com')
        db.session.add(user)
        db.session.commit()
        
        # Get stats
        stats = GameSessionRepository.get_user_stats(user.id)
        
        self.assertEqual(stats['total_games'], 0)
        self.assertEqual(stats['total_score'], 0)
        self.assertEqual(stats['average_score'], 0.0)

    def test_get_by_user_with_details_loads_related_data(self):
        """Test that get_by_user_with_details loads User and Category data"""
        from data_access import GameSessionRepository
        
        # Create test data
        user = User('testuser', 'test@example.com')
        category = Category('Science')
        db.session.add(user)
        db.session.add(category)
        db.session.commit()
        
        session = GameSession(user.id, 100, category.id)
        db.session.add(session)
        db.session.commit()
        
        # Get sessions with details
        result = GameSessionRepository.get_by_user_with_details(user.id, page=1, per_page=50)
        
        self.assertEqual(len(result.items), 1)
        s = result.items[0]
        self.assertEqual(s.user_id, user.id)
        self.assertEqual(s.score, 100)
        self.assertEqual(s.category_id, category.id)


if __name__ == '__main__':
    unittest.main()
