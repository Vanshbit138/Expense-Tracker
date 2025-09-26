"""
Category service for business logic operations.
"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.category import Category
from src.models.expense import Expense
from src.repositories.category_repository import CategoryRepository
from src.schemas.category import CategoryCreate, CategoryUpdate
from src.schemas.category_queries import (
    CategoryFilter,
    CategoryQuery,
    CategoryValidation,
)


class CategoryService:
    """Category service for business logic operations following SOLID principles."""

    def __init__(self, db: Session):
        self.db = db
        self.category_repo = CategoryRepository(db)

    def create_category(self, user_id: int, category_data: CategoryCreate) -> Category:
        """Create a new category for a user."""
        # Validate category name uniqueness
        validation_data = CategoryValidation(name=category_data.name, user_id=user_id)
        self._validate_category_name_unique(validation_data)

        # Create category
        category = Category(
            name=category_data.name,
            description=category_data.description,
            color=category_data.color,
            user_id=user_id,
        )

        return self.category_repo.create(category)

    def get_category_by_id(self, data: CategoryQuery) -> Optional[Category]:
        """Get category by ID for a specific user."""
        category = self.category_repo.get_by_id(data.category_id)
        if not category:
            return None

        # Check if user has access to this category
        if not (category.is_system or category.user_id == data.user_id):
            return None

        return category

    def get_user_categories(self, data: CategoryFilter) -> List[Category]:
        """Get all categories available to a user."""
        return self.category_repo.get_user_categories(
            data.user_id, data.skip, data.limit
        )

    def get_system_categories(self) -> List[Category]:
        """Get all system categories."""
        return self.category_repo.get_system_categories()

    def update_category(
        self, category_id: int, user_id: int, category_data: CategoryUpdate
    ) -> Optional[Category]:
        """Update category."""
        category = self.category_repo.get_by_id(category_id)
        if not category:
            return None

        # Check if user has access to this category
        if not (category.user_id == user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this category",
            )

        # Validate name uniqueness if name is being updated
        if category_data.name and category_data.name != category.name:
            validation_data = CategoryValidation(
                name=category_data.name,
                user_id=user_id,
                exclude_category_id=category_id,
            )
            self._validate_category_name_unique(validation_data)

        # Update category fields
        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        return self.category_repo.update(category)

    def delete_category(self, data: CategoryQuery) -> bool:
        """Delete category."""
        category = self.category_repo.get_by_id(data.category_id)
        if not category:
            return False

        # Check if user has access to this category
        if not (category.user_id == data.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this category",
            )

        # Check if category has associated expenses
        if self._has_associated_expenses(data.category_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category with associated expenses",
            )

        return self.category_repo.delete(data.category_id)

    def create_system_categories(self, user_id: int) -> List[Category]:
        """Create system categories (idempotent operation)."""
        # Check if user is superuser
        from src.repositories.user_repository import UserRepository

        user_repo = UserRepository(self.db)
        user = user_repo.get_by_id(user_id)

        if not user or not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only superusers can create system categories",
            )

        system_categories_data = [
            {
                "name": "Food & Dining",
                "description": "Restaurants, groceries, and dining",
            },
            {"name": "Transportation", "description": "Car, gas, public transport"},
            {"name": "Entertainment", "description": "Movies, games, hobbies"},
            {"name": "Utilities", "description": "Electricity, water, internet"},
            {"name": "Healthcare", "description": "Medical expenses and insurance"},
            {
                "name": "Shopping",
                "description": "Clothes, electronics, general shopping",
            },
            {"name": "Travel", "description": "Vacations and business travel"},
            {"name": "Education", "description": "Books, courses, training"},
        ]

        created_categories = []
        for category_data in system_categories_data:
            # Check if system category already exists
            existing = self.category_repo.get_system_category_by_name(
                category_data["name"]
            )
            if not existing:
                category = Category(
                    name=category_data["name"],
                    description=category_data["description"],
                    is_system=True,
                    user_id=None,
                )
                created_categories.append(self.category_repo.create(category))
            else:
                created_categories.append(existing)

        return created_categories

    def _validate_category_name_unique(self, data: CategoryValidation) -> None:
        """Validate category name uniqueness."""
        if self.category_repo.is_name_taken(
            data.name, data.user_id, exclude_category_id=data.exclude_category_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists",
            )

    def _has_associated_expenses(self, category_id: int) -> bool:
        """Check if category has associated expenses."""
        count = (
            self.db.query(func.count(Expense.id))
            .filter(Expense.category_id == category_id)
            .scalar()
        )
        return count > 0
