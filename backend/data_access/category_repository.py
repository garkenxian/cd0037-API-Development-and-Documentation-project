"""Category repository - read/write operations only"""

from models import db, Category
from sqlalchemy import func


class CategoryRepository:
    """Repository for Category model"""

    @staticmethod
    def create(category_type):
        """Create a new category (no commit)"""
        category = Category(type=category_type)
        db.session.add(category)
        return category

    @staticmethod
    def get_by_id(category_id):
        """Get category by ID"""
        return db.session.get(Category, category_id)

    @staticmethod
    def get_by_type(category_type):
        """Get category by type name"""
        return Category.query.filter_by(type=category_type).first()

    @staticmethod
    def get_all(page=1, per_page=50):
        """Get all categories with pagination"""
        return Category.query.paginate(page=page, per_page=per_page)

    @staticmethod
    def update(category, **kwargs):
        """Update category attributes (no commit)"""
        for key, value in kwargs.items():
            if hasattr(category, key):
                setattr(category, key, value)
        return category

    @staticmethod
    def delete(category):
        """Delete category from database (no commit)"""
        db.session.delete(category)

    @staticmethod
    def exists_by_type(category_type):
        """Check if category type already exists"""
        return Category.query.filter_by(type=category_type).first() is not None

    @staticmethod
    def get_question_count(category_id):
        """Get count of questions in a category"""
        from models import Question
        return Question.query.filter_by(category=category_id).count()

    @staticmethod
    def get_all_with_question_counts(page=1, per_page=50):
        """
        Get all categories WITH question counts in single query
        Uses OUTERJOIN to avoid N+1 query problem
        
        Returns:
            Paginated results with category and question_count label
        """
        from models import Question
        
        # Query returns tuples of (Category, count)
        results = db.session.query(
            Category,
            func.count(Question.id).label('question_count')
        ).outerjoin(Question).group_by(Category.id).paginate(
            page=page, per_page=per_page
        )
        
        return results
