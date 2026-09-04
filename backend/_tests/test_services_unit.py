"""
Unit tests for service layer
Tests business logic and validation in isolation with mocked repositories
"""

import unittest
from unittest.mock import Mock, patch, MagicMock

import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import UserService, CategoryService, QuestionService, GameSessionService


class UserServiceUnitTests(unittest.TestCase):
    """Unit tests for UserService - mock repositories and db"""

    @patch('services.user_service.db')
    @patch('services.user_service.UserRepository')
    def test_create_user_validates_empty_username(self, mock_repo, mock_db):
        """Test that create_user validates empty username"""
        with self.assertRaises(ValueError) as context:
            UserService.create_user('', 'test@example.com')
        
        self.assertIn('empty', str(context.exception).lower())

    @patch('services.user_service.db')
    @patch('services.user_service.UserRepository')
    def test_create_user_validates_short_username(self, mock_repo, mock_db):
        """Test that create_user validates username length"""
        with self.assertRaises(ValueError) as context:
            UserService.create_user('ab', 'test@example.com')
        
        self.assertIn('3 characters', str(context.exception))

    @patch('services.user_service.db')
    @patch('services.user_service.UserRepository')
    def test_create_user_validates_invalid_email(self, mock_repo, mock_db):
        """Test that create_user validates email format"""
        with self.assertRaises(ValueError) as context:
            UserService.create_user('testuser', 'notanemail')
        
        self.assertIn('email', str(context.exception).lower())

    @patch('services.user_service.db')
    @patch('services.user_service.UserRepository')
    def test_create_user_checks_username_uniqueness(self, mock_repo, mock_db):
        """Test that create_user checks if username already exists"""
        mock_repo.exists_by_username.return_value = True
        
        with self.assertRaises(ValueError) as context:
            UserService.create_user('duplicate', 'new@example.com')
        
        self.assertIn('already exists', str(context.exception).lower())
        mock_repo.exists_by_username.assert_called_once_with('duplicate')

    @patch('services.user_service.db')
    @patch('services.user_service.UserRepository')
    def test_create_user_checks_email_uniqueness(self, mock_repo, mock_db):
        """Test that create_user checks if email already exists"""
        mock_repo.exists_by_username.return_value = False
        mock_repo.exists_by_email.return_value = True
        
        with self.assertRaises(ValueError) as context:
            UserService.create_user('newuser', 'duplicate@example.com')
        
        self.assertIn('already registered', str(context.exception).lower())
        mock_repo.exists_by_email.assert_called_once_with('duplicate@example.com')

    @patch('services.user_service.db')
    @patch('services.user_service.UserRepository')
    def test_create_user_commits_on_success(self, mock_repo, mock_db):
        """Test that create_user commits transaction on success"""
        mock_repo.exists_by_username.return_value = False
        mock_repo.exists_by_email.return_value = False
        mock_user = Mock()
        mock_repo.create.return_value = mock_user
        
        result = UserService.create_user('newuser', 'new@example.com')
        
        # Verify commit was called
        mock_db.session.commit.assert_called_once()
        self.assertEqual(result, mock_user)

    @patch('services.user_service.db')
    @patch('services.user_service.UserRepository')
    def test_create_user_rollsback_on_commit_error(self, mock_repo, mock_db):
        """Test that create_user rollsback on commit failure"""
        mock_repo.exists_by_username.return_value = False
        mock_repo.exists_by_email.return_value = False
        mock_repo.create.return_value = Mock()
        mock_db.session.commit.side_effect = Exception("DB Error")
        
        with self.assertRaises(ValueError):
            UserService.create_user('newuser', 'new@example.com')
        
        # Verify rollback was called
        mock_db.session.rollback.assert_called_once()

    @patch('services.user_service.UserRepository')
    def test_get_user_returns_user(self, mock_repo):
        """Test that get_user returns user when found"""
        mock_user = Mock()
        mock_repo.get_by_id.return_value = mock_user
        
        result = UserService.get_user(1)
        
        self.assertEqual(result, mock_user)
        mock_repo.get_by_id.assert_called_once_with(1)

    @patch('services.user_service.UserRepository')
    def test_get_user_raises_error_when_not_found(self, mock_repo):
        """Test that get_user raises error when user not found"""
        mock_repo.get_by_id.return_value = None
        
        with self.assertRaises(ValueError) as context:
            UserService.get_user(999)
        
        self.assertIn('not found', str(context.exception).lower())

    @patch('services.user_service.UserRepository')
    def test_get_user_by_username_returns_user(self, mock_repo):
        """Test that get_user_by_username returns user when found"""
        mock_user = Mock()
        mock_repo.get_by_username.return_value = mock_user
        
        result = UserService.get_user_by_username('testuser')
        
        self.assertEqual(result, mock_user)
        mock_repo.get_by_username.assert_called_once_with('testuser')

    @patch('services.user_service.UserRepository')
    def test_get_user_by_username_raises_error_when_not_found(self, mock_repo):
        """Test that get_user_by_username raises error when not found"""
        mock_repo.get_by_username.return_value = None
        
        with self.assertRaises(ValueError) as context:
            UserService.get_user_by_username('nonexistent')
        
        self.assertIn('not found', str(context.exception).lower())

    @patch('services.user_service.UserRepository')
    def test_get_all_users_returns_paginated_users(self, mock_repo):
        """Test that get_all_users returns paginated results"""
        mock_users = [Mock(), Mock()]
        mock_repo.get_all.return_value = mock_users
        
        result = UserService.get_all_users(page=2, per_page=25)
        
        self.assertEqual(result, mock_users)
        mock_repo.get_all.assert_called_once_with(page=2, per_page=25)

    @patch('services.user_service.db')
    @patch('services.user_service.UserRepository')
    def test_update_user_score_success(self, mock_repo, mock_db):
        """Test that update_user_score updates score successfully"""
        mock_user = Mock()
        mock_user.total_score = 100
        mock_repo.get_by_id.return_value = mock_user
        
        result = UserService.update_user_score(1, 50)
        
        self.assertEqual(mock_user.total_score, 150)
        mock_db.session.commit.assert_called_once()
        self.assertEqual(result, mock_user)

    @patch('services.user_service.UserRepository')
    def test_update_user_score_user_not_found(self, mock_repo):
        """Test that update_user_score raises error when user not found"""
        mock_repo.get_by_id.return_value = None
        
        with self.assertRaises(ValueError) as context:
            UserService.update_user_score(999, 50)
        
        self.assertIn('not found', str(context.exception).lower())

    @patch('services.user_service.db')
    @patch('services.user_service.UserRepository')
    def test_update_user_score_commit_error(self, mock_repo, mock_db):
        """Test that update_user_score rollsback on commit error"""
        mock_user = Mock()
        mock_user.total_score = 100
        mock_repo.get_by_id.return_value = mock_user
        mock_db.session.commit.side_effect = Exception("DB Error")
        
        with self.assertRaises(ValueError):
            UserService.update_user_score(1, 50)
        
        mock_db.session.rollback.assert_called_once()

    @patch('services.user_service.db')
    @patch('services.user_service.UserRepository')
    def test_increment_games_played_success(self, mock_repo, mock_db):
        """Test that increment_games_played increments counter"""
        mock_user = Mock()
        mock_user.games_played = 5
        mock_repo.get_by_id.return_value = mock_user
        
        result = UserService.increment_games_played(1)
        
        self.assertEqual(mock_user.games_played, 6)
        mock_db.session.commit.assert_called_once()
        self.assertEqual(result, mock_user)

    @patch('services.user_service.UserRepository')
    def test_increment_games_played_user_not_found(self, mock_repo):
        """Test that increment_games_played raises error when user not found"""
        mock_repo.get_by_id.return_value = None
        
        with self.assertRaises(ValueError) as context:
            UserService.increment_games_played(999)
        
        self.assertIn('not found', str(context.exception).lower())

    @patch('services.user_service.db')
    @patch('services.user_service.UserRepository')
    def test_increment_games_played_commit_error(self, mock_repo, mock_db):
        """Test that increment_games_played rollsback on commit error"""
        mock_user = Mock()
        mock_user.games_played = 5
        mock_repo.get_by_id.return_value = mock_user
        mock_db.session.commit.side_effect = Exception("DB Error")
        
        with self.assertRaises(ValueError):
            UserService.increment_games_played(1)
        
        mock_db.session.rollback.assert_called_once()

    @patch('services.user_service.db')
    @patch('services.user_service.UserRepository')
    def test_delete_user_success(self, mock_repo, mock_db):
        """Test that delete_user deletes user successfully"""
        mock_user = Mock()
        mock_repo.get_by_id.return_value = mock_user
        
        UserService.delete_user(1)
        
        mock_repo.delete.assert_called_once_with(mock_user)
        mock_db.session.commit.assert_called_once()

    @patch('services.user_service.UserRepository')
    def test_delete_user_not_found(self, mock_repo):
        """Test that delete_user raises error when user not found"""
        mock_repo.get_by_id.return_value = None
        
        with self.assertRaises(ValueError) as context:
            UserService.delete_user(999)
        
        self.assertIn('not found', str(context.exception).lower())

    @patch('services.user_service.db')
    @patch('services.user_service.UserRepository')
    def test_delete_user_commit_error(self, mock_repo, mock_db):
        """Test that delete_user rollsback on commit error"""
        mock_user = Mock()
        mock_repo.get_by_id.return_value = mock_user
        mock_db.session.commit.side_effect = Exception("DB Error")
        
        with self.assertRaises(ValueError):
            UserService.delete_user(1)
        
        mock_db.session.rollback.assert_called_once()


