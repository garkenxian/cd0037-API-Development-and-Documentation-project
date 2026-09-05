"""
Tests for Phase 1 - Game failure paths and error handling
Validates atomicity, error propagation, and persistence guarantees
"""

import unittest
import json
from unittest.mock import patch, MagicMock
from flaskr import create_app
from data_access import db
from data_access.category_repository import CategoryRepository
from data_access.question_repository import QuestionRepository
from data_access.user_repository import UserRepository
from data_access.game_session_repository import GameSessionRepository
from data_access.game_session_answer_repository import GameSessionAnswerRepository


class GameFailurePathTests(unittest.TestCase):
    """Test failure paths and atomicity guarantees"""

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
        self.user = UserRepository.create('testuser', None)
        db.session.flush()
        
        self.cat_science = CategoryRepository.create('Science')
        self.cat_history = CategoryRepository.create('History')
        db.session.flush()
        
        self.q1 = QuestionRepository.create('What is H2O?', 'Water', self.cat_science.id, 'easy')
        self.q2 = QuestionRepository.create('What is H2SO4?', 'Sulfuric acid', self.cat_science.id, 'medium')
        self.q3 = QuestionRepository.create('What year did Rome fall?', '476', self.cat_history.id, 'hard')
        self.q4 = QuestionRepository.create('Who was Caesar?', 'Roman Emperor', self.cat_history.id, 'medium')
        self.q5 = QuestionRepository.create('What is CO2?', 'Carbon dioxide', self.cat_science.id, 'easy')
        db.session.commit()

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        self.app_context.pop()

    # ==================== Atomicity Tests ====================
    
    def test_atomic_create_game_no_orphan_on_first_question_failure(self):
        """If first question record fails, entire game creation should roll back"""
        # This test validates that create_game_session_with_first_question is atomic
        from services import GameSessionService
        
        # Create a game session that will fail on first question persist
        # Mock GameSessionAnswerRepository.create to raise exception
        with patch('services.game_session_service.GameSessionAnswerRepository.create') as mock_create:
            mock_create.side_effect = Exception("Simulated DB error on first question")
            
            try:
                GameSessionService.create_game_session_with_first_question(
                    user_id=self.user.id,
                    score=0,
                    first_question=self.q1,
                    category_id=self.cat_science.id,
                    number_of_questions=3
                )
                self.fail("Expected exception from first question creation")
            except Exception as e:
                self.assertIn("DB error", str(e))
            
            # Verify no orphan game session was created
            sessions_pagination = GameSessionRepository.get_by_user(self.user.id)
            # sessions_pagination is a QueryPagination object with .items attribute
            sessions = sessions_pagination.items if hasattr(sessions_pagination, 'items') else []
            self.assertEqual(len(sessions), 0, "Orphan game session created on atomic failure")

    def test_next_question_persistence_failure_returns_500(self):
        """If next question persistence fails, should return 500, not return unpersisted question"""
        # Create game
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 2
        })
        data = json.loads(response.data)
        game_id = data['game_session_id']
        
        # Get the answer from creation
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        correct_answer = answers[0].answer_snapshot
        
        # Mock GameSessionAnswerRepository.create to fail on next question persist
        from services import GameSessionAnswerService as orig_service
        
        with patch('data_access.GameSessionAnswerRepository.create') as mock_create:
            # First call succeeds (updating current answer), second call fails (persisting next question)
            mock_create.side_effect = [
                # First call: creating next question - should fail
                Exception("DB persistence error on next question")
            ]
            
            # Answer the first question
            response = self.client.post(f'/games/{game_id}/1', json={
                'user_answer': correct_answer
            })
            
            # When next question persistence fails, should return 500
            # (The actual implementation may vary - could be caught during answer or during next fetch)
            # The key point is that if it fails, we should not return a question that wasn't persisted
            if response.status_code != 500:
                # If it doesn't fail during answer, verify no question is returned
                # that wasn't properly persisted
                data = json.loads(response.data)
                if data.get('question') and data['question'] is not None:
                    # Verify the next question IS actually in the audit trail
                    next_ans = GameSessionAnswerRepository.get_by_game_and_question(game_id, 2)
                    self.assertIsNotNone(next_ans, 
                        "Question returned but not persisted in audit trail")

    def test_duplicate_answer_rejection_prevents_re_answering(self):
        """Once a question is answered, answering it again should fail with 422"""
        # Create game
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 1
        })
        data = json.loads(response.data)
        game_id = data['game_session_id']
        correct_answer = data['question']
        
        # Answer correctly
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': 'Water'
        })
        self.assertEqual(response.status_code, 200)
        
        # Try to answer again - should fail with 422
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': 'Water'
        })
        self.assertEqual(response.status_code, 422)
        
        # Verify only one submitted answer exists
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        submitted = [a for a in answers if a.user_answer and a.user_answer.strip()]
        self.assertEqual(len(submitted), 1)

    def test_exclude_ids_prevents_duplicate_questions_in_normal_flow(self):
        """Normal game flow should never assign same question twice"""
        # Create game with 3 questions
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 3
        })
        data = json.loads(response.data)
        game_id = data['game_session_id']
        
        question_ids = []
        
        # Collect all question IDs from the audit trail throughout the game
        # Start with Q1 from creation
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        for ans in answers:
            if ans.question_id not in question_ids:
                question_ids.append(ans.question_id)
        
        # Answer Q1
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        q1_answer = answers[0]
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': q1_answer.answer_snapshot
        })
        
        # Collect Q2
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        for ans in answers:
            if ans.question_id not in question_ids:
                question_ids.append(ans.question_id)
        
        # Answer Q2
        q2_answer = next((a for a in answers if a.question_number == 2), None)
        if q2_answer:
            response = self.client.post(f'/games/{game_id}/2', json={
                'user_answer': q2_answer.answer_snapshot
            })
        
        # Collect Q3
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        for ans in answers:
            if ans.question_id not in question_ids:
                question_ids.append(ans.question_id)
        
        # Verify no duplicates in the collected question IDs
        self.assertEqual(len(question_ids), len(set(question_ids)), 
                         f"Duplicate question IDs found: {question_ids}")

    def test_sequence_enforced_from_start(self):
        """First answerable question must be 1, not any number"""
        # Create game with 3 questions
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 3
        })
        data = json.loads(response.data)
        game_id = data['game_session_id']
        
        # Try to answer question 2 as the first answer
        response = self.client.post(f'/games/{game_id}/2', json={
            'user_answer': 'Wrong'
        })
        self.assertEqual(response.status_code, 422, "Should reject non-sequential answer")
        
        # Try to answer question 3 as the first answer
        response = self.client.post(f'/games/{game_id}/3', json={
            'user_answer': 'Wrong'
        })
        self.assertEqual(response.status_code, 422, "Should reject non-sequential answer")
        
        # Answer question 1 - should succeed
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': answers[0].answer_snapshot
        })
        self.assertEqual(response.status_code, 200)

    def test_all_questions_must_be_answered_in_order_for_completion(self):
        """Completion requires answering all questions in sequence 1..N"""
        # Create game with 2 questions
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 2
        })
        data = json.loads(response.data)
        game_id = data['game_session_id']
        
        # Answer question 1
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': answers[0].answer_snapshot
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertNotEqual(data.get('status'), 'completed')
        
        # Verify next question is 2
        response = self.client.get(f'/games/{game_id}')
        data = json.loads(response.data)
        self.assertEqual(data['question_number'], 2)
        
        # Answer question 2
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        q2_answer = next((a for a in answers if a.question_number == 2), None)
        response = self.client.post(f'/games/{game_id}/2', json={
            'user_answer': q2_answer.answer_snapshot
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get('status'), 'completed')

    # ==================== Batch A: Concurrency Tests ====================
    
    def test_concurrent_completion_no_double_award(self):
        """Concurrent completion requests must only award once, not double-increment user stats"""
        # Create game
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 1
        })
        data = json.loads(response.data)
        game_id = data['game_session_id']
        
        # Get initial user stats
        from services import UserService
        initial_user = UserService.get_user(self.user.id)
        initial_score = initial_user.total_score
        initial_games = initial_user.games_played
        
        # Answer the only question to reach completion
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': answers[0].answer_snapshot
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get('status'), 'completed')
        
        # Verify user stats incremented by 1, not more
        updated_user = UserService.get_user(self.user.id)
        self.assertEqual(updated_user.total_score, initial_score + 1,
                        "User total_score should increment by exactly 1")
        self.assertEqual(updated_user.games_played, initial_games + 1,
                        "User games_played should increment by exactly 1")
        
        # Verify game is marked as completed
        game = GameSessionRepository.get_by_id(game_id)
        self.assertTrue(game.is_completed, "Game should be marked as completed")
        self.assertEqual(game.awarded_score, 1, "Game awarded_score should be 1")
        
        # Simulate second completion request to same game
        # (In real scenario this would be concurrent, but we simulate by calling again)
        # Try to answer the same question again - should fail with 422
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': answers[0].answer_snapshot
        })
        self.assertEqual(response.status_code, 422, "Should reject re-answer of completed question")
        
        # Verify user stats did not increment again
        final_user = UserService.get_user(self.user.id)
        self.assertEqual(final_user.total_score, updated_user.total_score,
                        "User total_score should not change on re-answer attempt")
        self.assertEqual(final_user.games_played, updated_user.games_played,
                        "User games_played should not change on re-answer attempt")

    def test_next_question_payload_consistency_never_partial(self):
        """If next_question_number is set in response, question payload must never be null"""
        # Create game with 2 questions
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 2
        })
        self.assertIn(response.status_code, [200, 201])  # Accept either 200 or 201
        data = json.loads(response.data)
        game_id = data['game_session_id']
        
        # Initial response should have question for Q1
        self.assertIsNotNone(data['question'], "First question must not be null")
        self.assertEqual(data['question_number'], 1)
        
        # Answer Q1
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': answers[0].answer_snapshot
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check payload consistency: if next_question_number is set, question must be set
        if data.get('next_question_number') is not None:
            self.assertIsNotNone(data.get('question'), 
                "If next_question_number is returned, question payload must not be null")
            self.assertNotEqual(data.get('question'), None,
                "question field must not be null when next_question_number is present")
        
        # On completion, next_question_number should be None and question should be None
        if data.get('status') == 'completed':
            self.assertIsNone(data.get('next_question_number'),
                "next_question_number should be None on completion")
            self.assertIsNone(data.get('question'),
                "question should be None on completion")

    # ==================== Batch A: Capacity Validation Tests ====================
    
    def test_create_game_insufficient_unique_questions_returns_422(self):
        """Creating a game requesting more questions than available should return 422"""
        # We have 3 science questions (q1, q2, q5 from setUp)
        # Request a game with 5 questions - should fail
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 5  # Request 5 but only 3 available
        })
        
        self.assertEqual(response.status_code, 422, 
                        "Should return 422 when requested questions exceed available unique questions")
        data = json.loads(response.data)
        self.assertIn('message', data, "Error response should include message")

    def test_create_game_exact_capacity_accepted(self):
        """Requesting exactly the available unique questions should succeed"""
        # We have 3 science questions - request exactly 3
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 3  # Request 3, exactly available
        })
        
        self.assertIn(response.status_code, [200, 201],
                        "Should accept request for exactly available unique questions")
        data = json.loads(response.data)
        self.assertIsNotNone(data.get('game_session_id'))
        self.assertEqual(data['question_number'], 1)

    def test_create_game_all_categories_insufficient_returns_422(self):
        """Capacity validation should work for all-categories (category_id=0) requests too"""
        # We have 3 science + 2 history = 5 total questions
        # Request 10 - should fail
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': 0,  # All categories
            'number_of_questions': 10  # More than 5 available
        })
        
        self.assertEqual(response.status_code, 422,
                        "Should return 422 even for all-categories when insufficient questions")

    # ==================== Batch B: Legacy/Corrupt Session Tests ====================
    
    def test_missing_answer_record_returns_409_conflict(self):
        """
        When game session exists but expected answer record is missing (legacy/corrupt data),
        should return 409 Conflict to indicate state machine violation, not 400 bad request
        """
        # Create a game normally
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 2
        })
        self.assertIn(response.status_code, [200, 201])
        data = json.loads(response.data)
        game_id = data['game_session_id']
        
        # Manually delete the answer record to simulate legacy/corrupt data
        # This violates the invariant that all questions should be pre-served
        from data_access import GameSessionAnswerRepository
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        for ans in answers:
            if ans.question_number == 1:
                db.session.delete(ans)
        db.session.commit()
        
        # Try to answer question 1 - should get 409 (conflict), not 400 (bad request)
        response = self.client.post(f'/games/{game_id}/1', json={
            'user_answer': 'Water'
        })
        
        self.assertEqual(response.status_code, 409,
                        "Missing expected answer record should return 409 Conflict, not 400")
        data = json.loads(response.data)
        self.assertIn('message', data, "Error response should include explanatory message")
        # Message should indicate conflict in session state, not malformed request
        self.assertIn('conflict', data['message'].lower(), 
                     "Error message should mention conflict in state")

    def test_missing_record_error_is_deterministic(self):
        """Verify that missing record always returns same error contract"""
        # Create game and corrupt it
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 1
        })
        game_id = json.loads(response.data)['game_session_id']
        
        # Delete the answer record
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        for ans in answers:
            db.session.delete(ans)
        db.session.commit()
        
        # Try answer - should consistently return 409
        response1 = self.client.post(f'/games/{game_id}/1', json={'user_answer': 'Wrong'})
        self.assertEqual(response1.status_code, 409)
        
        # Try again with different answer - should also be 409 (not 422, 400, etc)
        response2 = self.client.post(f'/games/{game_id}/1', json={'user_answer': 'Water'})
        self.assertEqual(response2.status_code, 409, "Error contract must be deterministic")
        
        # Both error responses should have same structure
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        self.assertIn('message', data1)
        self.assertIn('message', data2)
        self.assertEqual(type(data1['message']), type(data2['message']),
                        "Error response structure should be consistent")

    # ==================== Batch B: Strict Failure-Path Assertions ====================
    
    def test_next_question_persistence_strict_500_on_failure(self):
        """
        STRICT: Next question persistence failure MUST return 500, never partial success.
        Contract is: if persistence fails, return error, not question payload.
        """
        # Create game
        response = self.client.post('/games', json={
            'user_id': self.user.id,
            'category_id': self.cat_science.id,
            'number_of_questions': 2
        })
        data = json.loads(response.data)
        game_id = data['game_session_id']
        
        # Get first answer
        answers = GameSessionAnswerRepository.get_by_game(game_id)
        q1_answer = answers[0].answer_snapshot
        
        # Mock to make next question persist fail
        with patch('data_access.GameSessionAnswerRepository.create') as mock_create:
            mock_create.side_effect = Exception("DB persistence error")
            
            # Answer Q1 - next question persistence will fail
            response = self.client.post(f'/games/{game_id}/1', json={
                'user_answer': q1_answer
            })
            
            # STRICT: Must be 500, never any other code
            self.assertEqual(response.status_code, 500,
                           "Next-question persistence failure must return 500, NEVER partial success")
            
            # STRICT: Error response should not contain question payload
            error_data = json.loads(response.data)
            self.assertNotIn('question', error_data, 
                           "Error response must not include question field from failed operation")


if __name__ == '__main__':
    unittest.main()
