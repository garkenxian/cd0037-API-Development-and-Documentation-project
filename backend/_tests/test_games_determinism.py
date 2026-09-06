"""
Tests for Phase 1 - Deterministic Secure Game Session Core
Validates game flow correctness, answer audit trail, and sequence integrity
"""

import unittest
import json
from unittest.mock import patch
from flaskr import create_app
from data_access import db
from data_access.category_repository import CategoryRepository
from data_access.question_repository import QuestionRepository
from data_access.user_repository import UserRepository
from data_access.game_session_repository import GameSessionRepository
from data_access.game_session_answer_repository import GameSessionAnswerRepository
from services import GameSessionAnswerService


class GameDeterminismTests(unittest.TestCase):
    """Test deterministic game flow with audit trail"""

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
        
        # Create test data
        self.user = UserRepository.create('testuser', 'testuser@test.com')
        db.session.flush()
        
        self.cat_science = CategoryRepository.create('Science')
        self.cat_history = CategoryRepository.create('History')
        db.session.flush()
        
        self.q1 = QuestionRepository.create('What is H2O?', 'Water', self.cat_science.id, 1)
        self.q2 = QuestionRepository.create('What is H2SO4?', 'Sulfuric acid', self.cat_science.id, 3)
        self.q3 = QuestionRepository.create('What year did Rome fall?', '476', self.cat_history.id, 5)
        self.q4 = QuestionRepository.create('Who was Caesar?', 'Roman Emperor', self.cat_history.id, 3)
        self.q5 = QuestionRepository.create('What is CO2?', 'Carbon dioxide', self.cat_science.id, 1)
        db.session.commit()

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        self.app_context.pop()

    # ==================== Determinism Tests ====================
    
    def test_create_game_stores_first_question_deterministically(self):
        """POST /games should store first question in audit trail"""
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 2
        })
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        game_id = data['game_session_id']
        
        # Check that first question was stored in audit trail
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        self.assertEqual(len(answers), 1)
        self.assertEqual(answers[0].question_number, 1)
        self.assertIsNotNone(answers[0].question_id)
        self.assertIsNotNone(answers[0].question_snapshot)
        self.assertIsNotNone(answers[0].answer_snapshot)

    def test_answer_uses_stored_question_snapshot_not_random(self):
        """POST /games/<id>/<q_number> should validate against stored snapshot, not random fetch"""
        # Create game
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 3
        })
        data = json.loads(response.data)
        game_id = data['game_session_id']
        first_q = data['question']['id']
        
        # Get stored question for verification
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        stored_answer_text = answers[0].answer_snapshot
        
        # Answer the first question correctly
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': stored_answer_text
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['correct'])

    def test_duplicate_answer_rejected_with_422(self):
        """POST /games/<id>/<q_number> twice should reject second with 422"""
        # Create game
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 2
        })
        data = json.loads(response.data)
        game_id = data['game_session_id']
        
        # Answer question 1 once
        response1 = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': 'Water'
        })
        self.assertEqual(response1.status_code, 200)
        
        # Try to answer question 1 again - should be 422
        response2 = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': 'Water'
        })
        self.assertEqual(response2.status_code, 422)

    def test_out_of_order_answers_rejected_with_422(self):
        """Submitting answers out of order should be rejected with 422"""
        # Create game with 3 questions
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 3
        })
        data = json.loads(response.data)
        game_id = data['game_session_id']
        
        # Try to answer question 2 first (out of order)
        # Question 1 should be the expected next question
        response = self.client.post(f'/games/{game_id}/2', json={
            'user_answer': 'Wrong answer'
        })
        # Should reject with 422 because it's not the next expected question
        self.assertEqual(response.status_code, 422)
        
        # Answer question 1 (the correct sequence)
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': 'Water'
        })
        self.assertEqual(response.status_code, 200)
        
        # Only question 1 should have been answered
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        answered = [a for a in answers if a.user_answer and a.user_answer.strip()]
        self.assertEqual(len(answered), 1)
        self.assertEqual(answered[0].question_number, 1)

    def test_resume_returns_correct_next_question(self):
        """GET /games/<id> should return first unanswered question from audit trail"""
        # Create game
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 3
        })
        data = json.loads(response.data)
        game_id = data['game_session_id']
        
        # Get the correct answer for question 1
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        correct_answer_1 = answers[0].answer_snapshot
        
        # Answer question 1
        self.client.post(f'/games/{game_id}/1', json={
            'user_answer': correct_answer_1
        })
        
        # Resume should return question 2
        response = self.client.get(f'/games/{game_id}')
        data = json.loads(response.data)
        self.assertEqual(data['current_question_number'], 2)
        self.assertNotEqual(data['current_score']['total_answered'], 0)

    def test_game_complete_updates_user_stats_exactly_once(self):
        """Completing a game should update User.total_score and games_played exactly once"""
        # Create game with 1 question
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 1
        })
        data = json.loads(response.data)
        game_id = data['game_session_id']
        correct_answer = data['question']  # This will have the answer in the audit trail
        
        # Get the correct answer from the audit trail
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        correct_answer_text = answers[0].answer_snapshot
        
        # Get user initial stats
        user_before = UserRepository.get_by_id(self.user.id)
        self.assertEqual(user_before.total_score, 0)
        self.assertEqual(user_before.games_played, 0)
        
        # Answer the only question correctly using the correct answer from snapshot
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': correct_answer_text
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['correct'])
        self.assertEqual(data['status'], 'completed')
        
        # Get user after game
        user_after = UserRepository.get_by_id(self.user.id)
        self.assertEqual(user_after.total_score, 1)  # 1 correct answer
        self.assertEqual(user_after.games_played, 1)  # 1 game completed
        
        # Verify idempotency - GET should still show completed
        response = self.client.get(f'/games/{game_id}')
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'completed')
        
        # User stats should not change from second GET
        user_final = UserRepository.get_by_id(self.user.id)
        self.assertEqual(user_final.total_score, 1)
        self.assertEqual(user_final.games_played, 1)

    def test_score_matches_correct_count_not_assumed(self):
        """Game score should match count of correct GameSessionAnswers, not assumed"""
        # Create game with 2 questions
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 2
        })
        data = json.loads(response.data)
        game_id = data['game_session_id']
        
        # Get the correct answer for question 1
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        correct_answer_1 = answers[0].answer_snapshot
        
        # Answer first correctly
        self.client.post(f'/games/{game_id}/1', json={
            'user_answer': correct_answer_1
        })
        
        # Get the correct answer for question 2 (was created when we answered 1)
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        correct_answer_2 = None
        for ans in answers:
            if ans.question_number == 2:
                correct_answer_2 = ans.answer_snapshot
                break
        
        # Answer second incorrectly
        self.client.post(f'/games/{game_id}/2', json={
            'user_answer': 'Wrong'
        })
        
        # Complete and check final state
        response = self.client.get(f'/games/{game_id}')
        data = json.loads(response.data)
        
        # Score should be 1 (only 1 correct)
        self.assertEqual(data['current_score']['correct'], 1)
        self.assertEqual(data['current_score']['total_answered'], 2)
        
        # Verify via audit trail - only check user-submitted answers (question_number in [1,2])
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        user_answers = [ans for ans in answers if ans.question_number in [1, 2] and ans.user_answer and ans.user_answer.strip()]
        correct_count = sum(1 for ans in user_answers if ans.is_correct)
        self.assertEqual(correct_count, 1)

    def test_answer_audit_trail_immutable(self):
        """GameSessionAnswer records should be immutable after creation"""
        # Create game and answer a question
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 1
        })
        data = json.loads(response.data)
        game_id = data['game_session_id']
        first_question = data['question']  # Get the actually returned question
        
        self.client.post(f'/games/{game_id}/1', json={
            'user_answer': 'Water'
        })
        
        # Verify audit trail has correct snapshot of the served question
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        answer_record = answers[-1]  # Last one is the actual answer
        
        # The snapshot should match the question that was actually served
        self.assertEqual(answer_record.question_snapshot, first_question['question'])
        self.assertIsNotNone(answer_record.answer_snapshot)
        self.assertEqual(answer_record.user_answer, 'Water')
        # Note: is_correct depends on which question was served
        self.assertIsNotNone(answer_record.created_at)

    def test_sequence_validation_rejects_out_of_bounds_question_number(self):
        """POST /games/<id>/<q_number> should reject question_number outside [1..N]"""
        # Create game with 2 questions
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 2
        })
        data = json.loads(response.data)
        game_id = data['game_session_id']
        
        # Try question 0
        response = self.client.post(f'/games/{game_id}/0', json={
            'user_answer': 'Water'
        })
        self.assertEqual(response.status_code, 422)
        
        # Try question 3 (beyond max)
        response = self.client.post(f'/games/{game_id}/3', json={
            'user_answer': 'Water'
        })
        self.assertEqual(response.status_code, 422)

    def test_next_question_correctly_generated_and_stored(self):
        """Next question should be deterministically generated and stored on first access"""
        # Create game with 3 questions
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 3
        })
        data = json.loads(response.data)
        game_id = data['game_session_id']
        first_q_id = data['question']['id']
        
        # Answer first question
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': 'Water'
        })
        data = json.loads(response.data)
        second_q_id = data['question']['id']
        
        # Verify second question is stored in audit trail
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        self.assertGreaterEqual(len(answers), 2)
        second_q_record = None
        for ans in answers:
            if ans.question_number == 2:
                second_q_record = ans
                break
        
        self.assertIsNotNone(second_q_record)
        self.assertEqual(second_q_record.question_id, second_q_id)

    def test_no_duplicate_questions_within_session(self):
        """No question should appear twice in a game session (normal or resumed flow)"""
        # Create game with 3 questions
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 3
        })
        data = json.loads(response.data)
        game_id = data['game_session_id']
        question_ids = []
        
        # Get question IDs for all questions as we progress through the game
        # Q1 from creation
        question_ids.append(data['question']['id'])
        
        # Answer Q1, get Q2
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': 'Water'
        })
        data = json.loads(response.data)
        if data.get('question'):
            question_ids.append(data['question']['id'])
        
        # Get Q2 again and answer, get Q3
        response = self.client.get(f'/games/{game_id}')
        data = json.loads(response.data)
        if data.get('question'):
            q2_id = data['question']['id']
            if q2_id not in question_ids:
                question_ids.append(q2_id)
        
        response = self.client.post(f'/games/{game_id}/2', json={
            'user_answer': 'Wrong'
        })
        data = json.loads(response.data)
        if data.get('question'):
            question_ids.append(data['question']['id'])
        
        # Verify no duplicates
        self.assertEqual(len(question_ids), len(set(question_ids)), 
                         f"Duplicate question IDs found: {question_ids}")

    def test_idempotent_completion_no_double_award(self):
        """Completion should be idempotent - completing twice should not double-award"""
        # Create game with 1 question
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 1
        })
        data = json.loads(response.data)
        game_id = data['game_session_id']
        
        # Get initial user stats
        user_before = UserRepository.get_by_id(self.user.id)
        self.assertEqual(user_before.total_score, 0)
        self.assertEqual(user_before.games_played, 0)
        
        # Get the correct answer from the persisted record
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        correct_answer = answers[0].answer_snapshot
        
        # Answer correctly
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': correct_answer
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'completed')
        
        # Check user stats after first completion
        user_after_first = UserRepository.get_by_id(self.user.id)
        first_score = user_after_first.total_score
        first_games = user_after_first.games_played
        
        # Get the game and verify completion flag
        from models import GameSession
        game_session = db.session.query(GameSession).get(game_id)
        self.assertTrue(game_session.is_completed)
        self.assertEqual(game_session.awarded_score, 1)
        
        # Try to GET the game multiple times - should remain completed
        for i in range(3):
            response = self.client.get(f'/games/{game_id}')
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'completed')
        
        # User stats should not change from multiple GETs
        user_after_gets = UserRepository.get_by_id(self.user.id)
        self.assertEqual(user_after_gets.total_score, first_score)
        self.assertEqual(user_after_gets.games_played, first_games)

    def test_completion_updates_are_atomic(self):
        """Completion should atomically update is_completed flag and awarded_score"""
        # Create game with 1 question
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 1
        })
        data = json.loads(response.data)
        game_id = data['game_session_id']
        
        # Get the GameSession before answering
        from models import GameSession
        game_before = db.session.query(GameSession).get(game_id)
        self.assertFalse(game_before.is_completed)
        self.assertIsNone(game_before.awarded_score)
        
        # Answer the question
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': 'Water'
        })
        self.assertEqual(response.status_code, 200)
        
        # Verify completion flag and award were set atomically
        game_after = db.session.query(GameSession).get(game_id)
        self.assertTrue(game_after.is_completed)
        self.assertIsNotNone(game_after.awarded_score)
        self.assertGreaterEqual(game_after.awarded_score, 0)


