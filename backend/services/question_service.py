"""
Question Service - Business logic for question operations
Handles validation, transaction boundaries, and coordination
"""

from data_access import db, QuestionRepository


class QuestionService:
    """Service layer for question operations"""

    @staticmethod
    def create_question(question_text, answer, category, difficulty, rating=0):
        """
        Create a new question with validation
        
        Args:
            question_text: Question text
            answer: Correct answer
            category: Category ID (must exist)
            difficulty: Difficulty level (1-5)
            rating: Optional rating (default 0)
            
        Returns:
            Created question object
            
        Raises:
            ValueError: If validation fails
        """
        # Validation
        if not question_text or len(question_text.strip()) == 0:
            raise ValueError("Question text cannot be empty")

        normalized_question_text = question_text.strip()
        if len(normalized_question_text) > 500:
            raise ValueError("Question text must be between 1 and 500 characters")
        
        if not answer or len(answer.strip()) == 0:
            raise ValueError("Answer cannot be empty")

        normalized_answer = answer.strip()
        if len(normalized_answer) > 500:
            raise ValueError("Answer must be between 1 and 500 characters")
        
        if not category:
            raise ValueError("Category ID is required")
        
        if not isinstance(difficulty, int) or difficulty < 1 or difficulty > 5:
            raise ValueError("Difficulty must be between 1 and 5")
        
        if rating is None:
            rating = 0

        if not isinstance(rating, (int, float)) or rating < 0.0 or rating > 5.0:
            raise ValueError("Rating must be between 0.0 and 5.0")
        
        # Check for duplicate question (composite key: question + answer + category)
        # Uses normalized (lowercase) comparison
        QuestionService._check_duplicate_question(
            normalized_question_text,
            normalized_answer,
            category
        )
        
        # Create via repository (no commit yet)
        question = QuestionRepository.create(
            question_text=normalized_question_text,
            answer=normalized_answer,
            category=category,
            difficulty=difficulty,
            rating=rating
        )
        
        # Transaction boundary - commit here
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise  # Re-raise DB error so it surfaces as 500, not client error
        
        return question

    @staticmethod
    def get_question(question_id):
        """Get question by ID"""
        question = QuestionRepository.get_by_id(question_id)
        if not question:
            raise ValueError(f"Question {question_id} not found")
        return question

    @staticmethod
    def get_all_questions(page=1, per_page=50):
        """Get all questions with pagination"""
        return QuestionRepository.get_all(page=page, per_page=per_page)

    @staticmethod
    def get_all_questions_with_categories(page=1, per_page=50):
        """
        Get all questions WITH category details eagerly loaded
        Optimized: Avoids N+1 lazy loading of categories
        
        Args:
            page: Pagination page
            per_page: Results per page
            
        Returns:
            Paginated Question results with Category data loaded
        """
        return QuestionRepository.get_all_with_categories(page=page, per_page=per_page)

    @staticmethod
    def search_questions(search_term, page=1, per_page=50):
        """Search questions by term"""
        return QuestionRepository.search(search_term, page=page, per_page=per_page)

    @staticmethod
    def get_questions_by_category(category_id, page=1, per_page=50):
        """Get questions for a specific category"""
        return QuestionRepository.get_by_category(category_id, page=page, per_page=per_page)

    @staticmethod
    def get_questions_by_category_with_details(category_id, page=1, per_page=50):
        """
        Get questions for a category WITH category details
        Optimized: Uses JOIN to ensure category data is loaded
        
        Args:
            category_id: Category ID to filter by
            page: Pagination page
            per_page: Results per page
            
        Returns:
            Paginated Question results with Category data loaded
        """
        return QuestionRepository.get_by_category_with_details(category_id, page=page, per_page=per_page)

    @staticmethod
    def get_random_question_by_category(category_id, exclude_ids=None):
        """Get random question from category"""
        return QuestionRepository.get_random_by_category(category_id, exclude_ids=exclude_ids)

    @staticmethod
    def get_random_question(exclude_ids=None):
        """Get random question from all categories"""
        return QuestionRepository.get_random(exclude_ids=exclude_ids)

    @staticmethod
    def count_total_questions(exclude_ids=None):
        """
        Count total available questions in database
        
        Args:
            exclude_ids: Optional list of question IDs to exclude from count
            
        Returns:
            Integer count of available questions
        """
        return QuestionRepository.count_all(exclude_ids=exclude_ids)

    @staticmethod
    def count_questions_by_category(category_id, exclude_ids=None):
        """
        Count available questions in a specific category
        
        Args:
            category_id: Category ID to count questions for
            exclude_ids: Optional list of question IDs to exclude from count
            
        Returns:
            Integer count of available questions in category
        """
        return QuestionRepository.count_by_category(category_id, exclude_ids=exclude_ids)

    @staticmethod
    def update_question(question_id, **kwargs):
        """Update question fields"""
        question = QuestionRepository.get_by_id(question_id)
        if not question:
            raise ValueError(f"Question {question_id} not found")
        
        try:
            QuestionRepository.update(question, **kwargs)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Failed to update question: {str(e)}")
        
        return question

    @staticmethod
    def delete_question(question_id):
        """Delete a question"""
        question = QuestionRepository.get_by_id(question_id)
        if not question:
            raise ValueError(f"Question {question_id} not found")
        
        try:
            QuestionRepository.delete(question)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Failed to delete question: {str(e)}")
        
        return question

    @staticmethod
    def _check_duplicate_question(question_text, answer, category_id):
        """
        Check if a question with the same normalized text, answer, and category already exists.
        Uses case-insensitive comparison (via SQL LIKE).
        
        Args:
            question_text: Question text (should already be trimmed)
            answer: Answer text (should already be trimmed)
            category_id: Category ID
            
        Raises:
            ValueError: If a duplicate question is found
        """
        # Query via repository for duplicate
        existing = QuestionRepository.get_by_composite_key(question_text, answer, category_id)
        
        if existing:
            raise ValueError(
                f"A question with this text, answer, and category already exists "
                f"(ID: {existing.id}). Composite key constraint: question + answer + category must be unique."
            )