class CategoryServiceUnitTests(unittest.TestCase):
    """Unit tests for CategoryService - mock repositories and db"""

    @patch('services.category_service.db')
    @patch('services.category_service.CategoryRepository')
    def test_create_category_validates_empty_type(self, mock_repo, mock_db):
        """Test that create_category validates empty type"""
        with self.assertRaises(ValueError) as context:
            CategoryService.create_category('')
        
        self.assertIn('empty', str(context.exception).lower())

    @patch('services.category_service.db')
    @patch('services.category_service.CategoryRepository')
    def test_create_category_checks_uniqueness(self, mock_repo, mock_db):
        """Test that create_category checks if category already exists"""
        mock_repo.exists_by_type.return_value = True
        
        with self.assertRaises(ValueError) as context:
            CategoryService.create_category('Science')
        
        self.assertIn('already exists', str(context.exception).lower())

    @patch('services.category_service.db')
    @patch('services.category_service.CategoryRepository')
    def test_create_category_commits_on_success(self, mock_repo, mock_db):
        """Test that create_category commits transaction on success"""
        mock_repo.exists_by_type.return_value = False
        mock_category = Mock()
        mock_repo.create.return_value = mock_category
        
        result = CategoryService.create_category('Science')
        
        mock_db.session.commit.assert_called_once()
        self.assertEqual(result, mock_category)

    @patch('services.category_service.CategoryRepository')
    def test_get_category_returns_category(self, mock_repo):
        """Test that get_category returns category when found"""
        mock_category = Mock()
        mock_repo.get_by_id.return_value = mock_category
        
        result = CategoryService.get_category(1)
        
        self.assertEqual(result, mock_category)

    @patch('services.category_service.CategoryRepository')
    def test_get_category_raises_error_when_not_found(self, mock_repo):
        """Test that get_category raises error when not found"""
        mock_repo.get_by_id.return_value = None
        
        with self.assertRaises(ValueError) as context:
            CategoryService.get_category(999)
        
        self.assertIn('not found', str(context.exception).lower())

    @patch('services.category_service.CategoryRepository')
    def test_get_all_categories_returns_categories(self, mock_repo):
        """Test that get_all_categories returns all categories"""
        mock_categories = [Mock(), Mock()]
        mock_repo.get_all.return_value = mock_categories
        
        result = CategoryService.get_all_categories()
        
        self.assertEqual(result, mock_categories)
        mock_repo.get_all.assert_called_once()

    @patch('services.category_service.CategoryRepository')
    def test_get_all_categories_with_question_counts(self, mock_repo):
        """Test that get_all_categories_with_question_counts calls optimized repo method"""
        mock_categories = [Mock(), Mock()]
        mock_repo.get_all_with_question_counts.return_value = mock_categories
        
        result = CategoryService.get_all_categories_with_question_counts()
        
        self.assertEqual(result, mock_categories)
        mock_repo.get_all_with_question_counts.assert_called_once()

    @patch('services.category_service.db')
    @patch('services.category_service.CategoryRepository')
    def test_create_category_commit_error(self, mock_repo, mock_db):
        """Test that create_category rollsback on commit error"""
        mock_repo.exists_by_type.return_value = False
        mock_repo.create.return_value = Mock()
        mock_db.session.commit.side_effect = Exception("DB Error")
        
        with self.assertRaises(ValueError):
            CategoryService.create_category('Science')
        
        mock_db.session.rollback.assert_called_once()

    @patch('services.category_service.CategoryRepository')
    def test_get_category_by_type(self, mock_repo):
        """Test that get_category_by_type returns category when found"""
        mock_category = Mock()
        mock_repo.get_by_type.return_value = mock_category
        
        result = CategoryService.get_category_by_type('Science')
        
        self.assertEqual(result, mock_category)
        mock_repo.get_by_type.assert_called_once_with('Science')

    @patch('services.category_service.CategoryRepository')
    def test_get_category_by_type_not_found(self, mock_repo):
        """Test that get_category_by_type raises error when not found"""
        mock_repo.get_by_type.return_value = None
        
        with self.assertRaises(ValueError) as context:
            CategoryService.get_category_by_type('NonExistent')
        
        self.assertIn('not found', str(context.exception).lower())

    @patch('services.category_service.CategoryRepository')
    def test_get_all_categories(self, mock_repo):
        """Test that get_all_categories returns all categories"""
        mock_categories = [Mock(), Mock()]
        mock_repo.get_all.return_value = mock_categories
        
        result = CategoryService.get_all_categories()
        
        self.assertEqual(result, mock_categories)

    @patch('services.category_service.CategoryRepository')
    def test_get_all_categories_with_question_counts(self, mock_repo):
        """Test that get_all_categories_with_question_counts calls optimized method"""
        mock_categories = [Mock(), Mock()]
        mock_repo.get_all_with_question_counts.return_value = mock_categories
        
        result = CategoryService.get_all_categories_with_question_counts()
        
        self.assertEqual(result, mock_categories)
        mock_repo.get_all_with_question_counts.assert_called_once()

    @patch('services.category_service.db')
    @patch('services.category_service.CategoryRepository')
    def test_update_category_success(self, mock_repo, mock_db):
        """Test that update_category updates successfully"""
        mock_category = Mock()
        mock_repo.get_by_id.return_value = mock_category
        
        result = CategoryService.update_category(1, type='History')
        
        mock_repo.update.assert_called_once_with(mock_category, type='History')
        mock_db.session.commit.assert_called_once()

    @patch('services.category_service.CategoryRepository')
    def test_update_category_not_found(self, mock_repo):
        """Test that update_category raises error when not found"""
        mock_repo.get_by_id.return_value = None
        
        with self.assertRaises(ValueError):
            CategoryService.update_category(999, type='History')

    @patch('services.category_service.db')
    @patch('services.category_service.CategoryRepository')
    def test_update_category_commit_error(self, mock_repo, mock_db):
        """Test that update_category rollsback on commit error"""
        mock_category = Mock()
        mock_repo.get_by_id.return_value = mock_category
        mock_db.session.commit.side_effect = Exception("DB Error")
        
        with self.assertRaises(ValueError):
            CategoryService.update_category(1, type='History')
        
        mock_db.session.rollback.assert_called_once()

    @patch('services.category_service.db')
    @patch('services.category_service.CategoryRepository')
    def test_delete_category_success(self, mock_repo, mock_db):
        """Test that delete_category deletes successfully"""
        mock_category = Mock()
        mock_repo.get_by_id.return_value = mock_category
        
        result = CategoryService.delete_category(1)
        
        mock_repo.delete.assert_called_once_with(mock_category)
        mock_db.session.commit.assert_called_once()

    @patch('services.category_service.CategoryRepository')
    def test_delete_category_not_found(self, mock_repo):
        """Test that delete_category raises error when not found"""
        mock_repo.get_by_id.return_value = None
        
        with self.assertRaises(ValueError):
            CategoryService.delete_category(999)

    @patch('services.category_service.db')
    @patch('services.category_service.CategoryRepository')
    def test_delete_category_commit_error(self, mock_repo, mock_db):
        """Test that delete_category rollsback on commit error"""
        mock_category = Mock()
        mock_repo.get_by_id.return_value = mock_category
        mock_db.session.commit.side_effect = Exception("DB Error")
        
        with self.assertRaises(ValueError):
            CategoryService.delete_category(1)
        
        mock_db.session.rollback.assert_called_once()


