"""
Tests for CategoryService.
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException, status

from src.models.category.category import Category
from src.schemas.category.category import CategoryCreate, CategoryUpdate
from src.services.category.category_service import CategoryService


class TestCategoryService:
    """Test cases for CategoryService."""

    def test_service_initialization(self, mock_db_session):
        """Test service initialization with database session."""
        category_service = CategoryService(mock_db_session)

        assert category_service.db == mock_db_session
        assert category_service.category_repo is not None

    def test_create_category_success(self, mock_db_session):
        """Test successful category creation."""
        # Create test data
        category_data = CategoryCreate(
            name="Test Category", description="A test category"
        )

        # Mock the repository
        mock_repo = Mock()
        mock_category = Mock(spec=Category)
        mock_category.id = 1
        mock_category.name = "Test Category"
        mock_category.description = "A test category"
        mock_category.user_id = 1
        mock_category.is_system = False

        mock_repo.get_by_name.return_value = None
        mock_repo.create.return_value = mock_category

        with patch(
            "src.services.category.category_service.CategoryRepository",
            return_value=mock_repo,
        ):
            category_service = CategoryService(mock_db_session)
            result = category_service.create_category(category_data, user_id=1)

        assert result == mock_category
        mock_repo.create.assert_called_once()

    def test_create_category_name_already_exists(self, mock_db_session):
        """Test category creation when name already exists."""
        # Create test data
        category_data = CategoryCreate(
            name="Existing Category", description="A test category"
        )

        # Mock existing category
        mock_repo = Mock()
        existing_category = Mock(spec=Category)
        mock_repo.get_by_name.return_value = existing_category

        with patch(
            "src.services.category.category_service.CategoryRepository",
            return_value=mock_repo,
        ):
            category_service = CategoryService(mock_db_session)

            with pytest.raises(HTTPException) as exc_info:
                category_service.create_category(category_data, user_id=1)

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Category name already exists" in str(exc_info.value.detail)

    def test_get_category_by_id_success(self, mock_db_session):
        """Test successful category retrieval by ID."""
        # Mock category
        mock_repo = Mock()
        mock_category = Mock(spec=Category)
        mock_category.id = 1
        mock_category.user_id = 1
        mock_repo.get_by_id.return_value = mock_category

        with patch(
            "src.services.category.category_service.CategoryRepository",
            return_value=mock_repo,
        ):
            category_service = CategoryService(mock_db_session)
            result = category_service.get_category_by_id(1, user_id=1)

        assert result == mock_category
        mock_repo.get_by_id.assert_called_once_with(1)

    def test_get_category_by_id_not_found(self, mock_db_session):
        """Test category retrieval when category not found."""
        # Mock repository to return None
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = None

        with patch(
            "src.services.category.category_service.CategoryRepository",
            return_value=mock_repo,
        ):
            category_service = CategoryService(mock_db_session)

            with pytest.raises(HTTPException) as exc_info:
                category_service.get_category_by_id(999, user_id=1)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "Category not found" in str(exc_info.value.detail)

    def test_get_category_by_id_wrong_user(self, mock_db_session):
        """Test category retrieval when user doesn't own category."""
        # Mock category owned by different user
        mock_repo = Mock()
        mock_category = Mock(spec=Category)
        mock_category.id = 1
        mock_category.user_id = 2  # Different user
        mock_repo.get_by_id.return_value = mock_category

        with patch(
            "src.services.category.category_service.CategoryRepository",
            return_value=mock_repo,
        ):
            category_service = CategoryService(mock_db_session)

            with pytest.raises(HTTPException) as exc_info:
                category_service.get_category_by_id(1, user_id=1)

            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
            assert "Access denied to category" in str(exc_info.value.detail)

    def test_get_user_categories(self, mock_db_session):
        """Test getting user categories."""
        # Mock categories
        mock_repo = Mock()
        mock_categories = [Mock(spec=Category), Mock(spec=Category)]
        mock_repo.get_user_categories.return_value = mock_categories

        with patch(
            "src.services.category.category_service.CategoryRepository",
            return_value=mock_repo,
        ):
            category_service = CategoryService(mock_db_session)
            result = category_service.get_user_categories(user_id=1, skip=0, limit=10)

        assert result == mock_categories
        mock_repo.get_user_categories.assert_called_once_with(1, skip=0, limit=10)

    def test_update_category_success(self, mock_db_session):
        """Test successful category update."""
        # Create test data
        update_data = CategoryUpdate(
            name="Updated Category", description="Updated description"
        )

        # Mock existing category
        mock_repo = Mock()
        existing_category = Mock(spec=Category)
        existing_category.id = 1
        existing_category.name = "Old Category"
        existing_category.user_id = 1
        existing_category.description = "Old description"

        updated_category = Mock(spec=Category)
        updated_category.id = 1
        updated_category.name = "Updated Category"
        updated_category.description = "Updated description"
        updated_category.user_id = 1

        mock_repo.get_by_id.return_value = existing_category
        mock_repo.get_by_name.return_value = None  # Name is unique
        mock_repo.update.return_value = updated_category

        with patch(
            "src.services.category.category_service.CategoryRepository",
            return_value=mock_repo,
        ):
            category_service = CategoryService(mock_db_session)
            result = category_service.update_category(1, update_data, user_id=1)

        assert result == updated_category
        mock_repo.update.assert_called_once()

    def test_delete_category_success(self, mock_db_session):
        """Test successful category deletion."""
        # Mock repository
        mock_repo = Mock()
        mock_repo.delete.return_value = True

        with patch(
            "src.services.category.category_service.CategoryRepository",
            return_value=mock_repo,
        ):
            category_service = CategoryService(mock_db_session)
            result = category_service.delete_category(1, user_id=1)

        assert result is True
        mock_repo.delete.assert_called_once_with(1)

    def test_delete_category_not_found(self, mock_db_session):
        """Test category deletion when category not found."""
        # Mock repository
        mock_repo = Mock()
        mock_repo.delete.return_value = False

        with patch(
            "src.services.category.category_service.CategoryRepository",
            return_value=mock_repo,
        ):
            category_service = CategoryService(mock_db_session)
            result = category_service.delete_category(999, user_id=1)

        assert result is False

    def test_create_system_categories(self, mock_db_session):
        """Test creating system categories."""
        # Mock repository
        mock_repo = Mock()
        # mock_categories = [Mock(spec=Category), Mock(spec=Category)]
        mock_repo.get_by_name.return_value = None  # No existing categories
        mock_repo.create.return_value = Mock(spec=Category)

        with patch(
            "src.services.category.category_service.CategoryRepository",
            return_value=mock_repo,
        ):
            category_service = CategoryService(mock_db_session)
            result = category_service.create_system_categories(user_id=1)

        assert len(result) == 10
        assert mock_repo.create.call_count == 10
