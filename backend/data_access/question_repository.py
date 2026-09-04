"""Question repository - read/write operations only"""

from models import db, Question, Category


class QuestionRepository:
    """Repository for Question model"""

    @staticmethod
    def create(question_text, answer, category, difficulty, rating=0):
        """Create a new question (no commit)"""
        question = Question(
            question=question_text,
            answer=answer,
            category=category,
            difficulty=difficulty,
            rating=rating
        )
        db.session.add(question)
        return question

    @staticmethod
    def get_by_id(question_id):
        """Get question by ID"""
        return db.session.get(Question, question_id)

    @staticmethod
    def get_all(page=1, per_page=50):
        """Get all questions with pagination"""
        return Question.query.paginate(page=page, per_page=per_page)

    @staticmethod
    def search(search_term, page=1, per_page=50):
        """Search questions by text"""
        return Question.query.filter(
            Question.question.ilike(f'%{search_term}%')
        ).paginate(page=page, per_page=per_page)

    @staticmethod
    def get_by_category(category_id, page=1, per_page=50):
        """Get all questions in a category"""
        return Question.query.filter_by(category=category_id).paginate(
            page=page, per_page=per_page
        )

    @staticmethod
    def update(question, **kwargs):
        """Update question attributes (no commit)"""
        for key, value in kwargs.items():
            if hasattr(question, key):
                setattr(question, key, value)
        return question

    @staticmethod
    def delete(question):
        """Delete question from database (no commit)"""
        db.session.delete(question)

    @staticmethod
    def get_random_by_category(category_id, exclude_ids=None):
        """Get a random question from a category"""
        import random
        query = Question.query.filter_by(category=category_id)
        
        if exclude_ids:
            query = query.filter(~Question.id.in_(exclude_ids))
        
        questions = query.all()
        return random.choice(questions) if questions else None

    @staticmethod
    def delete_by_category(category_id):
        """Delete all questions in a category (no commit)"""
        Question.query.filter_by(category=category_id).delete()

    @staticmethod
    def get_all_with_categories(page=1, per_page=50):
        """
        Get all questions WITH category details in single query
        Uses JOIN to avoid N+1 lazy loading problem
        
        Returns:
            Paginated Question results with Category relationship loaded
        """
        return Question.query.join(Category).paginate(
            page=page, per_page=per_page
        )

    @staticmethod
    def get_by_category_with_details(category_id, page=1, per_page=50):
        """
        Get questions for a category WITH category details
        Ensures category info is eagerly loaded
        
        Args:
            category_id: Category ID to filter by
            page: Pagination page
            per_page: Results per page
            
        Returns:
            Paginated Question results
        """
        return Question.query.join(Category).filter(
            Question.category == category_id
        ).paginate(page=page, per_page=per_page)