class QuestionServiceUnitTests(unittest.TestCase):
    """Unit tests for QuestionService - mock repositories and db"""

    @patch('services.question_service.db')
    @patch('services.question_service.QuestionRepository')
    def test_create_question_validates_empty_question(self, mock_repo, mock_db):
        """Test that create_question validates empty question text"""
        with self.assertRaises(ValueError) as context:
            QuestionService.create_question('', 'answer', 1, 1)
        
        self.assertIn('question', str(context.exception).lower())

    @patch('services.question_service.db')
    @patch('services.question_service.QuestionRepository')
    def test_create_question_validates_empty_answer(self, mock_repo, mock_db):
        """Test that create_question validates empty answer"""
        with self.assertRaises(ValueError) as context:
            QuestionService.create_question('Question?', '', 1, 1)
        
        self.assertIn('answer', str(context.exception).lower())

    @patch('services.question_service.db')
    @patch('services.question_service.QuestionRepository')
    def test_create_question_validates_missing_category(self, mock_repo, mock_db):
        """Test that create_question validates category"""
        with self.assertRaises(ValueError) as context:
            QuestionService.create_question('Question?', 'Answer', None, 1)
        
        self.assertIn('category', str(context.exception).lower())

    @patch('services.question_service.db')
    @patch('services.question_service.QuestionRepository')
    def test_create_question_validates_difficulty_range(self, mock_repo, mock_db):
        """Test that create_question validates difficulty range"""
        # Test too low
        with self.assertRaises(ValueError) as context:
            QuestionService.create_question('Q?', 'A', 1, 0)
        
        self.assertIn('1 and 5', str(context.exception))
        
        # Test too high
        with self.assertRaises(ValueError) as context:
            QuestionService.create_question('Q?', 'A', 1, 6)
        
        self.assertIn('1 and 5', str(context.exception))

    @patch('services.question_service.db')
    @patch('services.question_service.QuestionRepository')
    def test_create_question_sets_default_rating(self, mock_repo, mock_db):
        """Test that create_question sets default rating to 0"""
        mock_repo.exists_by_type.return_value = False
        mock_question = Mock()
        mock_repo.create.return_value = mock_question
        
        QuestionService.create_question('Question?', 'Answer', 1, 1)
        
        # Verify create was called with rating=0
        call_kwargs = mock_repo.create.call_args[1]
        self.assertEqual(call_kwargs['rating'], 0)

    @patch('services.question_service.db')
    @patch('services.question_service.QuestionRepository')
    def test_create_question_commits_on_success(self, mock_repo, mock_db):
        """Test that create_question commits on success"""
        mock_question = Mock()
        mock_repo.create.return_value = mock_question
        
        result = QuestionService.create_question('Q?', 'A', 1, 3, 4.5)
        
        mock_db.session.commit.assert_called_once()
        self.assertEqual(result, mock_question)

    @patch('services.question_service.QuestionRepository')
    def test_get_question_returns_question(self, mock_repo):
        """Test that get_question returns question when found"""
        mock_question = Mock()
        mock_repo.get_by_id.return_value = mock_question
        
        result = QuestionService.get_question(1)
        
        self.assertEqual(result, mock_question)

    @patch('services.question_service.QuestionRepository')
    def test_get_question_raises_error_when_not_found(self, mock_repo):
        """Test that get_question raises error when not found"""
        mock_repo.get_by_id.return_value = None
        
        with self.assertRaises(ValueError):
            QuestionService.get_question(999)

    @patch('services.question_service.db')
    @patch('services.question_service.QuestionRepository')
    def test_create_question_commit_error(self, mock_repo, mock_db):
        """Test that create_question rollsback on commit error"""
        mock_repo.create.return_value = Mock()
        mock_db.session.commit.side_effect = Exception("DB Error")
        
        with self.assertRaises(ValueError):
            QuestionService.create_question('Q?', 'A', 1, 3)
        
        mock_db.session.rollback.assert_called_once()

    @patch('services.question_service.QuestionRepository')
    def test_search_questions_by_text(self, mock_repo):
        """Test that search_questions returns search results"""
        mock_questions = [Mock(), Mock()]
        mock_repo.search.return_value = mock_questions
        
        result = QuestionService.search_questions('biology')
        
        self.assertEqual(result, mock_questions)
        mock_repo.search.assert_called_once_with('biology', page=1, per_page=50)

    @patch('services.question_service.QuestionRepository')
    def test_get_all_questions_returns_questions(self, mock_repo):
        """Test that get_all_questions returns all questions"""
        mock_questions = [Mock(), Mock(), Mock()]
        mock_repo.get_all.return_value = mock_questions
        
        result = QuestionService.get_all_questions()
        
        self.assertEqual(result, mock_questions)

    @patch('services.question_service.QuestionRepository')
    def test_get_all_questions_with_categories(self, mock_repo):
        """Test that get_all_questions_with_categories calls optimized repo method"""
        mock_questions = [Mock(), Mock()]
        mock_repo.get_all_with_categories.return_value = mock_questions
        
        result = QuestionService.get_all_questions_with_categories()
        
        self.assertEqual(result, mock_questions)
        mock_repo.get_all_with_categories.assert_called_once()

    @patch('services.question_service.QuestionRepository')
    def test_get_questions_by_category(self, mock_repo):
        """Test that get_questions_by_category returns filtered questions"""
        mock_questions = [Mock(), Mock()]
        mock_repo.get_by_category.return_value = mock_questions
        
        result = QuestionService.get_questions_by_category(1)
        
        self.assertEqual(result, mock_questions)
        mock_repo.get_by_category.assert_called_once_with(1, page=1, per_page=50)

    @patch('services.question_service.QuestionRepository')
    def test_get_questions_by_category_with_details(self, mock_repo):
        """Test that get_questions_by_category_with_details calls optimized method"""
        mock_questions = [Mock(), Mock()]
        mock_repo.get_by_category_with_details.return_value = mock_questions
        
        result = QuestionService.get_questions_by_category_with_details(1)
        
        self.assertEqual(result, mock_questions)
        mock_repo.get_by_category_with_details.assert_called_once_with(1, page=1, per_page=50)

    @patch('services.question_service.QuestionRepository')
    def test_get_random_question_by_category(self, mock_repo):
        """Test that get_random_question_by_category returns random question"""
        mock_question = Mock()
        mock_repo.get_random_by_category.return_value = mock_question
        
        result = QuestionService.get_random_question_by_category(1)
        
        self.assertEqual(result, mock_question)
        mock_repo.get_random_by_category.assert_called_once_with(1)

    @patch('services.question_service.db')
    @patch('services.question_service.QuestionRepository')
    def test_update_question_success(self, mock_repo, mock_db):
        """Test that update_question updates successfully"""
        mock_question = Mock()
        mock_repo.get_by_id.return_value = mock_question
        
        result = QuestionService.update_question(1, difficulty=4)
        
        mock_repo.update.assert_called_once_with(mock_question, difficulty=4)
        mock_db.session.commit.assert_called_once()

    @patch('services.question_service.QuestionRepository')
    def test_update_question_not_found(self, mock_repo):
        """Test that update_question raises error when not found"""
        mock_repo.get_by_id.return_value = None
        
        with self.assertRaises(ValueError):
            QuestionService.update_question(999, difficulty=4)

    @patch('services.question_service.db')
    @patch('services.question_service.QuestionRepository')
    def test_update_question_commit_error(self, mock_repo, mock_db):
        """Test that update_question rollsback on commit error"""
        mock_question = Mock()
        mock_repo.get_by_id.return_value = mock_question
        mock_db.session.commit.side_effect = Exception("DB Error")
        
        with self.assertRaises(ValueError):
            QuestionService.update_question(1, difficulty=4)
        
        mock_db.session.rollback.assert_called_once()

    @patch('services.question_service.db')
    @patch('services.question_service.QuestionRepository')
    def test_delete_question_success(self, mock_repo, mock_db):
        """Test that delete_question deletes successfully"""
        mock_question = Mock()
        mock_repo.get_by_id.return_value = mock_question
        
        QuestionService.delete_question(1)
        
        mock_repo.delete.assert_called_once_with(mock_question)
        mock_db.session.commit.assert_called_once()

    @patch('services.question_service.QuestionRepository')
    def test_delete_question_not_found(self, mock_repo):
        """Test that delete_question raises error when not found"""
        mock_repo.get_by_id.return_value = None
        
        with self.assertRaises(ValueError):
            QuestionService.delete_question(999)

    @patch('services.question_service.db')
    @patch('services.question_service.QuestionRepository')
    def test_delete_question_commit_error(self, mock_repo, mock_db):
        """Test that delete_question rollsback on commit error"""
        mock_question = Mock()
        mock_repo.get_by_id.return_value = mock_question
        mock_db.session.commit.side_effect = Exception("DB Error")
        
        with self.assertRaises(ValueError):
            QuestionService.delete_question(1)
        
        mock_db.session.rollback.assert_called_once()


