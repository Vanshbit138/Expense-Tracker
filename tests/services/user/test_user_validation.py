"""
Tests for the user validation service.
"""

from src.services.user.user_validation import UserValidationService


class TestUserValidationService:
    """Test cases for user validation service."""

    def test_validate_email_valid(self):
        """Test email validation with valid email."""
        assert UserValidationService.validate_email("test@example.com") is True
        assert (
            UserValidationService.validate_email("user.name+tag@example.co.uk") is True
        )

    def test_validate_email_invalid(self):
        """Test email validation with invalid email."""
        assert UserValidationService.validate_email("invalid") is False
        assert UserValidationService.validate_email("@example.com") is False
        assert UserValidationService.validate_email("test@") is False
        assert UserValidationService.validate_email("test@@example.com") is False

    def test_validate_username_valid(self):
        """Test username validation with valid username."""
        assert UserValidationService.validate_username("user123") is True
        assert UserValidationService.validate_username("test_user") is True
        assert UserValidationService.validate_username("User_Name_123") is True

    def test_validate_username_invalid(self):
        """Test username validation with invalid username."""
        assert UserValidationService.validate_username("ab") is False  # Too short
        assert UserValidationService.validate_username("a" * 51) is False  # Too long
        assert (
            UserValidationService.validate_username("user-name") is False
        )  # Invalid char
        assert UserValidationService.validate_username("user name") is False  # Space
        assert (
            UserValidationService.validate_username("user@name") is False
        )  # Special char

    def test_validate_password_valid(self):
        """Test password validation with valid password."""
        assert UserValidationService.validate_password("password123") is True
        assert UserValidationService.validate_password("Pass123word") is True
        assert UserValidationService.validate_password("12345678a") is True

    def test_validate_password_invalid(self):
        """Test password validation with invalid password."""
        assert UserValidationService.validate_password("short1") is False  # Too short
        assert UserValidationService.validate_password("nodigits") is False  # No number
        assert UserValidationService.validate_password("12345678") is False  # No letter

    def test_validate_full_name_valid(self):
        """Test full name validation with valid names."""
        assert UserValidationService.validate_full_name("John Doe") is True
        assert UserValidationService.validate_full_name("Mary-Jane Smith") is True
        assert UserValidationService.validate_full_name("O'Brien") is True
        assert UserValidationService.validate_full_name(None) is True  # Optional
        assert (
            UserValidationService.validate_full_name("") is True
        )  # Will be False because empty

    def test_validate_full_name_invalid(self):
        """Test full name validation with invalid names."""
        assert UserValidationService.validate_full_name("   ") is False  # Only spaces
        assert UserValidationService.validate_full_name("a" * 101) is False  # Too long
        assert UserValidationService.validate_full_name("John123") is False  # Numbers
        assert (
            UserValidationService.validate_full_name("John@Doe") is False
        )  # Special char
