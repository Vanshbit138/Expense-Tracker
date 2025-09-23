"""
Category repository for database operations.
"""

from typing import List, Optional

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from src.models.category import Category


class CategoryRepository:
    """Category repository for database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, category: Category) -> Category:
        """Create a new category."""
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def get_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID."""
        return self.db.query(Category).filter(Category.id == category_id).first()

    def get_by_name(
        self, name: str, user_id: Optional[int] = None
    ) -> Optional[Category]:
        """Get category by name for a specific user."""
        query = self.db.query(Category).filter(Category.name == name)
        if user_id is not None:
            query = query.filter(or_(Category.user_id == user_id, Category.is_system))
        return query.first()

    def get_user_categories(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Category]:
        """Get all categories available to a user (user's + system categories)."""
        return (
            self.db.query(Category)
            .filter(or_(Category.user_id == user_id, Category.is_system))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_system_categories(self) -> List[Category]:
        """Get all system categories."""
        return self.db.query(Category).filter(Category.is_system).all()

    def update(self, category: Category) -> Category:
        """Update category."""
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category_id: int) -> bool:
        """Delete category by ID (only user categories)."""
        category = self.get_by_id(category_id)
        if category and not category.is_system:
            self.db.delete(category)
            self.db.commit()
            return True
        return False

    def is_name_taken(
        self, name: str, user_id: int, exclude_category_id: Optional[int] = None
    ) -> bool:
        """Check if category name is already taken for a user."""
        query = self.db.query(Category).filter(
            and_(
                Category.name == name,
                or_(Category.user_id == user_id, Category.is_system),
            )
        )
        if exclude_category_id:
            query = query.filter(Category.id != exclude_category_id)
        return query.first() is not None
