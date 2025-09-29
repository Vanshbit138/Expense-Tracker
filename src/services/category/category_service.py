"""
Category service for business logic operations.
"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.core.logging_config import get_logger
from src.models.category import Category
from src.repositories.category_repository import CategoryRepository
from src.schemas.category import CategoryCreate, CategoryUpdate
from src.schemas.category_queries import CategoryFilter, CategoryQuery

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

            category = self.category_repo.create_category(category_data, user_id)
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
            raise

    def get_category_by_id(self, category_query: CategoryQuery) -> Optional[Category]:
        """Get category by ID."""
        self.logger.debug(
            "Fetching category by ID",
            category_id=category_query.category_id,
            user_id=category_query.user_id,
        )
        category = self.category_repo.get_category_by_id(
            category_query.category_id, category_query.user_id
        )
        if category:
            self.logger.debug(
                "Category found by ID", category_id=category.id, name=category.name
            )
        else:
            self.logger.debug(
                "Category not found by ID", category_id=category_query.category_id
            )
        return category

    def get_categories(self, category_filter: CategoryFilter) -> List[Category]:
        """Get all categories with pagination and filters."""
        self.logger.debug(
            "Fetching categories with filters",
            user_id=category_filter.user_id,
            skip=category_filter.skip,
            limit=category_filter.limit,
        )
        categories = self.category_repo.get_categories(category_filter)
        self.logger.debug("Categories fetched successfully", count=len(categories))
        return categories

    def update_category(
        self, category_id: int, category_data: CategoryUpdate, user_id: int
    ) -> Optional[Category]:
        """Update an existing category."""
        self.logger.info("Updating category", category_id=category_id, user_id=user_id)

        try:
            category = self.category_repo.update_category(
                category_id, category_data, user_id
            )
            if category:
                self.logger.info(
                    "Category updated successfully",
                    category_id=category.id,
                    name=category.name,
                )
            else:
                self.logger.warning(
                    "Category not found for update",
                    category_id=category_id,
                    user_id=user_id,
                )
            return category
        except Exception as e:
            self.logger.error(
                "Failed to update category",
                category_id=category_id,
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            raise

    def delete_category(self, category_query: CategoryQuery) -> bool:
        """Delete a category."""
        self.logger.info(
            "Deleting category",
            category_id=category_query.category_id,
            user_id=category_query.user_id,
        )

        try:
            success = self.category_repo.delete_category(
                category_query.category_id, category_query.user_id
            )
            if success:
                self.logger.info(
                    "Category deleted successfully",
                    category_id=category_query.category_id,
                )
            else:
                self.logger.warning(
                    "Category not found for deletion",
                    category_id=category_query.category_id,
                    user_id=category_query.user_id,
                )
            return success
        except Exception as e:
            self.logger.error(
                "Failed to delete category",
                category_id=category_query.category_id,
                user_id=category_query.user_id,
                error=str(e),
                exc_info=True,
            )
            raise

    def _validate_name_unique(self, name: str, user_id: int) -> None:
        """Validate if category name is unique for user."""
        self.logger.debug(
            "Validating category name uniqueness", name=name, user_id=user_id
        )
        if self.category_repo.get_category_by_name(name, user_id):
            self.logger.warning(
                "Category name already exists", name=name, user_id=user_id
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists",
            )
        self.logger.debug("Category name is unique", name=name, user_id=user_id)
