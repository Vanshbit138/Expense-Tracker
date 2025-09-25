"""
Category service for business logic operations.
"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.category import Category
from src.repositories.category_repository import CategoryRepository
from src.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    """Category service for business logic operations."""

    def __init__(self, db: Session):
        self.db = db
        self.category_repo = CategoryRepository(db)

    def create_category(self, user_id: int, category_data: CategoryCreate) -> Category:
        """Create a new category for a user."""
        # Check if category name is already taken
        if self.category_repo.is_name_taken(category_data.name, user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists",
            )

        # Create category
        category = Category(
            name=category_data.name,
            description=category_data.description,
            color=category_data.color,
            user_id=user_id,
        )

        return self.category_repo.create(category)

    def get_category_by_id(self, category_id: int, user_id: int) -> Optional[Category]:
        """Get category by ID for a specific user."""
        category = self.category_repo.get_by_id(category_id)
        if not category:
            return None

        # Check if user has access to this category
        if not (category.is_system or category.user_id == user_id):
            return None

        return category

    def get_user_categories(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Category]:
        """Get all categories available to a user."""
        return self.category_repo.get_user_categories(user_id, skip, limit)

    def get_system_categories(self) -> List[Category]:
        """Get all system categories."""
        return self.category_repo.get_system_categories()

    def update_category(
        self, category_id: int, user_id: int, category_data: CategoryUpdate
    ) -> Optional[Category]:
        """Update category."""
        category = self.get_category_by_id(category_id, user_id)
        if not category:
            return None

        # System categories cannot be updated
        if category.is_system:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="System categories cannot be updated",
            )

        # Check name uniqueness if name is being updated
        if category_data.name and category_data.name != category.name:
            if self.category_repo.is_name_taken(
                category_data.name, user_id, exclude_category_id=category_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category name already exists",
                )

        # Update category fields
        update_data = category_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        return self.category_repo.update(category)

    def delete_category(self, category_id: int, user_id: int) -> bool:
        """Delete category."""
        category = self.get_category_by_id(category_id, user_id)
        if not category:
            return False

        # System categories cannot be deleted
        if category.is_system:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="System categories cannot be deleted",
            )

        # Check if category has associated expenses
        if category.expenses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category with associated expenses",
            )

        return self.category_repo.delete(category_id)

    def create_system_categories(self) -> List[Category]:
        """Create default system categories."""
        system_categories = [
            {
                "name": "Food & Dining",
                "description": "Restaurants, groceries, and food expenses",
                "color": "#FF6B6B",
            },
            {
                "name": "Transportation",
                "description": "Gas, public transport, car maintenance",
                "color": "#4ECDC4",
            },
            {
                "name": "Shopping",
                "description": "Clothing, electronics, general shopping",
                "color": "#45B7D1",
            },
            {
                "name": "Entertainment",
                "description": "Movies, games, hobbies, subscriptions",
                "color": "#96CEB4",
            },
            {
                "name": "Bills & Utilities",
                "description": "Electricity, water, internet, phone bills",
                "color": "#FFEAA7",
            },
            {
                "name": "Healthcare",
                "description": "Medical expenses, pharmacy, insurance",
                "color": "#DDA0DD",
            },
            {
                "name": "Education",
                "description": "Books, courses, school fees",
                "color": "#98D8C8",
            },
            {
                "name": "Travel",
                "description": "Vacation, hotels, flights",
                "color": "#F7DC6F",
            },
            {
                "name": "Other",
                "description": "Miscellaneous expenses",
                "color": "#BB8FCE",
            },
        ]

        created_categories = []
        for cat_data in system_categories:
            # Check if category already exists (look only for system categories)
            existing = (
                self.db.query(Category)
                .filter(Category.name == cat_data["name"], Category.is_system == True)
                .first()
            )
            if not existing:
                category = Category(
                    name=cat_data["name"],
                    description=cat_data["description"],
                    color=cat_data["color"],
                    is_system=True,
                    user_id=None,
                )
                created_categories.append(self.category_repo.create(category))

        return created_categories
