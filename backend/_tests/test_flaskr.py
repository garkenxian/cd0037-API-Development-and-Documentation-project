import os
import sys
import unittest
from dotenv import load_dotenv

# Add backend directory to Python path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flaskr import create_app
from data_access.models import db, Question, Category

# Load environment variables
load_dotenv()


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        # Use SQLite in-memory database for tests (fast, no external dependencies)
        self.database_path = "sqlite:///:memory:"

        # Create app with the test configuration
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_app_created(self):
        """Test that the app is created successfully."""
        self.assertIsNotNone(self.app)
        self.assertIsNotNone(self.client)

    # TODO: Write at least one test for each test for successful operation and for expected errors.


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
