"""Additional tests for GameSessionAnswerService to achieve 80%+ coverage"""

import unittest
from flaskr import create_app
from data_access import db
from data_access.category_repository import CategoryRepository
from data_access.question_repository import QuestionRepository
from data_access.user_repository import UserRepository
from data_access.game_session_repository import GameSessionRepository
from services import GameSessionAnswerService


class GameSessionAnswerServiceCoverageTests(unittest.TestCase):
    """Additional tests to cover exception paths in GameSessionAnswerService"""

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
        
        self.q1 = QuestionRepository.create('Q1?', 'Answer1', self.category.id, 'easy')
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

    # ==================== Exception Path Tests ====================

    def test_record_answer_missing_game_session_id(self):
        """Test record_answer with missing game_session_id"""
        with self.assertRaises(ValueError) as context:
            GameSessionAnswerService.record_answer(
                game_session_id=None,
                question_number=1,
                question=self.q1,
                user_answer='answer'
            )
        self.assertIn('game_session_id', str(context.exception))

    def test_record_answer_missing_question(self):
        """Test record_answer with missing question"""
        with self.assertRaises(ValueError) as context:
            GameSessionAnswerService.record_answer(
                game_session_id=self.game.id,
                question_number=1,
                question=None,
                user_answer='answer'
            )
        self.assertIn('question', str(context.exception))

    def test_record_answer_user_answer_none(self):
        """Test record_answer with user_answer as None"""
        with self.assertRaises(ValueError) as context:
            GameSessionAnswerService.record_answer(
                game_session_id=self.game.id,
                question_number=1,
                question=self.q1,
                user_answer=None
            )
        self.assertIn('user_answer', str(context.exception))

    def test_record_answer_invalid_question_number_negative(self):
        """Test record_answer with negative question_number"""
        with self.assertRaises(ValueError) as context:
            GameSessionAnswerService.record_answer(
                game_session_id=self.game.id,
                question_number=-1,
                question=self.q1,
                user_answer='answer'
            )
        self.assertIn('positive integer', str(context.exception))

    def test_record_answer_invalid_question_number_zero(self):
        """Test record_answer with zero question_number"""
        with self.assertRaises(ValueError) as context:
            GameSessionAnswerService.record_answer(
                game_session_id=self.game.id,
                question_number=0,
                question=self.q1,
                user_answer='answer'
            )
        self.assertIn('positive integer', str(context.exception))

    def test_record_answer_invalid_question_number_non_int(self):
        """Test record_answer with non-integer question_number"""
        with self.assertRaises(ValueError) as context:
            GameSessionAnswerService.record_answer(
                game_session_id=self.game.id,
                question_number='one',
                question=self.q1,
                user_answer='answer'
            )
        self.assertIn('positive integer', str(context.exception))

    def test_record_answer_game_session_not_found(self):
        """Test record_answer with non-existent game_session_id"""
        with self.assertRaises(ValueError) as context:
            GameSessionAnswerService.record_answer(
                game_session_id=99999,
                question_number=1,
                question=self.q1,
                user_answer='answer'
            )
        self.assertIn('not found', str(context.exception))

    def test_record_answer_question_number_exceeds_game_length(self):
        """Test record_answer with question_number beyond game length"""
        with self.assertRaises(ValueError) as context:
            GameSessionAnswerService.record_answer(
                game_session_id=self.game.id,
                question_number=10,  # Game only has 3 questions
                question=self.q1,
                user_answer='answer'
            )
        self.assertIn('exceeds game length', str(context.exception))

    # ==================== Answer Normalization Tests ====================

    def test_compare_answers_exact_match(self):
        """Test _compare_answers with exact match"""
        is_correct = GameSessionAnswerService._compare_answers('Water', 'water')
        self.assertTrue(is_correct)

    def test_compare_answers_case_insensitive(self):
        """Test _compare_answers is case insensitive"""
        is_correct = GameSessionAnswerService._compare_answers('WATER', 'water')
        self.assertTrue(is_correct)

    def test_compare_answers_with_punctuation(self):
        """Test _compare_answers with punctuation"""
        is_correct = GameSessionAnswerService._compare_answers('Water.', 'water')
        self.assertTrue(is_correct)

    def test_compare_answers_with_extra_spaces(self):
        """Test _compare_answers with extra spaces"""
        is_correct = GameSessionAnswerService._compare_answers('Water', '  water  ')
        self.assertTrue(is_correct)

    def test_compare_answers_multiple_words_all_present(self):
        """Test _compare_answers with multiple words - all present"""
        is_correct = GameSessionAnswerService._compare_answers(
            'Sulfuric acid',
            'acid sulfuric'
        )
        self.assertTrue(is_correct)

    def test_compare_answers_multiple_words_partial(self):
        """Test _compare_answers with multiple words - partial"""
        is_correct = GameSessionAnswerService._compare_answers(
            'Sulfuric acid',
            'acid'
        )
        self.assertFalse(is_correct)

    def test_compare_answers_completely_wrong(self):
        """Test _compare_answers with wrong answer"""
        is_correct = GameSessionAnswerService._compare_answers('Water', 'fire')
        self.assertFalse(is_correct)

    # ==================== Game State Tests ====================

    def test_get_game_state_summary_not_found(self):
        """Test get_game_state_summary with non-existent game"""
        with self.assertRaises(ValueError) as context:
            GameSessionAnswerService.get_game_state_summary(99999)
        self.assertIn('not found', str(context.exception))

    def test_get_game_state_summary_valid(self):
        """Test get_game_state_summary with valid game"""
        # Record an answer
        GameSessionAnswerService.record_answer(
            game_session_id=self.game.id,
            question_number=1,
            question=self.q1,
            user_answer='Answer1'
        )
        db.session.commit()
        
        # Get state
        state = GameSessionAnswerService.get_game_state_summary(self.game.id)
        self.assertEqual(state['correct'], 1)
        self.assertEqual(state['total_answered'], 1)
        self.assertEqual(state['total_questions'], 3)

    # ==================== Deprecation Coverage Tests ====================

    def test_has_submitted_answer_true(self):
        """Test has_submitted_answer returns True when non-empty answer exists"""
        # Record an answer with a submitted answer
        GameSessionAnswerService.record_answer(
            game_session_id=self.game.id,
            question_number=1,
            question=self.q1,
            user_answer='Answer1'
        )
        db.session.commit()
        
        # Check - should return True for non-empty user_answer
        has_answer = GameSessionAnswerService.has_submitted_answer(self.game.id, 1)
        self.assertTrue(has_answer)

    def test_has_submitted_answer_false_no_record(self):
        """Test has_submitted_answer returns False when record doesn't exist"""
        has_answer = GameSessionAnswerService.has_submitted_answer(self.game.id, 1)
        self.assertFalse(has_answer)

    def test_has_submitted_answer_false_empty_user_answer(self):
        """Test has_submitted_answer returns False when record exists but user_answer is empty"""
        # Record an answer without a submitted answer (served but not answered)
        GameSessionAnswerService.record_answer(
            game_session_id=self.game.id,
            question_number=1,
            question=self.q1,
            user_answer=''  # Empty user_answer for served but not answered
        )
        db.session.commit()
        
        # Check - should return False for empty user_answer even though record exists
        has_answer = GameSessionAnswerService.has_submitted_answer(self.game.id, 1)
        self.assertFalse(has_answer)


if __name__ == '__main__':
    unittest.main()
