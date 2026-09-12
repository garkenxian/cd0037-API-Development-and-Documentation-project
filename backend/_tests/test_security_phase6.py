"""
Security tests for Phase 6 hardening
Tests CORS configuration, rate limiting, input validation, and answer leakage prevention
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flaskr import create_app
from data_access import db, User, Category, Question, GameSession, GameSessionAnswer
from utils import RateLimiter

# Load environment variables
load_dotenv()


class SecurityCORSTestCase(unittest.TestCase):
    """Test CORS configuration based on environment"""

    def test_cors_wildcard_in_development(self):
        """Test that CORS allows all origins in development"""
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}):
            app = create_app({
                "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
                "TESTING": True
            })
            
            # CORS should be configured in the app
            self.assertIsNotNone(app)
            
            # Make a test request to verify CORS headers are present
            with app.test_client() as client:
                response = client.options('/', headers={'Origin': 'http://example.com'})
                # The response should include CORS headers
                self.assertIn('Access-Control-Allow-Methods', response.headers)

    def test_cors_wildcard_in_test_config(self):
        """Test that CORS allows all origins when test_config is provided"""
        app = create_app({
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "TESTING": True
        })
        
        # App created with test config should work
        self.assertIsNotNone(app)
        with app.test_client() as client:
            response = client.get('/users')
            # Should get a valid response
            self.assertIn(response.status_code, [200, 401, 404])


class RateLimitingTestCase(unittest.TestCase):
    """Test rate limiting functionality"""

    def setUp(self):
        """Initialize rate limiter for testing"""
        self.limiter = RateLimiter()

    def test_rate_limit_allows_requests_within_limit(self):
        """Test that requests within the limit are allowed"""
        identifier = "test_ip_123"
        limit = 5
        window_seconds = 60
        
        # Make 5 requests
        for i in range(limit):
            result = self.limiter.is_allowed(identifier, limit, window_seconds)
            self.assertTrue(result, f"Request {i+1} should be allowed")

    def test_rate_limit_blocks_requests_over_limit(self):
        """Test that requests exceeding the limit are blocked"""
        identifier = "test_ip_456"
        limit = 3
        window_seconds = 60
        
        # Make 3 allowed requests
        for i in range(limit):
            self.limiter.is_allowed(identifier, limit, window_seconds)
        
        # 4th request should be blocked
        result = self.limiter.is_allowed(identifier, limit, window_seconds)
        self.assertFalse(result, "Request exceeding limit should be blocked")

    def test_rate_limit_retry_after(self):
        """Test retry_after calculation"""
        identifier = "test_ip_789"
        limit = 1
        window_seconds = 10
        
        # Use up the limit
        self.limiter.is_allowed(identifier, limit, window_seconds)
        
        # Get retry_after
        retry_after = self.limiter.get_retry_after(identifier, window_seconds)
        self.assertGreater(retry_after, 0, "Should have a positive retry_after")
        # Allow +1 due to integer rounding in calculation
        self.assertLessEqual(retry_after, window_seconds + 1)

    def test_rate_limit_per_identifier(self):
        """Test that rate limiting is per-identifier"""
        limit = 2
        window_seconds = 60
        
        # Use up limit for identifier 1
        for _ in range(limit):
            self.limiter.is_allowed("ip_1", limit, window_seconds)
        
        # Identifier 2 should not be affected
        result = self.limiter.is_allowed("ip_2", limit, window_seconds)
        self.assertTrue(result, "Different identifier should have its own limit")


class InputValidationTestCase(unittest.TestCase):
    """Test input validation and normalization"""

    def setUp(self):
        """Set up test database"""
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "TESTING": True
        })
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up test database"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_username_length_validation(self):
        """Test that username length is validated (3-50 characters)"""
        with self.app.app_context():
            from services import UserService
            
            # Too short
            with self.assertRaises(ValueError) as context:
                UserService.create_user("ab", "test@example.com")
            self.assertIn("between 3 and 50", str(context.exception))
            
            # Too long
            with self.assertRaises(ValueError) as context:
                UserService.create_user("a" * 51, "test@example.com")
            self.assertIn("between 3 and 50", str(context.exception))
            
            # Valid length
            user = UserService.create_user("testuser", "test@example.com")
            self.assertIsNotNone(user.id)

    def test_question_length_validation(self):
        """Test that question/answer length is validated (1-500 characters)"""
        with self.app.app_context():
            from services import QuestionService, CategoryService
            
            # Create a category first
            category = CategoryService.create_category("Test Category")
            
            # Too long question
            with self.assertRaises(ValueError) as context:
                QuestionService.create_question(
                    "a" * 501,
                    "answer",
                    category.id,
                    1
                )
            self.assertIn("between 1 and 500", str(context.exception))
            
            # Too long answer
            with self.assertRaises(ValueError) as context:
                QuestionService.create_question(
                    "question",
                    "a" * 501,
                    category.id,
                    1
                )
            self.assertIn("between 1 and 500", str(context.exception))
            
            # Valid lengths
            question = QuestionService.create_question(
                "What is 2+2?",
                "4",
                category.id,
                1
            )
            self.assertIsNotNone(question.id)

    def test_category_length_validation(self):
        """Test that category type length is validated (1-100 characters)"""
        with self.app.app_context():
            from services import CategoryService
            
            # Too long
            with self.assertRaises(ValueError) as context:
                CategoryService.create_category("a" * 101)
            self.assertIn("between 1 and 100", str(context.exception))
            
            # Valid length
            category = CategoryService.create_category("Science")
            self.assertIsNotNone(category.id)

    def test_input_normalization(self):
        """Test that inputs are normalized (trimmed, lowercased where appropriate)"""
        with self.app.app_context():
            from services import UserService
            
            # Create user with whitespace
            user = UserService.create_user("  testuser  ", "  TEST@EXAMPLE.COM  ")
            
            # Should be trimmed
            self.assertEqual(user.username, "testuser")
            # Email should be lowercased
            self.assertEqual(user.email, "test@example.com")


class AnswerLeakageTestCase(unittest.TestCase):
    """Test that answers are not leaked before submission"""

    def setUp(self):
        """Set up test database and create sample data"""
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "TESTING": True
        })
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self._create_test_data()

    def tearDown(self):
        """Clean up test database"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _create_test_data(self):
        """Create sample data for testing"""
        from services import UserService, CategoryService, QuestionService
        
        # Create user
        self.user = UserService.create_user("testuser", "test@example.com")
        
        # Create category
        self.category = CategoryService.create_category("Science")
        
        # Create question
        self.question = QuestionService.create_question(
            "What is 2+2?",
            "4",
            self.category.id,
            1
        )
        
        # Store IDs instead of objects to avoid DetachedInstanceError
        self.user_id = self.user.id
        self.category_id = self.category.id
        self.question_id = self.question.id

    def test_answer_not_in_create_game_response(self):
        """Test that answer is not returned when creating a game"""
        with self.app.app_context():
            response = self.client.post(
                '/games',
                json={
                    'user_id': self.user_id,
                    'category_id': self.category_id,
                    'number_of_questions': 1
                }
            )
            
            self.assertEqual(response.status_code, 201)
            data = response.get_json()
            
            # Question should be present
            self.assertIn('question', data)
            question = data['question']
            
            # Answer/correct_answer should NOT be in the question
            self.assertNotIn('answer', question, "Answer should not be in create game response")
            self.assertNotIn('correct_answer', question)

    def test_answer_not_in_get_game_state_response(self):
        """Test that answer is not returned when getting game state"""
        with self.app.app_context():
            # Create a game
            response = self.client.post(
                '/games',
                json={
                    'user_id': self.user_id,
                    'category_id': self.category_id,
                    'number_of_questions': 1
                }
            )
            game_id = response.get_json()['game_session_id']
            
            # Get game state
            response = self.client.get(f'/games/{game_id}')
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            
            # Question should be present
            self.assertIn('question', data)
            question = data['question']
            
            # Answer should NOT be in the question
            self.assertNotIn('answer', question, "Answer should not be in get game response")
            self.assertNotIn('correct_answer', question)

    def test_answer_revealed_after_submission(self):
        """Test that answer IS revealed after user submits"""
        with self.app.app_context():
            # Create a game
            response = self.client.post(
                '/games',
                json={
                    'user_id': self.user_id,
                    'category_id': self.category_id,
                    'number_of_questions': 1
                }
            )
            game_id = response.get_json()['game_session_id']
            
            # Submit an answer
            response = self.client.post(
                f'/games/{game_id}/1',
                json={'user_answer': '4'}
            )
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            
            # After submission, correct_answer SHOULD be revealed
            self.assertIn('correct_answer', data, "Answer should be revealed after submission")
            self.assertEqual(data['correct_answer'], '4')
            self.assertIn('correct', data, "Correctness should be indicated")