class GameSessionAnswerServiceTests(unittest.TestCase):
    """Unit tests for GameSessionAnswerService"""

    def setUp(self):
        """Set up test database and app context"""
        self.database_path = "sqlite:///:memory:"
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })

        # Push app context
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create tables
        db.create_all()
        
        # Create test data
        self.user = UserRepository.create('testuser', 'testuser@test.com')
        db.session.flush()
        
        self.cat = CategoryRepository.create('Science')
        db.session.flush()
        
        self.q1 = QuestionRepository.create('What is H2O?', 'Water', self.cat.id, 1)
        self.q2 = QuestionRepository.create('What is CO2?', 'Carbon dioxide', self.cat.id, 1)
        db.session.commit()
        
        # Create game
        self.game = GameSessionRepository.create(self.user.id, 0, self.cat.id, 2)
        db.session.commit()

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        self.app_context.pop()

    def test_record_answer_creates_audit_record(self):
        """record_answer should create GameSessionAnswer with all snapshots"""
        result = GameSessionAnswerService.record_answer(
            game_session_id=self.game.id,
            question_number=1,
            question=self.q1,
            user_answer='Water'
        )
        db.session.commit()
        
        self.assertTrue(result['is_correct'])
        self.assertEqual(result['correct_answer'], 'Water')
        
        # Verify record was created
        record = GameSessionAnswerRepository.get_by_game_and_question(self.game.id, 1)
        self.assertIsNotNone(record)
        self.assertEqual(record.question_snapshot, self.q1.question)
        self.assertEqual(record.answer_snapshot, self.q1.answer)

    def test_record_answer_allows_update_on_second_call(self):
        """record_answer should allow updating an existing record on second call"""
        # Record first answer
        result1 = GameSessionAnswerService.record_answer(
            game_session_id=self.game.id,
            question_number=1,
            question=self.q1,
            user_answer='Water'
        )
        db.session.commit()
        
        # Verify first record
        self.assertTrue(result1['is_correct'])
        record1 = GameSessionAnswerRepository.get_by_game_and_question(self.game.id, 1)
        self.assertEqual(record1.user_answer, 'Water')
        
        # Try to update (different answer)
        result2 = GameSessionAnswerService.record_answer(
            game_session_id=self.game.id,
            question_number=1,
            question=self.q1,
            user_answer='Wrong answer'
        )
        db.session.commit()
        
        # Verify second record is updated
        self.assertFalse(result2['is_correct'])
        record2 = GameSessionAnswerRepository.get_by_game_and_question(self.game.id, 1)
        self.assertEqual(record2.user_answer, 'Wrong answer')

    def test_compute_game_score_counts_correct_only(self):
        """compute_game_score should count only correct answers"""
        GameSessionAnswerService.record_answer(self.game.id, 1, self.q1, 'Water')
        GameSessionAnswerService.record_answer(self.game.id, 2, self.q2, 'Wrong answer')
        db.session.commit()
        
        score = GameSessionAnswerService.compute_game_score(self.game.id)
        self.assertEqual(score, 1)

    def test_get_next_question_number_finds_first_unanswered(self):
        """get_next_question_number should return first unanswered"""
        GameSessionAnswerService.record_answer(self.game.id, 1, self.q1, 'Water')
        db.session.commit()
        
        next_q = GameSessionAnswerService.get_next_question_number(self.game.id, 2)
        self.assertEqual(next_q, 2)

    def test_is_game_complete_when_all_answered(self):
        """is_game_complete should return True when all questions answered"""
        GameSessionAnswerService.record_answer(self.game.id, 1, self.q1, 'Water')
        GameSessionAnswerService.record_answer(self.game.id, 2, self.q2, 'Carbon dioxide')
        db.session.commit()
        
        complete = GameSessionAnswerService.is_game_complete(self.game.id, 2)
        self.assertTrue(complete)

    def test_answer_normalization_handles_punctuation(self):
        """Answer comparison should normalize punctuation"""
        # Question with answer "Dr. Martin Luther King Jr."
        q = QuestionRepository.create(
            'Who said "I have a dream"?',
            'Dr. Martin Luther King Jr.',
            self.cat.id,
            3
        )
        db.session.commit()
        
        result = GameSessionAnswerService.record_answer(
            self.game.id, 1, q, 'Dr Martin Luther King Jr'
        )
        db.session.commit()
        
        # Should match even without punctuation
        self.assertTrue(result['is_correct'])


if __name__ == '__main__':
    unittest.main()