class GameSessionServiceUnitTests(unittest.TestCase):
    """Unit tests for GameSessionService - mock repositories and db"""

    @patch('services.game_session_service.db')
    @patch('services.game_session_service.GameSessionRepository')
    def test_create_game_session_success(self, mock_repo, mock_db):
        """Test that create_game_session creates successfully"""
        mock_session = Mock()
        mock_repo.create.return_value = mock_session
        
        result = GameSessionService.create_game_session(1, 100, 1)
        
        mock_repo.create.assert_called_once_with(1, 100, 1)
        mock_db.session.commit.assert_called_once()
        self.assertEqual(result, mock_session)

    @patch('services.game_session_service.db')
    @patch('services.game_session_service.GameSessionRepository')
    def test_create_game_session_validates_user_id(self, mock_repo, mock_db):
        """Test that create_game_session validates user_id"""
        with self.assertRaises(ValueError) as context:
            GameSessionService.create_game_session(None, 100)
        
        self.assertIn('required', str(context.exception).lower())

    @patch('services.game_session_service.db')
    @patch('services.game_session_service.GameSessionRepository')
    def test_create_game_session_validates_score(self, mock_repo, mock_db):
        """Test that create_game_session validates score"""
        with self.assertRaises(ValueError) as context:
            GameSessionService.create_game_session(1, -10)
        
        self.assertIn('non-negative', str(context.exception).lower())

    @patch('services.game_session_service.db')
    @patch('services.game_session_service.GameSessionRepository')
    def test_create_game_session_commit_error(self, mock_repo, mock_db):
        """Test that create_game_session rollsback on commit error"""
        mock_repo.create.return_value = Mock()
        mock_db.session.commit.side_effect = Exception("DB Error")
        
        with self.assertRaises(ValueError):
            GameSessionService.create_game_session(1, 100)
        
        mock_db.session.rollback.assert_called_once()

    @patch('services.game_session_service.GameSessionRepository')
    def test_get_game_session_success(self, mock_repo):
        """Test that get_game_session returns session when found"""
        mock_session = Mock()
        mock_repo.get_by_id.return_value = mock_session
        
        result = GameSessionService.get_game_session(1)
        
        self.assertEqual(result, mock_session)

    @patch('services.game_session_service.GameSessionRepository')
    def test_get_game_session_not_found(self, mock_repo):
        """Test that get_game_session raises error when not found"""
        mock_repo.get_by_id.return_value = None
        
        with self.assertRaises(ValueError):
            GameSessionService.get_game_session(999)

    @patch('services.game_session_service.GameSessionRepository')
    def test_get_user_sessions(self, mock_repo):
        """Test that get_user_sessions returns user sessions"""
        mock_sessions = [Mock(), Mock()]
        mock_repo.get_by_user.return_value = mock_sessions
        
        result = GameSessionService.get_user_sessions(1)
        
        self.assertEqual(result, mock_sessions)
        mock_repo.get_by_user.assert_called_once_with(1, page=1, per_page=50)

    @patch('services.game_session_service.GameSessionRepository')
    def test_get_user_sessions_with_details(self, mock_repo):
        """Test that get_user_sessions_with_details calls optimized method"""
        mock_sessions = [Mock(), Mock()]
        mock_repo.get_by_user_with_details.return_value = mock_sessions
        
        result = GameSessionService.get_user_sessions_with_details(1)
        
        self.assertEqual(result, mock_sessions)
        mock_repo.get_by_user_with_details.assert_called_once_with(1, page=1, per_page=50)

    @patch('services.game_session_service.GameSessionRepository')
    def test_get_all_sessions(self, mock_repo):
        """Test that get_all_sessions returns all sessions"""
        mock_sessions = [Mock(), Mock()]
        mock_repo.get_all.return_value = mock_sessions
        
        result = GameSessionService.get_all_sessions()
        
        self.assertEqual(result, mock_sessions)

    @patch('services.game_session_service.GameSessionRepository')
    def test_get_category_sessions(self, mock_repo):
        """Test that get_category_sessions returns category sessions"""
        mock_sessions = [Mock(), Mock()]
        mock_repo.get_by_category.return_value = mock_sessions
        
        result = GameSessionService.get_category_sessions(1)
        
        self.assertEqual(result, mock_sessions)

    @patch('services.game_session_service.GameSessionRepository')
    def test_get_user_stats(self, mock_repo):
        """Test that get_user_stats calls stats method"""
        mock_stats = Mock()
        mock_repo.get_user_stats.return_value = mock_stats
        
        result = GameSessionService.get_user_stats(1)
        
        self.assertEqual(result, mock_stats)
        mock_repo.get_user_stats.assert_called_once_with(1)

    @patch('services.game_session_service.GameSessionRepository')
    def test_get_leaderboard(self, mock_repo):
        """Test that get_leaderboard returns sorted users"""
        mock_leaderboard = [Mock(), Mock()]
        mock_repo.get_leaderboard.return_value = mock_leaderboard
        
        result = GameSessionService.get_leaderboard(10)
        
        self.assertEqual(result, mock_leaderboard)
        mock_repo.get_leaderboard.assert_called_once_with(limit=10)

    @patch('services.game_session_service.db')
    @patch('services.game_session_service.GameSessionRepository')
    def test_update_game_session_success(self, mock_repo, mock_db):
        """Test that update_game_session updates successfully"""
        mock_session = Mock()
        mock_repo.get_by_id.return_value = mock_session
        
        result = GameSessionService.update_game_session(1, score=75)
        
        mock_repo.update.assert_called_once_with(mock_session, score=75)
        mock_db.session.commit.assert_called_once()

    @patch('services.game_session_service.GameSessionRepository')
    def test_update_game_session_not_found(self, mock_repo):
        """Test that update_game_session raises error when not found"""
        mock_repo.get_by_id.return_value = None
        
        with self.assertRaises(ValueError):
            GameSessionService.update_game_session(999, score=75)

    @patch('services.game_session_service.db')
    @patch('services.game_session_service.GameSessionRepository')
    def test_update_game_session_commit_error(self, mock_repo, mock_db):
        """Test that update_game_session rollsback on commit error"""
        mock_session = Mock()
        mock_repo.get_by_id.return_value = mock_session
        mock_db.session.commit.side_effect = Exception("DB Error")
        
        with self.assertRaises(ValueError):
            GameSessionService.update_game_session(1, score=75)
        
        mock_db.session.rollback.assert_called_once()

    @patch('services.game_session_service.db')
    @patch('services.game_session_service.GameSessionRepository')
    def test_delete_game_session_success(self, mock_repo, mock_db):
        """Test that delete_game_session deletes successfully"""
        mock_session = Mock()
        mock_repo.get_by_id.return_value = mock_session
        
        GameSessionService.delete_game_session(1)
        
        mock_repo.delete.assert_called_once_with(mock_session)
        mock_db.session.commit.assert_called_once()

    @patch('services.game_session_service.GameSessionRepository')
    def test_delete_game_session_not_found(self, mock_repo):
        """Test that delete_game_session raises error when not found"""
        mock_repo.get_by_id.return_value = None
        
        with self.assertRaises(ValueError):
            GameSessionService.delete_game_session(999)

    @patch('services.game_session_service.db')
    @patch('services.game_session_service.GameSessionRepository')
    def test_delete_game_session_commit_error(self, mock_repo, mock_db):
        """Test that delete_game_session rollsback on commit error"""
        mock_session = Mock()
        mock_repo.get_by_id.return_value = mock_session
        mock_db.session.commit.side_effect = Exception("DB Error")
        
        with self.assertRaises(ValueError):
            GameSessionService.delete_game_session(1)
        
        mock_db.session.rollback.assert_called_once()


if __name__ == '__main__':
    unittest.main()
