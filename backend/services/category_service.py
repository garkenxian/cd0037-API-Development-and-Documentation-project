"""
Category Service - Business logic for category operations
Handles validation, transaction boundaries, and coordination
"""

from data_access import db, CategoryRepository


class CategoryService:
    """Service layer for category operations"""

    @staticmethod
    def create_category(category_type):
        """
        Create a new category with validation
        
        Args:
            category_type: Category name/type string
            
        Returns:
            Created category object
            
        Raises:
            ValueError: If validation fails
        """
        # Validation
        if not category_type or len(category_type.strip()) == 0:
            raise ValueError("Category type cannot be empty")
        
        # Check uniqueness
        if CategoryRepository.exists_by_type(category_type):
            raise ValueError(f"Category '{category_type}' already exists")
        
        # Create via repository (no commit yet)
        category = CategoryRepository.create(category_type)
        
        # Transaction boundary - commit here
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise  # Re-raise DB error so it surfaces as 500, not client error
        
        return category

    @staticmethod
    def get_category(category_id):
        """Get category by ID"""
        category = CategoryRepository.get_by_id(category_id)
        if not category:
            raise ValueError(f"Category {category_id} not found")
        return category

    @staticmethod
    def get_category_by_type(category_type):
        """Get category by type"""
        category = CategoryRepository.get_by_type(category_type)
        if not category:
            raise ValueError(f"Category '{category_type}' not found")
        return category

    @staticmethod
    def get_all_categories(page=1, per_page=50):
        """Get all categories with pagination"""
        return CategoryRepository.get_all(page=page, per_page=per_page)

    @staticmethod
    def get_all_categories_list():
        """Get all categories as a simple list (no pagination)"""
        from models import Category
        return Category.query.all()

    @staticmethod
    def get_all_categories_with_question_counts(page=1, per_page=50):
        """
        Get all categories WITH question counts
        Optimized: Single query instead of 1 + N queries
        
        Args:
            page: Pagination page
            per_page: Results per page
            
        Returns:
            Paginated results with (Category, question_count) tuples
        """
        return CategoryRepository.get_all_with_question_counts(page=page, per_page=per_page)

    @staticmethod
    def update_category(category_id, **kwargs):
        """Update category fields"""
        category = CategoryRepository.get_by_id(category_id)
        if not category:
            raise ValueError(f"Category {category_id} not found")
        
        try:
            CategoryRepository.update(category, **kwargs)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Failed to update category: {str(e)}")
        
        return category

    @staticmethod
    def delete_category(category_id):
        """Delete a category"""
        category = CategoryRepository.get_by_id(category_id)
        if not category:
            raise ValueError(f"Category {category_id} not found")
        
        try:
            CategoryRepository.delete(category)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Failed to delete category: {str(e)}")
        
        return category
