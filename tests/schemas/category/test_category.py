"""
Tests for category schemas.
"""

import pytest
from pydantic import ValidationError

from src.schemas.category.category import (
    Category,
    CategoryBase,
    CategoryCreate,
    CategoryInDB,
    CategoryUpdate,
)


class TestCategoryBase:
    """Test cases for CategoryBase schema."""

    def test_category_base_valid_data(self):
        """Test CategoryBase with valid data."""
        category_data = {"name": "Test Category", "description": "A test category"}

        category = CategoryBase(**category_data)

        assert category.name == "Test Category"
        assert category.description == "A test category"

    def test_category_base_minimal_data(self):
        """Test CategoryBase with minimal required data."""
        category_data = {"name": "Test Category"}

        category = CategoryBase(**category_data)

        assert category.name == "Test Category"
        assert category.description is None

    def test_category_base_name_required(self):
        """Test CategoryBase name is required."""
        category_data = {}

        with pytest.raises(ValidationError) as exc_info:
            CategoryBase(**category_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "missing" for error in errors)
        assert any(error["loc"] == ("name",) for error in errors)

    def test_category_base_name_not_empty(self):
        """Test CategoryBase name cannot be empty."""
        category_data = {"name": ""}

        with pytest.raises(ValidationError) as exc_info:
            CategoryBase(**category_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)

    def test_category_base_description_optional(self):
        """Test CategoryBase description is optional."""
        category_data = {"name": "Test Category", "description": None}

        category = CategoryBase(**category_data)

        assert category.name == "Test Category"
        assert category.description is None

    def test_category_base_long_description(self):
        """Test CategoryBase with long description."""
        long_description = "A" * 1000
        category_data = {"name": "Test Category", "description": long_description}

        with pytest.raises(ValidationError) as exc_info:
            CategoryBase(**category_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)

    def test_category_base_name_validation(self):
        """Test CategoryBase name validation."""
        # Test name too long
        long_name = "A" * 101
        category_data = {"name": long_name}

        with pytest.raises(ValidationError) as exc_info:
            CategoryBase(**category_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)

    def test_category_base_name_whitespace_handling(self):
        """Test CategoryBase name whitespace handling."""
        category_data = {"name": "  Test Category  "}

        category = CategoryBase(**category_data)
        assert category.name == "Test Category"  # Should be stripped

    def test_category_base_description_whitespace_handling(self):
        """Test CategoryBase description whitespace handling."""
        category_data = {
            "name": "Test Category",
            "description": "  A test description  ",
        }

        category = CategoryBase(**category_data)
        assert category.description == "A test description"  # Should be stripped


class TestCategoryCreate:
    """Test cases for CategoryCreate schema."""

    def test_category_create_valid_data(self):
        """Test CategoryCreate with valid data."""
        category_data = {"name": "Test Category", "description": "A test category"}

        category = CategoryCreate(**category_data)

        assert category.name == "Test Category"
        assert category.description == "A test category"

    def test_category_create_inherits_category_base(self):
        """Test that CategoryCreate inherits CategoryBase validation."""
        category_data = {"name": ""}  # Invalid - empty name

        with pytest.raises(ValidationError):
            CategoryCreate(**category_data)


class TestCategoryUpdate:
    """Test cases for CategoryUpdate schema."""

    def test_category_update_all_fields(self):
        """Test CategoryUpdate with all fields."""
        category_data = {
            "name": "Updated Category",
            "description": "Updated description",
        }

        category = CategoryUpdate(**category_data)

        assert category.name == "Updated Category"
        assert category.description == "Updated description"

    def test_category_update_partial_fields(self):
        """Test CategoryUpdate with partial fields."""
        category_data = {"name": "Updated Category"}

        category = CategoryUpdate(**category_data)

        assert category.name == "Updated Category"
        assert category.description is None

    def test_category_update_empty(self):
        """Test CategoryUpdate with no fields."""
        category_data = {}

        category = CategoryUpdate(**category_data)

        assert category.name is None
        assert category.description is None

    def test_category_update_inherits_category_base(self):
        """Test that CategoryUpdate inherits CategoryBase validation."""
        category_data = {"name": ""}  # Invalid - empty name

        with pytest.raises(ValidationError):
            CategoryUpdate(**category_data)


class TestCategoryInDB:
    """Test cases for CategoryInDB schema."""

    def test_category_in_db_valid_data(self):
        """Test CategoryInDB with valid data."""
        from datetime import datetime

        category_data = {
            "id": 1,
            "name": "Test Category",
            "description": "A test category",
            "user_id": 1,
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "updated_at": datetime(2024, 1, 1, 12, 0, 0),
        }

        category = CategoryInDB(**category_data)

        assert category.id == 1
        assert category.name == "Test Category"
        assert category.description == "A test category"
        assert category.user_id == 1
        assert category.created_at == datetime(2024, 1, 1, 12, 0, 0)
        assert category.updated_at == datetime(2024, 1, 1, 12, 0, 0)

    def test_category_in_db_system_category(self):
        """Test CategoryInDB with system category."""
        from datetime import datetime

        category_data = {
            "id": 1,
            "name": "System Category",
            "user_id": 1,  # System categories still have user_id
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "updated_at": datetime(2024, 1, 1, 12, 0, 0),
        }

        category = CategoryInDB(**category_data)

        assert category.user_id == 1

    def test_category_in_db_inherits_category_base(self):
        """Test that CategoryInDB inherits CategoryBase validation."""
        from datetime import datetime

        category_data = {
            "id": 1,
            "name": "",  # Invalid - empty name
            "user_id": 1,
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "updated_at": datetime(2024, 1, 1, 12, 0, 0),
        }

        with pytest.raises(ValidationError):
            CategoryInDB(**category_data)


class TestCategory:
    """Test cases for Category schema."""

    def test_category_valid_data(self):
        """Test Category with valid data."""
        from datetime import datetime

        category_data = {
            "id": 1,
            "name": "Test Category",
            "description": "A test category",
            "user_id": 1,
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "updated_at": datetime(2024, 1, 1, 12, 0, 0),
        }

        category = Category(**category_data)

        assert category.id == 1
        assert category.name == "Test Category"
        assert category.description == "A test category"
        assert category.user_id == 1
        assert category.created_at == datetime(2024, 1, 1, 12, 0, 0)
        assert category.updated_at == datetime(2024, 1, 1, 12, 0, 0)

    def test_category_inherits_category_base(self):
        """Test that Category inherits CategoryBase validation."""
        from datetime import datetime

        category_data = {
            "id": 1,
            "name": "",  # Invalid - empty name
            "user_id": 1,
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "updated_at": datetime(2024, 1, 1, 12, 0, 0),
        }

        with pytest.raises(ValidationError):
            Category(**category_data)

    def test_category_from_attributes_config(self):
        """Test Category from_attributes configuration."""
        from datetime import datetime

        # This tests the Config.from_attributes = True setting
        class MockCategory:
            def __init__(self):
                self.id = 1
                self.name = "Test Category"
                self.description = "A test category"
                self.user_id = 1
                self.created_at = datetime(2024, 1, 1, 12, 0, 0)
                self.updated_at = datetime(2024, 1, 1, 12, 0, 0)

        mock_category = MockCategory()
        category = Category.model_validate(mock_category)

        assert category.id == 1
        assert category.name == "Test Category"
        assert category.description == "A test category"
        assert category.user_id == 1
        assert category.created_at == datetime(2024, 1, 1, 12, 0, 0)
        assert category.updated_at == datetime(2024, 1, 1, 12, 0, 0)
