"""
Unit tests for category service and repository.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.category.category import Category
from src.schemas.category.category import CategoryCreate, CategoryUpdate
from src.schemas.category.category_queries import CategoryFilter
from src.services.category.category_service import CategoryService


class TestCategoryService:
    """Test cases for CategoryService class."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return MagicMock(spec=Session)

    @pytest.fixture
    def category_service(self, mock_db_session):
        """Create a CategoryService instance with mocked dependencies."""
        with patch(
            "src.services.category.category_service.CategoryRepository"
        ) as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            service = CategoryService(mock_db_session)
            service.category_repo = mock_repo
            return service

    def test_create_category_success(self, category_service, sample_category_create):
        """Test successful category creation."""
        # Arrange
        mock_category = Category(
            id=1,
            name=sample_category_create.name,
            description=sample_category_create.description,
            user_id=1,
            is_system=False,
        )
        category_service.category_repo.get_by_name.return_value = None
        category_service.category_repo.create.return_value = mock_category

        # Act
        result = category_service.create_category(sample_category_create, user_id=1)

        # Assert
        assert result == mock_category
        category_service.category_repo.get_by_name.assert_called_once_with(
            sample_category_create.name, 1
        )
        category_service.category_repo.create.assert_called_once()

    def test_create_category_name_already_exists(
        self, category_service, sample_category_create
    ):
        """Test category creation with existing name for user."""
        # Arrange
        existing_category = Category(id=1, name=sample_category_create.name, user_id=1)
        category_service.category_repo.get_by_name.return_value = existing_category

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            category_service.create_category(sample_category_create, user_id=1)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Category name already exists" in exc_info.value.detail

    def test_create_category_database_error(
        self, category_service, sample_category_create
    ):
        """Test category creation with database error."""
        # Arrange
        category_service.category_repo.get_by_name.return_value = None
        category_service.category_repo.create.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            category_service.create_category(sample_category_create, user_id=1)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to create category" in exc_info.value.detail

    def test_get_category_by_id_success(self, category_service):
        """Test successful category retrieval by ID."""
        # Arrange
        mock_category = Category(id=1, name="Test Category", user_id=1)
        category_service.category_repo.get_by_id.return_value = mock_category

        # Act
        result = category_service.get_category_by_id(1, user_id=1)

        # Assert
        assert result == mock_category
        category_service.category_repo.get_by_id.assert_called_once_with(1)

    def test_get_category_by_id_not_found(self, category_service):
        """Test category retrieval by ID when category not found."""
        # Arrange
        category_service.category_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            category_service.get_category_by_id(1, user_id=1)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Category not found" in exc_info.value.detail

    def test_get_category_by_id_wrong_user(self, category_service):
        """Test category retrieval by ID when user doesn't own category."""
        # Arrange
        mock_category = Category(
            id=1, name="Test Category", user_id=2
        )  # Different user
        category_service.category_repo.get_by_id.return_value = mock_category

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            category_service.get_category_by_id(1, user_id=1)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Access denied to category" in exc_info.value.detail

    def test_get_user_categories_success(self, category_service):
        """Test successful user categories retrieval."""
        # Arrange
        mock_categories = [
            Category(id=1, name="Category 1", user_id=1),
            Category(id=2, name="Category 2", user_id=1),
        ]
        category_service.category_repo.get_user_categories.return_value = (
            mock_categories
        )

        # Act
        result = category_service.get_user_categories(user_id=1, skip=0, limit=10)

        # Assert
        assert result == mock_categories
        category_service.category_repo.get_user_categories.assert_called_once_with(
            1, skip=0, limit=10
        )

    def test_update_category_success(self, category_service):
        """Test successful category update."""
        # Arrange
        existing_category = Category(
            id=1, name="Old Category", description="Old description", user_id=1
        )
        category_service.category_repo.get_by_id.return_value = existing_category
        category_service.category_repo.get_by_name.return_value = None
        category_service.category_repo.update.return_value = existing_category

        update_data = CategoryUpdate(name="New Category", description="New description")

        # Act
        result = category_service.update_category(1, update_data, user_id=1)

        # Assert
        assert result == existing_category
        assert existing_category.name == "New Category"
        assert existing_category.description == "New description"
        category_service.category_repo.update.assert_called_once_with(existing_category)

    def test_update_category_not_found(self, category_service):
        """Test category update when category not found."""
        # Arrange
        category_service.category_repo.get_by_id.return_value = None
        update_data = CategoryUpdate(name="New Category")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            category_service.update_category(1, update_data, user_id=1)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Category not found" in exc_info.value.detail

    def test_update_category_wrong_user(self, category_service):
        """Test category update when user doesn't own category."""
        # Arrange
        existing_category = Category(
            id=1, name="Test Category", user_id=2
        )  # Different user
        category_service.category_repo.get_by_id.return_value = existing_category
        update_data = CategoryUpdate(name="New Category")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            category_service.update_category(1, update_data, user_id=1)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Access denied to category" in exc_info.value.detail

    def test_update_category_name_already_exists(self, category_service):
        """Test category update with existing name for user."""
        # Arrange
        existing_category = Category(id=1, name="Old Category", user_id=1)
        other_category = Category(id=2, name="New Category", user_id=1)
        category_service.category_repo.get_by_id.return_value = existing_category
        category_service.category_repo.get_by_name.return_value = other_category

        update_data = CategoryUpdate(name="New Category")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            category_service.update_category(1, update_data, user_id=1)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Category name already exists" in exc_info.value.detail

    def test_update_category_same_name(self, category_service):
        """Test category update with same name (should succeed)."""
        # Arrange
        existing_category = Category(id=1, name="Test Category", user_id=1)
        category_service.category_repo.get_by_id.return_value = existing_category
        category_service.category_repo.update.return_value = existing_category

        update_data = CategoryUpdate(name="Test Category")  # Same name

        # Act
        result = category_service.update_category(1, update_data, user_id=1)

        # Assert
        assert result == existing_category
        # Should not check for uniqueness since name is the same
        category_service.category_repo.get_by_name.assert_not_called()

    def test_delete_category_success(self, category_service):
        """Test successful category deletion."""
        # Arrange
        category_service.category_repo.delete.return_value = True

        # Act
        result = category_service.delete_category(1, user_id=1)

        # Assert
        assert result is True
        category_service.category_repo.delete.assert_called_once_with(1)

    def test_delete_category_not_found(self, category_service):
        """Test category deletion when category not found."""
        # Arrange
        category_service.category_repo.delete.return_value = False

        # Act
        result = category_service.delete_category(1, user_id=1)

        # Assert
        assert result is False

    def test_delete_category_database_error(self, category_service):
        """Test category deletion with database error."""
        # Arrange
        category_service.category_repo.delete.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            category_service.delete_category(1, user_id=1)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to delete category" in exc_info.value.detail

    def test_get_all_categories_success(self, category_service):
        """Test successful all categories retrieval with filtering."""
        # Arrange
        mock_categories = [
            Category(id=1, name="Category 1"),
            Category(id=2, name="Category 2"),
        ]
        category_service.category_repo.get_all.return_value = mock_categories

        category_filter = CategoryFilter(skip=0, limit=10)

        # Act
        result = category_service.get_all_categories(category_filter)

        # Assert
        assert result == mock_categories
        category_service.category_repo.get_all.assert_called_once_with(skip=0, limit=10)

    def test_get_all_categories_database_error(self, category_service):
        """Test all categories retrieval with database error."""
        # Arrange
        category_service.category_repo.get_all.side_effect = Exception("Database error")

        category_filter = CategoryFilter(skip=0, limit=10)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            category_service.get_all_categories(category_filter)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to retrieve categories" in exc_info.value.detail

    def test_validate_name_unique_success(self, category_service):
        """Test name uniqueness validation when name is unique."""
        # Arrange
        category_service.category_repo.get_by_name.return_value = None

        # Act
        category_service._validate_name_unique("Unique Category", user_id=1)

        # Assert - Should not raise an exception
        category_service.category_repo.get_by_name.assert_called_once_with(
            "Unique Category", 1
        )

    def test_validate_name_unique_failure(self, category_service):
        """Test name uniqueness validation when name already exists."""
        # Arrange
        existing_category = Category(id=1, name="Existing Category", user_id=1)
        category_service.category_repo.get_by_name.return_value = existing_category

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            category_service._validate_name_unique("Existing Category", user_id=1)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Category name already exists" in exc_info.value.detail

    def test_validate_name_unique_with_exclude_id(self, category_service):
        """Test name uniqueness validation with exclude_id (for updates)."""
        # Arrange
        existing_category = Category(id=1, name="Existing Category", user_id=1)
        category_service.category_repo.get_by_name.return_value = existing_category

        # Act - Should not raise exception when exclude_id matches
        category_service._validate_name_unique(
            "Existing Category", user_id=1, exclude_id=1
        )

        # Assert
        category_service.category_repo.get_by_name.assert_called_once_with(
            "Existing Category", 1
        )

    def test_validate_name_unique_with_different_exclude_id(self, category_service):
        """Test name uniqueness validation with different exclude_id."""
        # Arrange
        existing_category = Category(id=1, name="Existing Category", user_id=1)
        category_service.category_repo.get_by_name.return_value = existing_category

        # Act & Assert - Should raise exception when exclude_id doesn't match
        with pytest.raises(HTTPException) as exc_info:
            category_service._validate_name_unique(
                "Existing Category", user_id=1, exclude_id=2
            )

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Category name already exists" in exc_info.value.detail

    def test_create_system_categories_success(self, category_service):
        """Test successful system categories creation."""
        # Arrange
        category_service.category_repo.get_by_name.return_value = (
            None  # No existing categories
        )
        mock_created_category = Category(id=1, name="Food & Dining", is_system=True)
        category_service.category_repo.create.return_value = mock_created_category

        # Act
        result = category_service.create_system_categories(user_id=1)

        # Assert
        assert len(result) == 10  # Should create 10 system categories
        assert category_service.category_repo.create.call_count == 10

    def test_create_system_categories_with_existing(self, category_service):
        """Test system categories creation when some already exist."""

        # Arrange
        def side_effect(name, user_id):
            if name == "Food & Dining":
                return Category(id=1, name=name, user_id=user_id)  # Already exists
            return None  # Doesn't exist

        category_service.category_repo.get_by_name.side_effect = side_effect
        mock_created_category = Category(id=2, name="Transportation", is_system=True)
        category_service.category_repo.create.return_value = mock_created_category

        # Act
        result = category_service.create_system_categories(user_id=1)

        # Assert
        assert len(result) == 9  # Should create 9 categories (10 - 1 existing)
        assert category_service.category_repo.create.call_count == 9

    def test_create_system_categories_database_error(self, category_service):
        """Test system categories creation with database error."""
        # Arrange
        category_service.category_repo.get_by_name.return_value = None
        category_service.category_repo.create.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            category_service.create_system_categories(user_id=1)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to create system categories" in exc_info.value.detail


