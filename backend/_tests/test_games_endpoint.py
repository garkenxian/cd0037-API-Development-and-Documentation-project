"""Integration tests for /games endpoint"""

import unittest
from unittest.mock import Mock, patch, MagicMock

import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flaskr import create_app
from data_access import db
from models import User, Category, Question, GameSession


# Stub GameSessionAnswerService for testing Phase 1b paths
class StubGameSessionAnswerService:
    """Stub service to test Phase 1b integration paths"""
    
    @staticmethod
    def store_initial_question(game_session_id, question_number, question):
        """Stub: store initial question"""
        pass
    
    @staticmethod
    def get_next_question_number(game_session_id):
        """Stub: get next question number"""
        return 1
    
    @staticmethod
    def get_by_game_and_question_number(game_session_id, question_number):
        """Stub: get question record"""
        mock_record = MagicMock()
        mock_record.get_question_format.return_value = {
            'id': 1,
            'question': 'Test Question?',
            'answer': 'Test Answer'
        }
        return mock_record
    
    @staticmethod
    def get_correct_count(game_session_id):
        """Stub: get correct count"""
        return 0
    
    @staticmethod
    def get_total_questions(game_session_id):
        """Stub: get total questions"""
        return 5
    
    @staticmethod
    def get_max_question_number(game_session_id):
        """Stub: get max question number"""
        return 5


