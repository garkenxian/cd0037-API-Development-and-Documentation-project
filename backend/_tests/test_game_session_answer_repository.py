"""Tests for GameSessionAnswerRepository to achieve 80%+ coverage"""

import unittest
from flaskr import create_app
from data_access import db
from data_access.category_repository import CategoryRepository
from data_access.question_repository import QuestionRepository
from data_access.user_repository import UserRepository
from data_access.game_session_repository import GameSessionRepository
from data_access.game_session_answer_repository import GameSessionAnswerRepository
from models import GameSessionAnswer


class GameSessionAnswerRepositoryTests(unittest.TestCase):
    """Comprehensive tests for GameSessionAnswerRepository coverage"""

    def setUp(self):
        """Set up test database and app context"""
        self.database_path = "sqlite:///:memory:"
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create test data
        self.user = UserRepository.create('testuser', None)
        db.session.flush()
        
        self.category = CategoryRepository.create('Science')
        db.session.flush()
        
        self.q1 = QuestionRepository.create('Q1?', 'Answer1', self.category.id, 1)
        self.q2 = QuestionRepository.create('Q2?', 'Answer2', self.category.id, 3)
        self.q3 = QuestionRepository.create('Q3?', 'Answer3', self.category.id, 5)
        db.session.commit()
        
        # Create a game session
        self.game = GameSessionRepository.create(
            user_id=self.user.id,
            score=0,
            category_id=self.category.id,
            number_of_questions=3
        )
        db.session.commit()

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        self.app_context.pop()

    # ==================== CRUD Tests ====================

    def test_create_and_get_by_id(self):
        """Test create and get_by_id methods"""
        # Create
        answer = GameSessionAnswerRepository.create(
            game_session_id=self.game.id,
            question_number=1,
            question_id=self.q1.id,
            question_snapshot='Q1?',
            answer_snapshot='Answer1',
            user_answer='',
            is_correct=False
        )
        db.session.commit()
        answer_id = answer.id
        
        # Get by ID
        retrieved = GameSessionAnswerRepository.get_by_id(answer_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, answer_id)
        self.assertEqual(retrieved.game_session_id, self.game.id)
        self.assertEqual(retrieved.question_number, 1)

    def test_get_by_id_not_found(self):
        """Test get_by_id with non-existent ID"""
        result = GameSessionAnswerRepository.get_by_id(99999)
        self.assertIsNone(result)

    def test_get_by_game_and_question(self):
        """Test get_by_game_and_question method"""
        # Create answer
        GameSessionAnswerRepository.create(
            game_session_id=self.game.id,
            question_number=1,
            question_id=self.q1.id,
            question_snapshot='Q1?',
            answer_snapshot='Answer1',
            user_answer='Answer1',
            is_correct=True
        )
        db.session.commit()
        
        # Get by game and question
        result = GameSessionAnswerRepository.get_by_game_and_question(self.game.id, 1)
        self.assertIsNotNone(result)
        self.assertEqual(result.question_number, 1)
        self.assertTrue(result.is_correct)

    def test_get_by_game_and_question_not_found(self):
        """Test get_by_game_and_question with non-existent question"""
        result = GameSessionAnswerRepository.get_by_game_and_question(self.game.id, 99)
        self.assertIsNone(result)

    # ==================== Query Tests ====================

    def test_get_by_game_ordered(self):
        """Test get_by_game with order_by_question=True (default)"""
        # Create multiple answers
        GameSessionAnswerRepository.create(
            game_session_id=self.game.id,
            question_number=3,
            question_id=self.q3.id,
            question_snapshot='Q3?',
            answer_snapshot='Answer3',
            user_answer='Answer3',
            is_correct=True
        )
        GameSessionAnswerRepository.create(
            game_session_id=self.game.id,
            question_number=1,
            question_id=self.q1.id,
            question_snapshot='Q1?',
            answer_snapshot='Answer1',
            user_answer='Answer1',
            is_correct=True
        )
        GameSessionAnswerRepository.create(
            game_session_id=self.game.id,
            question_number=2,
            question_id=self.q2.id,
            question_snapshot='Q2?',
            answer_snapshot='Answer2',
            user_answer='',
            is_correct=False
        )
        db.session.commit()
        
        # Get by game with order
        results = GameSessionAnswerRepository.get_by_game(self.game.id, order_by_question=True)
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0].question_number, 1)
        self.assertEqual(results[1].question_number, 2)
        self.assertEqual(results[2].question_number, 3)

    def test_get_by_game_unordered(self):
        """Test get_by_game with order_by_question=False"""
        # Create multiple answers
        GameSessionAnswerRepository.create(
            game_session_id=self.game.id,
            question_number=1,
            question_id=self.q1.id,
            question_snapshot='Q1?',
            answer_snapshot='Answer1',
            user_answer='Answer1',
            is_correct=True
        )
        GameSessionAnswerRepository.create(
            game_session_id=self.game.id,
            question_number=2,
            question_id=self.q2.id,
            question_snapshot='Q2?',
            answer_snapshot='Answer2',
            user_answer='Answer2',
            is_correct=True
        )
        db.session.commit()
        
        # Get by game without order
        results = GameSessionAnswerRepository.get_by_game(self.game.id, order_by_question=False)
        self.assertEqual(len(results), 2)

    def test_get_by_game_empty(self):
        """Test get_by_game with no answers"""
        results = GameSessionAnswerRepository.get_by_game(self.game.id)
        self.assertEqual(len(results), 0)

    # ==================== Count Tests ====================

    def test_count_correct_by_game(self):
        """Test count_correct_by_game method"""
        # Create correct and incorrect answers
        GameSessionAnswerRepository.create(
            game_session_id=self.game.id,
            question_number=1,
            question_id=self.q1.id,
            question_snapshot='Q1?',
            answer_snapshot='Answer1',
            user_answer='Answer1',
            is_correct=True
        )
        GameSessionAnswerRepository.create(
            game_session_id=self.game.id,
            question_number=2,
            question_id=self.q2.id,
            question_snapshot='Q2?',
            answer_snapshot='Answer2',
            user_answer='Wrong',
            is_correct=False
        )
        GameSessionAnswerRepository.create(
            game_session_id=self.game.id,
            question_number=3,
            question_id=self.q3.id,
            question_snapshot='Q3?',
            answer_snapshot='Answer3',
            user_answer='Answer3',
            is_correct=True
        )
        db.session.commit()
        
        # Count correct
        count = GameSessionAnswerRepository.count_correct_by_game(self.game.id)
        self.assertEqual(count, 2)

    def test_count_correct_by_game_none(self):
        """Test count_correct_by_game with no correct answers"""
        GameSessionAnswerRepository.create(
            game_session_id=self.game.id,
            question_number=1,
            question_id=self.q1.id,
            question_snapshot='Q1?',
            answer_snapshot='Answer1',
            user_answer='Wrong',
            is_correct=False
        )
        db.session.commit()
        
        count = GameSessionAnswerRepository.count_correct_by_game(self.game.id)
        self.assertEqual(count, 0)

    def test_count_total_by_game(self):
        """Test count_total_by_game method"""
        GameSessionAnswerRepository.create(
            game_session_id=self.game.id,
            question_number=1,
            question_id=self.q1.id,
            question_snapshot='Q1?',
            answer_snapshot='Answer1',
            user_answer='Answer1',
            is_correct=True
        )
        GameSessionAnswerRepository.create(
            game_session_id=self.game.id,
            question_number=2,
            question_id=self.q2.id,
            question_snapshot='Q2?',
            answer_snapshot='Answer2',
            user_answer='',
            is_correct=False
        )
        db.session.commit()
        
        count = GameSessionAnswerRepository.count_total_by_game(self.game.id)
        self.assertEqual(count, 2)

    def test_count_total_by_game_empty(self):
        """Test count_total_by_game with no answers"""
        count = GameSessionAnswerRepository.count_total_by_game(self.game.id)
        self.assertEqual(count, 0)

    # ==================== Pagination Tests ====================

    def test_get_by_game_paginated(self):
        """Test get_by_game_paginated method"""
        # Create multiple answers
        for i in range(5):
            GameSessionAnswerRepository.create(
                game_session_id=self.game.id,
                question_number=i + 1,
                question_id=self.q1.id,
                question_snapshot=f'Q{i+1}?',
                answer_snapshot='Answer',
                user_answer='Answer',
                is_correct=True
            )
        db.session.commit()
        
        # Get paginated
        page1 = GameSessionAnswerRepository.get_by_game_paginated(self.game.id, page=1, per_page=2)
        self.assertEqual(len(page1.items), 2)
        self.assertTrue(page1.has_next)
        self.assertFalse(page1.has_prev)

    def test_get_by_game_paginated_page_2(self):
        """Test pagination page 2"""
        # Create multiple answers
        for i in range(5):
            GameSessionAnswerRepository.create(
                game_session_id=self.game.id,
                question_number=i + 1,
                question_id=self.q1.id,
                question_snapshot=f'Q{i+1}?',
                answer_snapshot='Answer',
                user_answer='Answer',
                is_correct=True
            )
        db.session.commit()
        
        # Get page 2
        page2 = GameSessionAnswerRepository.get_by_game_paginated(self.game.id, page=2, per_page=2)
        self.assertEqual(len(page2.items), 2)

    # ==================== Update/Delete Tests ====================

    def test_update(self):
        """Test update method"""
        answer = GameSessionAnswerRepository.create(
            game_session_id=self.game.id,
            question_number=1,
            question_id=self.q1.id,
            question_snapshot='Q1?',
            answer_snapshot='Answer1',
            user_answer='',
            is_correct=False
        )
        db.session.commit()
        
        # Update
        updated = GameSessionAnswerRepository.update(answer, user_answer='NewAnswer', is_correct=True)
        db.session.commit()
        
        # Verify
        retrieved = GameSessionAnswerRepository.get_by_id(answer.id)
        self.assertEqual(retrieved.user_answer, 'NewAnswer')
        self.assertTrue(retrieved.is_correct)

    def test_delete(self):
        """Test delete method"""
        answer = GameSessionAnswerRepository.create(
            game_session_id=self.game.id,
            question_number=1,
            question_id=self.q1.id,
            question_snapshot='Q1?',
            answer_snapshot='Answer1',
            user_answer='Answer1',
            is_correct=True
        )
        db.session.commit()
        answer_id = answer.id
        
        # Delete
        GameSessionAnswerRepository.delete(answer)
        db.session.commit()
        
        # Verify
        retrieved = GameSessionAnswerRepository.get_by_id(answer_id)
        self.assertIsNone(retrieved)

    def test_delete_by_game(self):
        """Test delete_by_game method"""
        # Create multiple answers
        GameSessionAnswerRepository.create(
            game_session_id=self.game.id,
            question_number=1,
            question_id=self.q1.id,
            question_snapshot='Q1?',
            answer_snapshot='Answer1',
            user_answer='Answer1',
            is_correct=True
        )
        GameSessionAnswerRepository.create(
            game_session_id=self.game.id,
            question_number=2,
            question_id=self.q2.id,
            question_snapshot='Q2?',
            answer_snapshot='Answer2',
            user_answer='Answer2',
            is_correct=True
        )
        db.session.commit()
        
        # Delete by game
        GameSessionAnswerRepository.delete_by_game(self.game.id)
        db.session.commit()
        
        # Verify
        count = GameSessionAnswerRepository.count_total_by_game(self.game.id)
        self.assertEqual(count, 0)

    # ==================== Existence Tests ====================

    def test_exists_by_game_and_question_true(self):
        """Test exists_by_game_and_question when exists"""
        GameSessionAnswerRepository.create(
            game_session_id=self.game.id,
            question_number=1,
            question_id=self.q1.id,
            question_snapshot='Q1?',
            answer_snapshot='Answer1',
            user_answer='Answer1',
            is_correct=True
        )
        db.session.commit()
        
        exists = GameSessionAnswerRepository.exists_by_game_and_question(self.game.id, 1)
        self.assertTrue(exists)

    def test_exists_by_game_and_question_false(self):
        """Test exists_by_game_and_question when not exists"""
        exists = GameSessionAnswerRepository.exists_by_game_and_question(self.game.id, 1)
        self.assertFalse(exists)


if __name__ == '__main__':
    unittest.main()