class TestCategoryServiceIntegration:
    """Integration tests for CategoryService."""

    def test_category_lifecycle(self, category_service):
        """Test complete category lifecycle: create, read, update, delete."""
        # Create category
        category_create = CategoryCreate(
            name="Lifecycle Category", description="A category for testing lifecycle"
        )

        created_category = Category(
            id=1,
            name=category_create.name,
            description=category_create.description,
            user_id=1,
        )

        category_service.category_repo.get_by_name.return_value = None
        category_service.category_repo.create.return_value = created_category

        result = category_service.create_category(category_create, user_id=1)
        assert result == created_category

        # Read category
        category_service.category_repo.get_by_id.return_value = created_category
        result = category_service.get_category_by_id(1, user_id=1)
        assert result == created_category

        # Update category
        update_data = CategoryUpdate(description="Updated description")
        category_service.category_repo.update.return_value = created_category
        result = category_service.update_category(1, update_data, user_id=1)
        assert result == created_category

        # Delete category
        category_service.category_repo.delete.return_value = True
        result = category_service.delete_category(1, user_id=1)
        assert result is True

    def test_user_categories_management(self, category_service):
        """Test user categories management workflow."""
        # Create multiple categories for user
        categories_data = [
            CategoryCreate(name="Food", description="Food expenses"),
            CategoryCreate(name="Transport", description="Transportation expenses"),
            CategoryCreate(name="Entertainment", description="Entertainment expenses"),
        ]

        created_categories = []
        for i, cat_data in enumerate(categories_data, 1):
            category = Category(
                id=i, name=cat_data.name, description=cat_data.description, user_id=1
            )
            created_categories.append(category)

        # Mock repository responses
        category_service.category_repo.get_by_name.return_value = None
        category_service.category_repo.create.side_effect = created_categories

        # Create categories
        for cat_data in categories_data:
            result = category_service.create_category(cat_data, user_id=1)
            assert result.name == cat_data.name

        # Get user categories
        category_service.category_repo.get_user_categories.return_value = (
            created_categories
        )
        result = category_service.get_user_categories(user_id=1)
        assert len(result) == 3

        # Update one category
        update_data = CategoryUpdate(description="Updated food description")
        category_service.category_repo.get_by_id.return_value = created_categories[0]
        category_service.category_repo.update.return_value = created_categories[0]

        result = category_service.update_category(1, update_data, user_id=1)
        assert result == created_categories[0]

        # Delete one category
        category_service.category_repo.delete.return_value = True
        result = category_service.delete_category(1, user_id=1)
        assert result is True
