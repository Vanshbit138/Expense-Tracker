"""
Tests for category API endpoints.
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException, status

from src.models.category.category import Category
from src.models.user.user import User
from src.schemas.category.category import CategoryCreate, CategoryUpdate


class TestCategoryAPI:
    """Test cases for category API endpoints."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing."""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.username = "testuser"
        user.full_name = "Test User"
        user.is_active = True
        user.is_superuser = False
        return user

    @pytest.fixture
    def mock_superuser(self):
        """Create a mock superuser for testing."""
        user = Mock(spec=User)
        user.id = 1
        user.email = "admin@example.com"
        user.username = "admin"
        user.full_name = "Admin User"
        user.is_active = True
        user.is_superuser = True
        return user

    @pytest.fixture
    def mock_category(self):
        """Create a mock category for testing."""
        category = Mock(spec=Category)
        category.id = 1
        category.name = "Test Category"
        category.description = "Test description"
        category.user_id = 1
        category.is_system = False
        return category

    @pytest.fixture
    def sample_category_data(self):
        """Create sample category data for testing."""
        return {"name": "Test Category", "description": "Test description"}

    @pytest.fixture
    def sample_category_update_data(self):
        """Create sample category update data for testing."""
        return {"name": "Updated Category", "description": "Updated description"}

    def test_create_category_success(
        self, mock_user, mock_category, sample_category_data
    ):
        """Test successful category creation."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.create_category.return_value = mock_category

            with patch(
                "src.api.category.categories.get_current_active_user_with_bypass",
                return_value=mock_user,
            ):
                with patch("src.api.category.categories.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.category.categories import create_category

                    result = create_category(
                        category_data=CategoryCreate(**sample_category_data),
                        current_user=mock_user,
                        db=mock_db,
                    )

                    assert result == mock_category
                    mock_service_class.assert_called_once_with(mock_db)
                    mock_service.create_category.assert_called_once_with(
                        CategoryCreate(**sample_category_data), mock_user.id
                    )

    def test_get_categories_success(self, mock_user, mock_category):
        """Test successful categories retrieval."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_user_categories.return_value = [mock_category]

            with patch(
                "src.api.category.categories.get_current_active_user_with_bypass",
                return_value=mock_user,
            ):
                with patch("src.api.category.categories.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.category.categories import get_categories

                    result = get_categories(
                        skip=0, limit=100, current_user=mock_user, db=mock_db
                    )

                    assert result == [mock_category]
                    mock_service_class.assert_called_once_with(mock_db)
                    mock_service.get_user_categories.assert_called_once_with(
                        mock_user.id, skip=0, limit=100
                    )

    def test_get_categories_with_pagination(self, mock_user, mock_category):
        """Test categories retrieval with pagination."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_user_categories.return_value = [mock_category]

            with patch(
                "src.api.category.categories.get_current_active_user_with_bypass",
                return_value=mock_user,
            ):
                with patch("src.api.category.categories.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.category.categories import get_categories

                    result = get_categories(
                        skip=10, limit=50, current_user=mock_user, db=mock_db
                    )

                    assert result == [mock_category]
                    mock_service.get_user_categories.assert_called_once_with(
                        mock_user.id, skip=10, limit=50
                    )

    def test_get_category_success(self, mock_user, mock_category):
        """Test successful single category retrieval."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_category_by_id.return_value = mock_category

            with patch(
                "src.api.category.categories.get_current_active_user_with_bypass",
                return_value=mock_user,
            ):
                with patch("src.api.category.categories.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.category.categories import get_category

                    result = get_category(
                        category_id=1, current_user=mock_user, db=mock_db
                    )

                    assert result == mock_category
                    mock_service.get_category_by_id.assert_called_once_with(
                        1, mock_user.id
                    )

    def test_get_category_not_found(self, mock_user):
        """Test single category retrieval when not found."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_category_by_id.return_value = None

            with patch(
                "src.api.category.categories.get_current_active_user_with_bypass",
                return_value=mock_user,
            ):
                with patch("src.api.category.categories.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.category.categories import get_category

                    with pytest.raises(HTTPException) as exc_info:
                        get_category(
                            category_id=999, current_user=mock_user, db=mock_db
                        )

                    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
                    assert exc_info.value.detail == "Category not found"

    def test_update_category_success(
        self, mock_user, mock_category, sample_category_update_data
    ):
        """Test successful category update."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.update_category.return_value = mock_category

            with patch(
                "src.api.category.categories.get_current_active_user_with_bypass",
                return_value=mock_user,
            ):
                with patch("src.api.category.categories.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.category.categories import update_category

                    result = update_category(
                        category_id=1,
                        category_data=CategoryUpdate(**sample_category_update_data),
                        current_user=mock_user,
                        db=mock_db,
                    )

                    assert result == mock_category
                    mock_service.update_category.assert_called_once_with(
                        1, CategoryUpdate(**sample_category_update_data), mock_user.id
                    )

    def test_update_category_not_found(self, mock_user, sample_category_update_data):
        """Test category update when not found."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.update_category.return_value = None

            with patch(
                "src.api.category.categories.get_current_active_user_with_bypass",
                return_value=mock_user,
            ):
                with patch("src.api.category.categories.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.category.categories import update_category

                    with pytest.raises(HTTPException) as exc_info:
                        update_category(
                            category_id=999,
                            category_data=CategoryUpdate(**sample_category_update_data),
                            current_user=mock_user,
                            db=mock_db,
                        )

                    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
                    assert exc_info.value.detail == "Category not found"

    def test_delete_category_success(self, mock_user):
        """Test successful category deletion."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.delete_category.return_value = True

            with patch(
                "src.api.category.categories.get_current_active_user_with_bypass",
                return_value=mock_user,
            ):
                with patch("src.api.category.categories.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.category.categories import delete_category

                    result = delete_category(
                        category_id=1, current_user=mock_user, db=mock_db
                    )

                    assert result == {"message": "Category deleted successfully"}
                    mock_service.delete_category.assert_called_once_with(
                        1, mock_user.id
                    )

    def test_delete_category_not_found(self, mock_user):
        """Test category deletion when not found."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.delete_category.return_value = False

            with patch(
                "src.api.category.categories.get_current_active_user_with_bypass",
                return_value=mock_user,
            ):
                with patch("src.api.category.categories.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.category.categories import delete_category

                    with pytest.raises(HTTPException) as exc_info:
                        delete_category(
                            category_id=999, current_user=mock_user, db=mock_db
                        )

                    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
                    assert exc_info.value.detail == "Category not found"

    def test_init_system_categories_success(self, mock_superuser, mock_category):
        """Test successful system categories initialization."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.create_system_categories.return_value = [mock_category]

            with patch(
                "src.api.category.categories.get_current_active_user_with_bypass",
                return_value=mock_superuser,
            ):
                with patch("src.api.category.categories.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.category.categories import init_system_categories

                    result = init_system_categories(
                        current_user=mock_superuser, db=mock_db
                    )

                    expected_result = {
                        "message": f"Created {len([mock_category])} system categories",
                        "categories": [mock_category],
                    }
                    assert result == expected_result
                    mock_service.create_system_categories.assert_called_once_with(
                        mock_superuser.id
                    )

    def test_init_system_categories_unauthorized(self, mock_user):
        """Test system categories initialization with unauthorized user."""
        with patch(
            "src.api.category.categories.get_current_active_user_with_bypass",
            return_value=mock_user,
        ):
            with patch("src.api.category.categories.get_db") as mock_get_db:
                mock_db = Mock()
                mock_get_db.return_value = mock_db

                from src.api.category.categories import init_system_categories

                with pytest.raises(HTTPException) as exc_info:
                    init_system_categories(current_user=mock_user, db=mock_db)

                assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
                assert exc_info.value.detail == "Not enough permissions"

    def test_init_system_categories_multiple_categories(self, mock_superuser):
        """Test system categories initialization with multiple categories."""
        mock_categories = [Mock(spec=Category) for _ in range(3)]
        for i, cat in enumerate(mock_categories):
            cat.id = i + 1
            cat.name = f"System Category {i + 1}"

        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.create_system_categories.return_value = mock_categories

            with patch(
                "src.api.category.categories.get_current_active_user_with_bypass",
                return_value=mock_superuser,
            ):
                with patch("src.api.category.categories.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.category.categories import init_system_categories

                    result = init_system_categories(
                        current_user=mock_superuser, db=mock_db
                    )

                    expected_result = {
                        "message": f"Created {len(mock_categories)} system categories",
                        "categories": mock_categories,
                    }
                    assert result == expected_result

    def test_router_initialization(self):
        """Test that the router is properly initialized."""
        from src.api.category.categories import router

        assert router is not None
        assert hasattr(router, "routes")

    def test_create_category_service_initialization(
        self, mock_user, sample_category_data
    ):
        """Test that CategoryService is properly initialized in create_category."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.create_category.return_value = Mock()

            with patch(
                "src.api.category.categories.get_current_active_user_with_bypass",
                return_value=mock_user,
            ):
                with patch("src.api.category.categories.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.category.categories import create_category

                    create_category(
                        category_data=CategoryCreate(**sample_category_data),
                        current_user=mock_user,
                        db=mock_db,
                    )

                    mock_service_class.assert_called_once_with(mock_db)

    def test_get_categories_service_initialization(self, mock_user):
        """Test that CategoryService is properly initialized in get_categories."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_user_categories.return_value = []

            with patch(
                "src.api.category.categories.get_current_active_user_with_bypass",
                return_value=mock_user,
            ):
                with patch("src.api.category.categories.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.category.categories import get_categories

                    get_categories(
                        skip=0, limit=100, current_user=mock_user, db=mock_db
                    )

                    mock_service_class.assert_called_once_with(mock_db)

    def test_get_category_service_initialization(self, mock_user, mock_category):
        """Test that CategoryService is properly initialized in get_category."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_category_by_id.return_value = mock_category

            with patch(
                "src.api.category.categories.get_current_active_user_with_bypass",
                return_value=mock_user,
            ):
                with patch("src.api.category.categories.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.category.categories import get_category

                    get_category(category_id=1, current_user=mock_user, db=mock_db)

                    mock_service_class.assert_called_once_with(mock_db)

    def test_update_category_service_initialization(
        self, mock_user, mock_category, sample_category_update_data
    ):
        """Test that CategoryService is properly initialized in update_category."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.update_category.return_value = mock_category

            with patch(
                "src.api.category.categories.get_current_active_user_with_bypass",
                return_value=mock_user,
            ):
                with patch("src.api.category.categories.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.category.categories import update_category

                    update_category(
                        category_id=1,
                        category_data=CategoryUpdate(**sample_category_update_data),
                        current_user=mock_user,
                        db=mock_db,
                    )

                    mock_service_class.assert_called_once_with(mock_db)

    def test_delete_category_service_initialization(self, mock_user):
        """Test that CategoryService is properly initialized in delete_category."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.delete_category.return_value = True

            with patch(
                "src.api.category.categories.get_current_active_user_with_bypass",
                return_value=mock_user,
            ):
                with patch("src.api.category.categories.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.category.categories import delete_category

                    delete_category(category_id=1, current_user=mock_user, db=mock_db)

                    mock_service_class.assert_called_once_with(mock_db)

    def test_init_system_categories_service_initialization(self, mock_superuser):
        """Test that CategoryService is properly initialized in init_system_categories."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.create_system_categories.return_value = []

            with patch(
                "src.api.category.categories.get_current_active_user_with_bypass",
                return_value=mock_superuser,
            ):
                with patch("src.api.category.categories.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.category.categories import init_system_categories

                    init_system_categories(current_user=mock_superuser, db=mock_db)

                    mock_service_class.assert_called_once_with(mock_db)
