"""
Tests for user schemas.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.schemas.user.user import User, UserBase, UserCreate, UserInDB, UserUpdate


class TestUserBase:
    """Test cases for UserBase schema."""

    def test_user_base_valid_data(self):
        """Test UserBase with valid data."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
        }

        user = UserBase(**user_data)

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"

    def test_user_base_minimal_data(self):
        """Test UserBase with minimal required data."""
        user_data = {"email": "test@example.com", "username": "testuser"}

        user = UserBase(**user_data)

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name is None

    def test_user_base_username_validation_too_short(self):
        """Test UserBase username validation - too short."""
        user_data = {"email": "test@example.com", "username": "a"}  # Too short

        with pytest.raises(ValidationError) as exc_info:
            UserBase(**user_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)

    def test_user_base_username_validation_invalid_characters(self):
        """Test UserBase username validation - invalid characters."""
        user_data = {"email": "test@example.com", "username": "test@user"}  # Contains @

        with pytest.raises(ValidationError) as exc_info:
            UserBase(**user_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)

    def test_user_base_username_validation_spaces(self):
        """Test UserBase username validation - spaces."""
        user_data = {
            "email": "test@example.com",
            "username": "test user",  # Contains space
        }

        with pytest.raises(ValidationError) as exc_info:
            UserBase(**user_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)

    def test_user_base_username_validation_dots(self):
        """Test UserBase username validation - dots."""
        user_data = {
            "email": "test@example.com",
            "username": "test.user",  # Contains dot
        }

        with pytest.raises(ValidationError) as exc_info:
            UserBase(**user_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)

    def test_user_base_username_validation_valid_characters(self):
        """Test UserBase username validation - valid characters."""
        valid_usernames = [
            "testuser",
            "test_user",
            "test-user",
            "test123",
            "TestUser123",
            "test_user-123",
        ]

        for username in valid_usernames:
            user_data = {"email": "test@example.com", "username": username}

            user = UserBase(**user_data)
            assert user.username == username

    def test_user_base_full_name_validation_too_short(self):
        """Test UserBase full_name validation - too short."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "A",  # Too short
        }

        with pytest.raises(ValidationError) as exc_info:
            UserBase(**user_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)

    def test_user_base_full_name_validation_whitespace(self):
        """Test UserBase full_name validation - whitespace handling."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "  Test User  ",
        }

        user = UserBase(**user_data)
        assert user.full_name == "Test User"  # Should be stripped

    def test_user_base_full_name_validation_none(self):
        """Test UserBase full_name validation - None value."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": None,
        }

        user = UserBase(**user_data)
        assert user.full_name is None

    def test_user_base_email_validation(self):
        """Test UserBase email validation."""
        user_data = {"email": "test@example.com", "username": "testuser"}

        user = UserBase(**user_data)
        assert user.email == "test@example.com"

    def test_user_base_email_validation_invalid(self):
        """Test UserBase email validation - invalid email."""
        user_data = {"email": "invalid-email", "username": "testuser"}

        with pytest.raises(ValidationError) as exc_info:
            UserBase(**user_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)


class TestUserCreate:
    """Test cases for UserCreate schema."""

    def test_user_create_valid_data(self):
        """Test UserCreate with valid data."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "TestPassword123!",
        }

        user = UserCreate(**user_data)

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.password == "TestPassword123!"

    def test_user_create_password_validation_too_short(self):
        """Test UserCreate password validation - too short."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "Test1!",  # Too short
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)

    def test_user_create_password_validation_no_uppercase(self):
        """Test UserCreate password validation - no uppercase."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123!",  # No uppercase
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)

    def test_user_create_password_validation_no_lowercase(self):
        """Test UserCreate password validation - no lowercase."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "TESTPASSWORD123!",  # No lowercase
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)

    def test_user_create_password_validation_no_digit(self):
        """Test UserCreate password validation - no digit."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPassword!",  # No digit
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)

    def test_user_create_password_validation_no_special_character(self):
        """Test UserCreate password validation - no special character."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPassword123",  # No special character
        }

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)

    def test_user_create_password_validation_valid_passwords(self):
        """Test UserCreate password validation - valid passwords."""
        valid_passwords = [
            "TestPassword123!",
            "MySecure123@",
            "AnotherPass456#",
            "ValidPass789$",
        ]

        for password in valid_passwords:
            user_data = {
                "email": "test@example.com",
                "username": "testuser",
                "password": password,
            }

            user = UserCreate(**user_data)
            assert user.password == password

    def test_user_create_inherits_user_base_validation(self):
        """Test that UserCreate inherits UserBase validation."""
        user_data = {
            "email": "test@example.com",
            "username": "a",  # Invalid - too short
            "password": "TestPassword123!",
        }

        with pytest.raises(ValidationError):
            UserCreate(**user_data)


class TestUserUpdate:
    """Test cases for UserUpdate schema."""

    def test_user_update_all_fields(self):
        """Test UserUpdate with all fields."""
        user_data = {
            "email": "updated@example.com",
            "username": "updateduser",
            "full_name": "Updated User",
            "is_active": True,
        }

        user = UserUpdate(**user_data)

        assert user.email == "updated@example.com"
        assert user.username == "updateduser"
        assert user.full_name == "Updated User"
        assert user.is_active is True

    def test_user_update_partial_fields(self):
        """Test UserUpdate with partial fields."""
        user_data = {"email": "updated@example.com", "username": "updateduser"}

        user = UserUpdate(**user_data)

        assert user.email == "updated@example.com"
        assert user.username == "updateduser"
        assert user.full_name is None
        assert user.is_active is None

    def test_user_update_empty(self):
        """Test UserUpdate with no fields."""
        user_data = {}

        user = UserUpdate(**user_data)

        assert user.email is None
        assert user.username is None
        assert user.full_name is None
        assert user.is_active is None

    def test_user_update_username_validation(self):
        """Test UserUpdate username validation."""
        user_data = {"username": "a"}  # Invalid - too short

        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(**user_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)

    def test_user_update_full_name_validation(self):
        """Test UserUpdate full_name validation."""
        user_data = {"full_name": "A"}  # Invalid - too short

        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(**user_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)

    def test_user_update_whitespace_handling(self):
        """Test UserUpdate whitespace handling."""
        user_data = {"username": "testuser", "full_name": "  Test User  "}

        user = UserUpdate(**user_data)

        assert user.username == "testuser"
        assert user.full_name == "Test User"


class TestUserInDB:
    """Test cases for UserInDB schema."""

    def test_user_in_db_valid_data(self):
        """Test UserInDB with valid data."""
        user_data = {
            "id": 1,
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "hashed_password": "hashed_password_here",
            "is_active": True,
            "is_superuser": False,
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "updated_at": datetime(2024, 1, 1, 12, 0, 0),
        }

        user = UserInDB(**user_data)

        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.hashed_password == "hashed_password_here"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.created_at == datetime(2024, 1, 1, 12, 0, 0)
        assert user.updated_at == datetime(2024, 1, 1, 12, 0, 0)

    def test_user_in_db_inherits_user_base_validation(self):
        """Test that UserInDB inherits UserBase validation."""
        user_data = {
            "id": 1,
            "email": "test@example.com",
            "username": "a",  # Invalid - too short
            "hashed_password": "hashed_password_here",
            "is_active": True,
            "is_superuser": False,
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "updated_at": datetime(2024, 1, 1, 12, 0, 0),
        }

        with pytest.raises(ValidationError):
            UserInDB(**user_data)


class TestUser:
    """Test cases for User schema."""

    def test_user_valid_data(self):
        """Test User with valid data."""
        user_data = {
            "id": 1,
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "is_active": True,
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "updated_at": datetime(2024, 1, 1, 12, 0, 0),
        }

        user = User(**user_data)

        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.created_at == datetime(2024, 1, 1, 12, 0, 0)
        assert user.updated_at == datetime(2024, 1, 1, 12, 0, 0)

    def test_user_inherits_user_base_validation(self):
        """Test that User inherits UserBase validation."""
        user_data = {
            "id": 1,
            "email": "test@example.com",
            "username": "a",  # Invalid - too short
            "is_active": True,
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "updated_at": datetime(2024, 1, 1, 12, 0, 0),
        }

        with pytest.raises(ValidationError):
            User(**user_data)

    def test_user_from_attributes_config(self):
        """Test User from_attributes configuration."""

        # This tests the Config.from_attributes = True setting
        class MockUser:
            def __init__(self):
                self.id = 1
                self.email = "test@example.com"
                self.username = "testuser"
                self.full_name = "Test User"
                self.is_active = True
                self.created_at = datetime(2024, 1, 1, 12, 0, 0)
                self.updated_at = datetime(2024, 1, 1, 12, 0, 0)

        mock_user = MockUser()
        user = User.model_validate(mock_user)

        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.created_at == datetime(2024, 1, 1, 12, 0, 0)
        assert user.updated_at == datetime(2024, 1, 1, 12, 0, 0)