class GamesEndpointUnitTests(unittest.TestCase):
    """Integration tests for /games endpoint"""

    def setUp(self):
        """Set up test app"""
        self.database_path = "sqlite:///:memory:"
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })

        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _create_test_data(self):
        """Helper to create test data"""
        # Create test user
        user = User(username='test_user', email='test@example.com')
        db.session.add(user)
        db.session.commit()
        
        # Create test category
        category = Category(type='Science')
        db.session.add(category)
        db.session.commit()
        
        # Create test question
        question = Question(
            question='What is H2O?',
            answer='Water',
            category=category.id,
            difficulty=2,
            rating=4.5
        )
        db.session.add(question)
        db.session.commit()
        
        return user, category, question

    def test_create_game_success(self):
        """Test successful game creation"""
        user, category, question = self._create_test_data()
        
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 5
            }
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('game_session_id', data)
        self.assertEqual(data['question_number'], 1)
        self.assertEqual(data['current_score']['correct'], 0)
        self.assertEqual(data['current_score']['total_questions'], 5)
        self.assertIn('question', data)
        self.assertEqual(data['question']['id'], question.id)

    def test_create_game_missing_user_id(self):
        """Test game creation fails with missing user_id"""
        response = self.client.post(
            '/games',
            json={
                'category_id': 1,
                'number_of_questions': 5
            }
        )
        
        self.assertEqual(response.status_code, 400)

    def test_create_game_invalid_user(self):
        """Test game creation fails with non-existent user"""
        response = self.client.post(
            '/games',
            json={
                'user_id': 9999,
                'category_id': 1,
                'number_of_questions': 5
            }
        )
        
        self.assertEqual(response.status_code, 404)

    def test_create_game_invalid_category(self):
        """Test game creation fails with non-existent category"""
        user, _, _ = self._create_test_data()
        
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': 9999,
                'number_of_questions': 5
            }
        )
        
        self.assertEqual(response.status_code, 404)

    def test_create_game_invalid_number_of_questions(self):
        """Test game creation fails with invalid number_of_questions"""
        user, category, _ = self._create_test_data()
        
        # Test with 0
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 0
            }
        )
        self.assertEqual(response.status_code, 422)
        
        # Test with 21 (too high)
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 21
            }
        )
        self.assertEqual(response.status_code, 422)

    def test_create_game_default_number_of_questions(self):
        """Test game creation uses default number_of_questions"""
        user, category, _ = self._create_test_data()
        
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id
            }
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['current_score']['total_questions'], 5)

    def test_get_game_success(self):
        """Test getting game session successfully"""
        user, category, _ = self._create_test_data()
        
        # Create game first
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 5
            }
        )
        game_session_id = response.get_json()['game_session_id']
        
        # Get game
        response = self.client.get(f'/games/{game_session_id}')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['game_session_id'], game_session_id)
        self.assertEqual(data['user_id'], user.id)
        self.assertEqual(data['category_id'], category.id)
        self.assertEqual(data['score'], 0)

    def test_get_game_not_found(self):
        """Test getting non-existent game"""
        response = self.client.get('/games/9999')
        
        self.assertEqual(response.status_code, 404)

    def test_answer_question_success(self):
        """Test answering a question - expects 501 until Phase 1b is implemented"""
        user, category, _ = self._create_test_data()
        
        # Create game
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 5
            }
        )
        game_session_id = response.get_json()['game_session_id']
        
        # Answer question - returns 501 (Not Implemented) until Phase 1b is ready
        # This prevents nondeterministic scoring bug
        response = self.client.post(
            f'/games/{game_session_id}/1',
            json={'user_answer': 'Water'}
        )
        
        self.assertEqual(response.status_code, 501)  # Not Implemented - Phase 1b required

    def test_answer_question_missing_answer(self):
        """Test answering question with missing user_answer"""
        user, category, _ = self._create_test_data()
        
        # Create game
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 5
            }
        )
        game_session_id = response.get_json()['game_session_id']
        
        # Try to answer without user_answer
        response = self.client.post(
            f'/games/{game_session_id}/1',
            json={}
        )
        
        self.assertEqual(response.status_code, 400)

    def test_answer_question_game_not_found(self):
        """Test answering question for non-existent game - validates game exists before Phase 1b check"""
        response = self.client.post(
            '/games/9999/1',
            json={'user_answer': 'Water'}
        )
        
        # Should get 404 because game validation happens before Phase 1b check
        self.assertEqual(response.status_code, 404)

    def test_create_game_empty_body(self):
        """Test game creation with empty request body"""
        response = self.client.post('/games', json={})
        self.assertEqual(response.status_code, 400)

    def test_create_game_number_of_questions_not_integer(self):
        """Test game creation with non-integer number_of_questions"""
        user, category, _ = self._create_test_data()
        
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 'five'  # String instead of int
            }
        )
        
        self.assertEqual(response.status_code, 422)

    def test_create_game_with_zero_category(self):
        """Test game creation with category_id=0 (selects from all categories)"""
        user, _, _ = self._create_test_data()
        
        # category_id=0 is treated like None in the endpoint
        # The code checks: if category_id is not None and category_id != 0
        # So 0 skips validation and succeeds
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': 0,  # 0 means "all categories" and should succeed
                'number_of_questions': 5
            }
        )
        
        # Should succeed because category_id=0 is special-cased to mean "all categories"
        self.assertEqual(response.status_code, 201)

    def test_create_game_no_category_provided(self):
        """Test game creation without category_id (defaults to all categories)"""
        user, _, _ = self._create_test_data()
        
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'number_of_questions': 5
            }
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertTrue(data['success'])

    def test_get_game_fallback_path(self):
        """Test GET /games/:id returns fallback response (Phase 1b not available)"""
        user, category, _ = self._create_test_data()
        
        # Create game
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 5
            }
        )
        game_session_id = response.get_json()['game_session_id']
        
        # Get game - should return basic info since Phase 1b not available
        response = self.client.get(f'/games/{game_session_id}')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('note', data)
        self.assertIn('Phase 1b', data['note'])
        self.assertIn('game_session_id', data)
        self.assertIn('user_id', data)
        self.assertIn('category_id', data)
        self.assertIn('score', data)

    def test_answer_question_phase_1b_gate(self):
        """Test that answer_question blocks with 501 when Phase 1b not available"""
        user, category, _ = self._create_test_data()
        
        # Create game
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 5
            }
        )
        game_session_id = response.get_json()['game_session_id']
        
        # Answer question should get 501 (Not Implemented) until Phase 1b ready
        response = self.client.post(
            f'/games/{game_session_id}/1',
            json={'user_answer': 'Test Answer'}
        )
        
        self.assertEqual(response.status_code, 501)

    def test_create_game_with_minimum_questions(self):
        """Test game creation with minimum number of questions (1)"""
        user, category, _ = self._create_test_data()
        
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 1
            }
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['current_score']['total_questions'], 1)

    def test_create_game_with_maximum_questions(self):
        """Test game creation with maximum number of questions (20)"""
        user, category, _ = self._create_test_data()
        
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 20
            }
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['current_score']['total_questions'], 20)

    def test_create_game_negative_questions(self):
        """Test game creation fails with negative number_of_questions"""
        user, category, _ = self._create_test_data()
        
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': -5
            }
        )
        
        self.assertEqual(response.status_code, 422)

    def test_answer_question_no_json_body(self):
        """Test answering question with no JSON body"""
        user, category, _ = self._create_test_data()
        
        # Create game
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 5
            }
        )
        game_session_id = response.get_json()['game_session_id']
        
        # Try to answer without JSON body
        response = self.client.post(f'/games/{game_session_id}/1', json=None)
        
        # Flask returns 415 when Content-Type mismatch, not our 400
        self.assertIn(response.status_code, [400, 415])

    def test_create_game_with_phase_1b_available(self):
        """Test POST /games calls Phase 1b when available"""
        user, category, _ = self._create_test_data()
        
        # Patch the controllers.games module to have Phase 1b available
        with patch.dict('sys.modules', {'services': MagicMock()}):
            # Import after patching
            import importlib
            import controllers.games
            
            # Store original values
            original_phase_1b = controllers.games.PHASE_1B_AVAILABLE
            original_service = None
            if hasattr(controllers.games, 'GameSessionAnswerService'):
                original_service = controllers.games.GameSessionAnswerService
            
            try:
                # Set Phase 1b as available and provide stub service
                controllers.games.PHASE_1B_AVAILABLE = True
                controllers.games.GameSessionAnswerService = StubGameSessionAnswerService
                
                # Make request
                response = self.client.post(
                    '/games',
                    json={
                        'user_id': user.id,
                        'category_id': category.id,
                        'number_of_questions': 5
                    }
                )
                
                self.assertEqual(response.status_code, 201)
                data = response.get_json()
                self.assertTrue(data['success'])
                self.assertIn('game_session_id', data)
            finally:
                # Restore original values
                controllers.games.PHASE_1B_AVAILABLE = original_phase_1b
                if original_service:
                    controllers.games.GameSessionAnswerService = original_service
                elif hasattr(controllers.games, 'GameSessionAnswerService'):
                    delattr(controllers.games, 'GameSessionAnswerService')

    def test_get_game_with_phase_1b_available_in_progress(self):
        """Test GET /games with Phase 1b in progress game"""
        user, category, _ = self._create_test_data()
        
        # Create game first
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 5
            }
        )
        game_session_id = response.get_json()['game_session_id']
        
        # Patch Phase 1b
        import controllers.games
        original_phase_1b = controllers.games.PHASE_1B_AVAILABLE
        original_service = getattr(controllers.games, 'GameSessionAnswerService', None)
        
        try:
            controllers.games.PHASE_1B_AVAILABLE = True
            controllers.games.GameSessionAnswerService = StubGameSessionAnswerService
            
            # Get game - should use Phase 1b path
            response = self.client.get(f'/games/{game_session_id}')
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['success'])
            self.assertIn('question_number', data)
            self.assertEqual(data['current_score']['correct'], 0)
            self.assertEqual(data['current_score']['total_questions'], 5)
        finally:
            controllers.games.PHASE_1B_AVAILABLE = original_phase_1b
            if original_service:
                controllers.games.GameSessionAnswerService = original_service
            elif hasattr(controllers.games, 'GameSessionAnswerService'):
                delattr(controllers.games, 'GameSessionAnswerService')

    def test_get_game_with_phase_1b_available_completed(self):
        """Test GET /games with Phase 1b when game is completed"""
        user, category, _ = self._create_test_data()
        
        # Create game
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 5
            }
        )
        game_session_id = response.get_json()['game_session_id']
        
        # Patch Phase 1b with custom stub for completed game
        import controllers.games
        original_phase_1b = controllers.games.PHASE_1B_AVAILABLE
        original_service = getattr(controllers.games, 'GameSessionAnswerService', None)
        
        try:
            # Create custom stub that indicates game is completed
            class CompletedGameStub(StubGameSessionAnswerService):
                @staticmethod
                def get_next_question_number(game_session_id):
                    return 6  # Beyond total questions
                
                @staticmethod
                def get_by_game_and_question_number(game_session_id, question_number):
                    return None  # No more questions
                
                @staticmethod
                def get_max_question_number(game_session_id):
                    return 5
            
            controllers.games.PHASE_1B_AVAILABLE = True
            controllers.games.GameSessionAnswerService = CompletedGameStub
            
            # Get game - should return completion status
            response = self.client.get(f'/games/{game_session_id}')
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['success'])
            self.assertEqual(data['status'], 'completed')
            self.assertEqual(data['current_score']['correct'], 0)
        finally:
            controllers.games.PHASE_1B_AVAILABLE = original_phase_1b
            if original_service:
                controllers.games.GameSessionAnswerService = original_service
            elif hasattr(controllers.games, 'GameSessionAnswerService'):
                delattr(controllers.games, 'GameSessionAnswerService')

    def test_answer_question_with_phase_1b_available(self):
        """Test POST /games/:id/:question_number with Phase 1b available"""
        user, category, _ = self._create_test_data()
        
        # Create game
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 5
            }
        )
        game_session_id = response.get_json()['game_session_id']
        
        # Patch Phase 1b
        import controllers.games
        original_phase_1b = controllers.games.PHASE_1B_AVAILABLE
        original_service = getattr(controllers.games, 'GameSessionAnswerService', None)
        
        try:
            # Create stub with answer logic
            class AnswerStub(StubGameSessionAnswerService):
                @staticmethod
                def get_by_game_and_question_number(game_session_id, question_number):
                    if question_number == 1:
                        # Current question (being answered)
                        mock_record = MagicMock()
                        mock_record.is_already_answered.return_value = False
                        mock_record.correct_answer = 'Test Answer'
                        mock_record.record_user_answer = MagicMock()
                        return mock_record
                    elif question_number == 2:
                        # Next question exists
                        mock_next = MagicMock()
                        mock_next.get_question_format.return_value = {
                            'id': 2,
                            'question': 'Next Question?',
                            'category': 1,
                            'difficulty': 2,
                            'rating': 4.0
                        }
                        return mock_next
                    return None
                
                @staticmethod
                def get_correct_count(game_session_id):
                    return 1
                
                @staticmethod
                def get_total_questions(game_session_id):
                    return 5
            
            controllers.games.PHASE_1B_AVAILABLE = True
            controllers.games.GameSessionAnswerService = AnswerStub
            
            # Answer question
            response = self.client.post(
                f'/games/{game_session_id}/1',
                json={'user_answer': 'Test Answer'}
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['success'])
            self.assertTrue(data['correct'])  # Correct answer
            self.assertEqual(data['answered_question_number'], 1)
            self.assertEqual(data['next_question_number'], 2)
            self.assertIn('question', data)
        finally:
            controllers.games.PHASE_1B_AVAILABLE = original_phase_1b
            if original_service:
                controllers.games.GameSessionAnswerService = original_service
            elif hasattr(controllers.games, 'GameSessionAnswerService'):
                delattr(controllers.games, 'GameSessionAnswerService')

    def test_answer_question_incorrect_with_phase_1b(self):
        """Test POST /games/:id/:question_number with incorrect answer and Phase 1b"""
        user, category, _ = self._create_test_data()
        
        # Create game
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 5
            }
        )
        game_session_id = response.get_json()['game_session_id']
        
        # Patch Phase 1b
        import controllers.games
        original_phase_1b = controllers.games.PHASE_1B_AVAILABLE
        original_service = getattr(controllers.games, 'GameSessionAnswerService', None)
        
        try:
            class AnswerStub(StubGameSessionAnswerService):
                @staticmethod
                def get_by_game_and_question_number(game_session_id, question_number):
                    if question_number == 1:
                        # Current question (being answered)
                        mock_record = MagicMock()
                        mock_record.is_already_answered.return_value = False
                        mock_record.correct_answer = 'Correct Answer'
                        mock_record.record_user_answer = MagicMock()
                        return mock_record
                    elif question_number == 2:
                        # Next question exists
                        mock_next = MagicMock()
                        mock_next.get_question_format.return_value = {
                            'id': 3,
                            'question': 'Next Question?',
                            'category': 1,
                            'difficulty': 2,
                            'rating': 4.0
                        }
                        return mock_next
                    return None
                
                @staticmethod
                def get_correct_count(game_session_id):
                    return 0  # No correct answers yet
                
                @staticmethod
                def get_total_questions(game_session_id):
                    return 5
            
            controllers.games.PHASE_1B_AVAILABLE = True
            controllers.games.GameSessionAnswerService = AnswerStub
            
            # Answer question with wrong answer
            response = self.client.post(
                f'/games/{game_session_id}/1',
                json={'user_answer': 'Wrong Answer'}
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertTrue(data['success'])
            self.assertFalse(data['correct'])  # Incorrect answer
            self.assertEqual(data['correct_answer'], 'Correct Answer')
            self.assertEqual(data['answered_question_number'], 1)
            self.assertEqual(data['next_question_number'], 2)
        finally:
            controllers.games.PHASE_1B_AVAILABLE = original_phase_1b
            if original_service:
                controllers.games.GameSessionAnswerService = original_service
            elif hasattr(controllers.games, 'GameSessionAnswerService'):
                delattr(controllers.games, 'GameSessionAnswerService')

    def test_answer_question_already_answered_with_phase_1b(self):
        """Test POST /games/:id/:question_number when already answered"""
        user, category, _ = self._create_test_data()
        
        # Create game
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 5
            }
        )
        game_session_id = response.get_json()['game_session_id']
        
        # Patch Phase 1b
        import controllers.games
        original_phase_1b = controllers.games.PHASE_1B_AVAILABLE
        original_service = getattr(controllers.games, 'GameSessionAnswerService', None)
        
        try:
            class AnswerStub(StubGameSessionAnswerService):
                @staticmethod
                def get_by_game_and_question_number(game_session_id, question_number):
                    mock_record = MagicMock()
                    mock_record.is_already_answered.return_value = True  # Already answered
                    return mock_record
            
            controllers.games.PHASE_1B_AVAILABLE = True
            controllers.games.GameSessionAnswerService = AnswerStub
            
            # Try to answer question again
            response = self.client.post(
                f'/games/{game_session_id}/1',
                json={'user_answer': 'Test Answer'}
            )
            
            self.assertEqual(response.status_code, 422)  # Unprocessable entity
        finally:
            controllers.games.PHASE_1B_AVAILABLE = original_phase_1b
            if original_service:
                controllers.games.GameSessionAnswerService = original_service
            elif hasattr(controllers.games, 'GameSessionAnswerService'):
                delattr(controllers.games, 'GameSessionAnswerService')

    def test_answer_question_not_served_with_phase_1b(self):
        """Test POST /games/:id/:question_number for question never served"""
        user, category, _ = self._create_test_data()
        
        # Create game
        response = self.client.post(
            '/games',
            json={
                'user_id': user.id,
                'category_id': category.id,
                'number_of_questions': 5
            }
        )
        game_session_id = response.get_json()['game_session_id']
        
        # Patch Phase 1b
        import controllers.games
        original_phase_1b = controllers.games.PHASE_1B_AVAILABLE
        original_service = getattr(controllers.games, 'GameSessionAnswerService', None)
        
        try:
            class AnswerStub(StubGameSessionAnswerService):
                @staticmethod
                def get_by_game_and_question_number(game_session_id, question_number):
                    return None  # Question never served
            
            controllers.games.PHASE_1B_AVAILABLE = True
            controllers.games.GameSessionAnswerService = AnswerStub
            
            # Try to answer question that was never served
            response = self.client.post(
                f'/games/{game_session_id}/99',
                json={'user_answer': 'Test Answer'}
            )
            
            self.assertEqual(response.status_code, 404)
        finally:
            controllers.games.PHASE_1B_AVAILABLE = original_phase_1b
            if original_service:
                controllers.games.GameSessionAnswerService = original_service
            elif hasattr(controllers.games, 'GameSessionAnswerService'):
                delattr(controllers.games, 'GameSessionAnswerService')


if __name__ == '__main__':
    unittest.main()
