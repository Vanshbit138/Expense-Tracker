"""
Category service for business logic operations.
"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.core.logging_config import get_logger
from src.models.category.category import Category
from src.repositories.category.category_repository import CategoryRepository
from src.schemas.category.category import CategoryCreate, CategoryUpdate
from src.schemas.category.category_queries import CategoryFilter

# Initialize logger
logger = get_logger(__name__)


class CategoryService:
    """Category service for business logic operations following SOLID principles."""

    def __init__(self, db: Session):
        self.db = db
        self.category_repo = CategoryRepository(db)
        self.logger = get_logger(self.__class__.__name__)

    def create_category(self, category_data: CategoryCreate, user_id: int) -> Category:
        """Create a new category."""
        self.logger.info(
            "Creating new category", name=category_data.name, user_id=user_id
        )

        try:
            # Validate name uniqueness for user
            self._validate_name_unique(category_data.name, user_id)

            category = self.category_repo.create(
                Category(
                    name=category_data.name,
                    description=category_data.description,
                    user_id=user_id,
                )
            )
            self.logger.info(
                "Category created successfully",
                category_id=category.id,
                name=category.name,
            )
            return category
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to create category",
                name=category_data.name,
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create category",
            )

    def get_category_by_id(self, category_id: int, user_id: int) -> Category:
        """Get category by ID."""
        self.logger.debug(
            "Getting category by ID", category_id=category_id, user_id=user_id
        )
        category = self.category_repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
        if category.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to category",
            )
        return category

    def get_user_categories(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Category]:
        """Get categories for a user."""
        self.logger.debug(
            "Getting user categories", user_id=user_id, skip=skip, limit=limit
        )
        return self.category_repo.get_user_categories(user_id, skip=skip, limit=limit)

    def update_category(
        self, category_id: int, category_data: CategoryUpdate, user_id: int
    ) -> Category:
        """Update category information."""
        self.logger.info("Updating category", category_id=category_id, user_id=user_id)

        try:

            # Update fields if provided
            if category_data.name is not None:
                if category_data.name != category.name:
                    self._validate_name_unique(
                        category_data.name, user_id, exclude_id=category_id
                    )
                category.name = category_data.name

            if category_data.description is not None:
                category.description = category_data.description

            # Save changes
            updated_category = self.category_repo.update(category)
            self.logger.info(
                "Category updated successfully", category_id=updated_category.id
            )
            return updated_category

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to update category",
                category_id=category_id,
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update category",
            )

    def delete_category(self, category_id: int, user_id: int) -> bool:
        """Delete category."""
        self.logger.info("Deleting category", category_id=category_id, user_id=user_id)

        try:
            success = self.category_repo.delete(category_id)

            if success:
                self.logger.info(
                    "Category deleted successfully", category_id=category_id
                )
            else:
                self.logger.warning(
                    "Failed to delete category", category_id=category_id
                )

            return success

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to delete category",
                category_id=category_id,
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete category",
            )

    def get_all_categories(self, query: CategoryFilter) -> List[Category]:
        """Get all categories with filtering and pagination."""
        self.logger.debug("Getting all categories", filters=query.model_dump())

        try:
            categories = self.category_repo.get_all(skip=query.skip, limit=query.limit)

            self.logger.debug(
                "Categories retrieved successfully", count=len(categories)
            )
            return categories

        except Exception as e:
            self.logger.error("Failed to get categories", error=str(e), exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve categories",
            )

    def _validate_name_unique(
        self, name: str, user_id: int, exclude_id: Optional[int] = None
    ) -> None:
        """Validate category name uniqueness for user."""
        existing_category = self.category_repo.get_by_name(name, user_id)
        if existing_category and (
            exclude_id is None or existing_category.id != exclude_id
        ):
            self.logger.warning(
                "Category name validation failed - name already exists",
                name=name,
                user_id=user_id,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists",
            )

    def create_system_categories(self, user_id: int) -> List[Category]:
        """Create system categories for a user."""
        self.logger.info("Creating system categories", user_id=user_id)

        try:
            # Define system categories
            system_categories = [
                {
                    "name": "Food & Dining",
                    "description": "Restaurants, groceries, and food expenses",
                },
                {
                    "name": "Transportation",
                    "description": "Gas, public transport, and vehicle expenses",
                },
                {
                    "name": "Entertainment",
                    "description": "Movies, games, and entertainment expenses",
                },
                {
                    "name": "Utilities",
                    "description": "Electricity, water, internet, and utility bills",
                },
                {
                    "name": "Healthcare",
                    "description": "Medical expenses and healthcare costs",
                },
                {
                    "name": "Shopping",
                    "description": "Clothing, electronics, and general shopping",
                },
                {
                    "name": "Travel",
                    "description": "Hotels, flights, and travel expenses",
                },
                {
                    "name": "Education",
                    "description": "Books, courses, and educational expenses",
                },
                {
                    "name": "Insurance",
                    "description": "Health, auto, and other insurance payments",
                },
                {
                    "name": "Miscellaneous",
                    "description": "Other expenses that do not fit other categories",
                },
            ]

            created_categories = []
            for cat_data in system_categories:
                # Check if category already exists for this user
                existing = self.category_repo.get_by_name(cat_data["name"], user_id)
                if not existing:
                    category = Category(
                        name=cat_data["name"],
                        description=cat_data["description"],
                        user_id=user_id,
                        is_system=True,
                    )
                    created_category = self.category_repo.create(category)
                    created_categories.append(created_category)
                    self.logger.debug(
                        "System category created",
                        category_id=created_category.id,
                        name=created_category.name,
                    )
                else:
                    self.logger.debug(
                        "System category already exists",
                        name=cat_data["name"],
                        user_id=user_id,
                    )

            self.logger.info(
                "System categories creation completed",
                user_id=user_id,
                created_count=len(created_categories),
            )
            return created_categories

        except Exception as e:
            self.logger.error(
                "Failed to create system categories",
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create system categories",
            )


def _validate_category_access(self, category_id: int, user_id: int) -> Category:
    """Validate user access to category."""
    category = self.category_repo.get_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    if category.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to category"
        )
    return category
