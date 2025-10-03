"""
Tests for CategoryValidationService.
"""

import pytest

from src.services.category.category_validation import CategoryValidationService


class TestCategoryValidationService:
    """Test cases for CategoryValidationService."""

    def test_validate_name_valid(self):
        """Test valid category name validation."""
        # Test normal name
        assert CategoryValidationService.validate_name("Food & Dining") is True

        # Test name with minimum length
        assert CategoryValidationService.validate_name("A") is True

        # Test name with maximum length (100 chars)
        long_name = "A" * 100
        assert CategoryValidationService.validate_name(long_name) is True

    def test_validate_name_invalid(self):
        """Test invalid category name validation."""
        # Test empty string
        assert CategoryValidationService.validate_name("") is False

        # Test whitespace only
        assert CategoryValidationService.validate_name("   ") is False

        # Test name too long (over 100 chars)
        long_name = "A" * 101
        assert CategoryValidationService.validate_name(long_name) is False

    def test_validate_name_none_raises_error(self):
        """Test that validate_name raises AttributeError for None."""
        with pytest.raises(AttributeError):
            CategoryValidationService.validate_name(None)

    def test_validate_name_edge_cases(self):
        """Test edge cases for name validation."""
        # Test name with leading/trailing whitespace (should be valid after strip)
        assert CategoryValidationService.validate_name("  Food  ") is True

        # Test name with special characters
        assert CategoryValidationService.validate_name("Food & Dining!") is True

        # Test name with numbers
        assert CategoryValidationService.validate_name("Category123") is True

    def test_validate_color_valid(self):
        """Test valid color validation."""
        # Test valid hex colors without #
        assert CategoryValidationService.validate_color("FF0000") is True
        assert CategoryValidationService.validate_color("00FF00") is True
        assert CategoryValidationService.validate_color("0000FF") is True
        assert CategoryValidationService.validate_color("ABCDEF") is True
        assert CategoryValidationService.validate_color("123456") is True
        assert CategoryValidationService.validate_color("abcdef") is True

    def test_validate_color_with_hash(self):
        """Test color validation with # prefix."""
        # Test valid hex colors with #
        assert CategoryValidationService.validate_color("#FF0000") is True
        assert CategoryValidationService.validate_color("#00FF00") is True
        assert CategoryValidationService.validate_color("#0000FF") is True
        assert CategoryValidationService.validate_color("#ABCDEF") is True
        assert CategoryValidationService.validate_color("#123456") is True
        assert CategoryValidationService.validate_color("#abcdef") is True

    def test_validate_color_invalid(self):
        """Test invalid color validation."""
        # Test invalid hex colors
        assert CategoryValidationService.validate_color("GG0000") is False
        assert CategoryValidationService.validate_color("FF00") is False  # Too short
        assert CategoryValidationService.validate_color("FF00000") is False  # Too long
        assert (
            CategoryValidationService.validate_color("FF000") is False
        )  # Wrong length
        assert CategoryValidationService.validate_color("ZZZZZZ") is False
        assert CategoryValidationService.validate_color("12345G") is False

    def test_validate_color_edge_cases(self):
        """Test edge cases for color validation."""
        # Test None (should be valid)
        assert CategoryValidationService.validate_color(None) is True

        # Test empty string (should be valid)
        assert CategoryValidationService.validate_color("") is True

        # Test color with multiple # symbols (lstrip removes all leading #, so ##FF0000 becomes FF0000 which is valid)
        assert CategoryValidationService.validate_color("##FF0000") is True

        # Test color with spaces
        assert CategoryValidationService.validate_color("FF 00 00") is False

        # Test color with special characters
        assert CategoryValidationService.validate_color("FF-00-00") is False

    def test_validate_description_valid(self):
        """Test valid description validation."""
        # Test normal description
        assert CategoryValidationService.validate_description("A test category") is True

        # Test empty description (should be valid)
        assert CategoryValidationService.validate_description("") is True

        # Test None description (should be valid)
        assert CategoryValidationService.validate_description(None) is True

        # Test description with maximum length (500 chars)
        long_description = "A" * 500
        assert CategoryValidationService.validate_description(long_description) is True

    def test_validate_description_invalid(self):
        """Test invalid description validation."""
        # Test description too long (over 500 chars)
        long_description = "A" * 501
        assert CategoryValidationService.validate_description(long_description) is False

    def test_validate_description_edge_cases(self):
        """Test edge cases for description validation."""
        # Test description with special characters
        assert (
            CategoryValidationService.validate_description("Food & Dining! @#$%")
            is True
        )

        # Test description with numbers
        assert CategoryValidationService.validate_description("Category 123") is True

        # Test description with newlines
        assert CategoryValidationService.validate_description("Line 1\nLine 2") is True

        # Test description with unicode characters
        assert (
            CategoryValidationService.validate_description("Café & Restaurant") is True
        )

    def test_validate_name_boundary_values(self):
        """Test boundary values for name validation."""
        # Test exactly 1 character (should be valid)
        assert CategoryValidationService.validate_name("A") is True

        # Test exactly 100 characters (should be valid)
        name_100 = "A" * 100
        assert CategoryValidationService.validate_name(name_100) is True

        # Test 101 characters (should be invalid)
        name_101 = "A" * 101
        assert CategoryValidationService.validate_name(name_101) is False

    def test_validate_description_boundary_values(self):
        """Test boundary values for description validation."""
        # Test exactly 500 characters (should be valid)
        desc_500 = "A" * 500
        assert CategoryValidationService.validate_description(desc_500) is True

        # Test 501 characters (should be invalid)
        desc_501 = "A" * 501
        assert CategoryValidationService.validate_description(desc_501) is False

    def test_validate_color_length_variations(self):
        """Test color validation with different lengths."""
        # Test 3 characters (should be invalid)
        assert CategoryValidationService.validate_color("FFF") is False

        # Test 6 characters (should be valid)
        assert CategoryValidationService.validate_color("FFFFFF") is True

        # Test 7 characters (should be invalid)
        assert CategoryValidationService.validate_color("FFFFFFF") is False

        # Test 8 characters (should be invalid)
        assert CategoryValidationService.validate_color("FFFFFFFF") is False

    def test_validate_color_hex_case_insensitive(self):
        """Test that color validation is case insensitive."""
        # Test uppercase
        assert CategoryValidationService.validate_color("ABCDEF") is True

        # Test lowercase
        assert CategoryValidationService.validate_color("abcdef") is True

        # Test mixed case
        assert CategoryValidationService.validate_color("AbCdEf") is True

    def test_validate_name_whitespace_handling(self):
        """Test name validation with various whitespace scenarios."""
        # Test name with only spaces (should be invalid after strip)
        assert CategoryValidationService.validate_name("   ") is False

        # Test name with tabs (should be invalid after strip)
        assert CategoryValidationService.validate_name("\t\t\t") is False

        # Test name with newlines (should be invalid after strip)
        assert CategoryValidationService.validate_name("\n\n\n") is False

        # Test name with mixed whitespace (should be invalid after strip)
        assert CategoryValidationService.validate_name(" \t\n ") is False

    def test_validate_color_with_whitespace(self):
        """Test color validation with whitespace."""
        # Test color with leading/trailing spaces
        assert CategoryValidationService.validate_color(" FF0000 ") is False

        # Test color with spaces in the middle
        assert CategoryValidationService.validate_color("FF 00 00") is False

        # Test color with tabs
        assert CategoryValidationService.validate_color("\tFF0000") is False

    def test_validate_description_whitespace_handling(self):
        """Test description validation with whitespace."""
        # Test description with only spaces (should be valid)
        assert CategoryValidationService.validate_description("   ") is True

        # Test description with tabs (should be valid)
        assert CategoryValidationService.validate_description("\t\t\t") is True

        # Test description with newlines (should be valid)
        assert CategoryValidationService.validate_description("\n\n\n") is True