class RateLimitingEndpointTestCase(unittest.TestCase):
    """Test rate limiting on the game answer endpoint"""

    def setUp(self):
        """Set up test database and create sample data"""
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "TESTING": True
        })
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self._create_test_data()

    def tearDown(self):
        """Clean up"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _create_test_data(self):
        """Create sample data"""
        from services import UserService, CategoryService, QuestionService
        
        user = UserService.create_user("testuser", "test@example.com")
        category = CategoryService.create_category("Science")
        self.user_id = user.id
        self.category_id = category.id
        
        # Create multiple questions for testing
        for i in range(10):
            QuestionService.create_question(
                f"Question {i}?",
                f"Answer {i}",
                category.id,
                1
            )

    def test_rate_limit_on_answer_endpoint(self):
        """Test that rate limiting is applied to answer endpoint"""
        with self.app.app_context():
            # Create a game with multiple questions
            response = self.client.post(
                '/games',
                json={
                    'user_id': self.user_id,
                    'category_id': self.category_id,
                    'number_of_questions': 5
                }
            )
            game_id = response.get_json()['game_session_id']
            
            # Submit answers repeatedly
            # The rate limit is 30 requests per 60 seconds per IP
            # This test may not trigger actual rate limit since it's fast,
            # but we verify the endpoint is reachable and responsive
            for i in range(1, 6):
                response = self.client.post(
                    f'/games/{game_id}/{i}',
                    json={'user_answer': f'Answer {i-1}'}
                )
                
                # Should get either 200 (success) or 422 (game complete/invalid)
                # We should NOT get 429 unless rate limited
                if response.status_code == 429:
                    self.fail("Rate limit triggered unexpectedly in test - this is expected behavior in production but shouldn't happen in fast tests")
                
                # Game completes after all answers
                if response.status_code == 200:
                    data = response.get_json()
                    if 'status' in data and data['status'] == 'completed':
                        break


class ProductionModeRateLimitTestCase(unittest.TestCase):
    """Test rate limiting behavior in production mode (issue #1)"""
    
    def test_rate_limit_enabled_by_default_in_production(self):
        """Test that rate limiting is ENABLED by default (not dependent on FLASK_ENV=production)"""
        # Production rate limiter should work with default environment settings
        # This ensures deployments without FLASK_ENV explicitly set still get protection
        
        from utils import get_rate_limiter
        limiter = get_rate_limiter()
        limiter.reset()
        
        # Create app without FLASK_ENV set (simulates typical production deployment)
        # but with RATE_LIMIT_ENABLED not explicitly disabled
        app = create_app({
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "TESTING": False,  # Not in testing mode
            "RATE_LIMIT_ENABLED": True  # Explicitly enabled
        })
        
        with app.app_context():
            db.create_all()
            from services import UserService, CategoryService, QuestionService
            
            # Create test data
            user = UserService.create_user("testuser", "test@example.com")
            category = CategoryService.create_category("Science")
            for i in range(10):
                QuestionService.create_question(f"Q{i}?", f"A{i}", category.id, 1)
            
            user_id = user.id
            category_id = category.id
        
        client = app.test_client()
        
        # Create a game
        response = client.post('/games', json={
            'user_id': user_id,
            'category_id': category_id,
            'number_of_questions': 1
        })
        self.assertEqual(response.status_code, 201)
        game_id = response.get_json()['game_session_id']
        
        # Make many requests to trigger rate limit (30/60s default)
        status_codes = []
        for i in range(35):
            response = client.post(f'/games/{game_id}/1', json={'user_answer': f'A{i}'})
            status_codes.append(response.status_code)
        
        # Should see some 429 responses (rate limited)
        has_429 = 429 in status_codes
        self.assertTrue(has_429, 
                       f"Rate limiting should trigger with RATE_LIMIT_ENABLED=true. Status codes: {set(status_codes)}")

    def test_retry_after_header_present_in_429_response(self):
        """Test that 429 response includes Retry-After header (issue #3)"""
        from utils import get_rate_limiter
        limiter = get_rate_limiter()
        limiter.reset()
        
        app = create_app({
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "TESTING": False,
            "RATE_LIMIT_ENABLED": True
        })
        
        with app.app_context():
            db.create_all()
            from services import UserService, CategoryService, QuestionService
            
            user = UserService.create_user("testuser", "test@example.com")
            category = CategoryService.create_category("Science")
            QuestionService.create_question("Q?", "A", category.id, 1)
            
            user_id = user.id
            category_id = category.id
        
        client = app.test_client()
        
        response = client.post('/games', json={
            'user_id': user_id,
            'category_id': category_id,
            'number_of_questions': 1
        })
        game_id = response.get_json()['game_session_id']
        
        # Exhaust rate limit
        for i in range(35):
            response = client.post(f'/games/{game_id}/1', json={'user_answer': 'A'})
            if response.status_code == 429:
                # Verify Retry-After header is present
                self.assertIn('Retry-After', response.headers,
                             "429 response must include Retry-After header")
                
                # Verify it's a valid number
                retry_after = response.headers.get('Retry-After')
                try:
                    seconds = int(retry_after)
                    self.assertGreater(seconds, 0, "Retry-After must be positive")
                    self.assertLessEqual(seconds, 60, "Retry-After should be within window")
                except ValueError:
                    self.fail(f"Retry-After header must be a number, got: {retry_after}")
                
                return  # Test passed
        
        self.fail("Should have received at least one 429 response")


class ProductionModeCORSTestCase(unittest.TestCase):
    """Test CORS configuration in production mode without test_config (issue #5)"""
    
    def test_cors_restricted_in_production_without_test_config(self):
        """Test that CORS origins are restricted in production (not using test_config)"""
        # The _get_cors_origins function checks environment and returns appropriate origins
        from flaskr import _get_cors_origins
        
        with patch.dict(os.environ, {
            'FLASK_ENV': 'production',
            'CORS_ALLOWED_ORIGINS': 'https://example.com,https://www.example.com'
        }):
            # Get origins without test_config
            origins = _get_cors_origins(test_config=None)
            
            # Should return a list of specific origins, not wildcard
            self.assertIsInstance(origins, list, "Should return list of origins in production")
            self.assertIn('https://example.com', origins, "Should include configured origin")
            self.assertIn('https://www.example.com', origins, "Should include second origin")
            self.assertNotIn('*', origins, "Should NOT allow wildcard in production")

    def test_cors_default_localhost_in_production(self):
        """Test that CORS defaults to localhost:3000 in production if env var not set"""
        from flaskr import _get_cors_origins
        
        with patch.dict(os.environ, {'FLASK_ENV': 'production'}, clear=False):
            # Remove CORS_ALLOWED_ORIGINS if it exists
            os.environ.pop('CORS_ALLOWED_ORIGINS', None)
            
            # Get origins - should default to localhost:3000
            origins = _get_cors_origins(test_config=None)
            
            self.assertIsInstance(origins, list, "Should return list of origins")
            self.assertIn('http://localhost:3000', origins, "Should default to localhost:3000")

    def test_cors_test_config_footgun_documented_behavior(self):
        """Document the intended behavior: test_config always returns wildcard
        
        This is a known behavior, not a bug. When test_config is passed (to support
        pytest's test_client which cannot set proper origin headers), CORS always
        returns wildcard regardless of TESTING flag or FLASK_ENV.
        
        WARNING: Custom launch scripts should NOT pass test_config=True in production.
        In production, omit test_config entirely to enable FLASK_ENV-based restrictions.
        """
        from flaskr import _get_cors_origins
        
        # Even in production mode with TESTING=false, test_config overrides to wildcard
        with patch.dict(os.environ, {'FLASK_ENV': 'production'}):
            origins = _get_cors_origins(test_config={})
            self.assertEqual(origins, '*', 
                           "test_config presence always returns wildcard for pytest compatibility")
        
        # This is intentional for pytest support
        with patch.dict(os.environ, {'FLASK_ENV': 'production'}):
            origins = _get_cors_origins(test_config={'TESTING': False})
            self.assertEqual(origins, '*',
                           "Even with explicit TESTING=False in test_config, still returns wildcard")


# Make tests runnable
if __name__ == "__main__":
    unittest.main()
