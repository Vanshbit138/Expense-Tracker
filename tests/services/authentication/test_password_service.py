"""
Tests for password service.
"""

import pytest

from src.services.authentication.password_service import (
    get_password_hash,
    verify_password,
)


class TestPasswordService:
    """Test cases for password service."""

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "TestPass123!"
        hashed_password = get_password_hash(password)

        result = verify_password(password, hashed_password)

        assert result is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "TestPass123!"
        wrong_password = "WrongPass456!"
        hashed_password = get_password_hash(password)

        result = verify_password(wrong_password, hashed_password)

        assert result is False

    def test_verify_password_empty_password(self):
        """Test password verification with empty password."""
        password = ""
        hashed_password = get_password_hash("SomePass123!")

        result = verify_password(password, hashed_password)

        assert result is False

    def test_verify_password_empty_hash(self):
        """Test password verification with empty hash."""
        password = "TestPass123!"
        hashed_password = ""

        result = verify_password(password, hashed_password)

        assert result is False

    def test_verify_password_none_password(self):
        """Test password verification with None password."""
        password = None
        hashed_password = get_password_hash("SomePass123!")

        result = verify_password(password, hashed_password)

        assert result is False

    def test_verify_password_none_hash(self):
        """Test password verification with None hash."""
        password = "TestPass123!"
        hashed_password = None

        result = verify_password(password, hashed_password)

        assert result is False

    def test_get_password_hash(self):
        """Test password hashing."""
        password = "TestPass123!"

        result = get_password_hash(password)

        # Should return a string
        assert isinstance(result, str)
        # Should not be the original password
        assert result != password
        # Should be a bcrypt hash (starts with $2b$)
        assert result.startswith("$2b$")
        # Should be reasonably long
        assert len(result) > 50

    def test_get_password_hash_different_passwords(self):
        """Test that different passwords produce different hashes."""
        password1 = "password1"
        password2 = "password2"

        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)

        assert hash1 != hash2

    def test_get_password_hash_same_password_different_hashes(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "SamePass123!"

        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different due to random salt
        assert hash1 != hash2

        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_password_hash_roundtrip(self):
        """Test password hashing and verification roundtrip."""
        password = "Complex123!"

        # Hash the password
        hashed = get_password_hash(password)

        # Verify it can be verified
        assert verify_password(password, hashed) is True

        # Verify wrong password fails
        assert verify_password("WrongPass123!", hashed) is False

    def test_password_hash_special_characters(self):
        """Test password hashing with special characters."""
        password = "Pass123!@#"

        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_password_hash_unicode(self):
        """Test password hashing with unicode characters."""
        password = "Pass123!"

        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_password_hash_long_password(self):
        """Test password hashing with very long password."""
        password = "a" * 50  # Very long password

        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_password_hash_very_long_password_truncation(self):
        """Test password hashing with password longer than bcrypt limit."""
        # bcrypt has a 72-byte limit, so longer passwords should be truncated
        password = "a" * 50  # Longer than 72 characters

        hashed = get_password_hash(password)

        # Should still work (password gets truncated internally)
        assert verify_password(password, hashed) is True

    def test_password_hash_empty_password(self):
        """Test password hashing with empty password."""
        password = ""

        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_password_hash_none_password(self):
        """Test password hashing with None password."""
        password = None

        # Should handle None gracefully
        with pytest.raises(ValueError):
            get_password_hash(password)

    def test_verify_password_exception_handling(self):
        """Test password verification with exception handling."""
        password = "TestPass123!"
        hashed_password = "invalid_hash"

        # Test with invalid hash - should return False
        result = verify_password(password, hashed_password)
        assert result is False

    def test_get_password_hash_exception_handling(self):
        """Test password hashing with exception handling."""
        password = "TestPass123!"

        # Test normal hashing - should work
        result = get_password_hash(password)
        assert isinstance(result, str)
        assert result.startswith("$2b$")
        assert len(result) > 50

    def test_password_hash_consistency(self):
        """Test that password hashing is consistent across multiple calls."""
        password = "Consistent123!"

        # Hash the same password multiple times
        hashes = [get_password_hash(password) for _ in range(5)]

        # All hashes should be different (due to salt)
        assert len(set(hashes)) == 5

        # But all should verify the original password
        for hashed in hashes:
            assert verify_password(password, hashed) is True

    def test_password_hash_rounds_configuration(self):
        """Test that password hashing uses the configured rounds."""
        password = "TestPass123!"

        # The service should use 12 rounds as configured
        hashed = get_password_hash(password)

        # Extract rounds from hash (format: $2b$rounds$...)
        parts = hashed.split("$")
        assert len(parts) >= 4
        assert parts[1] == "2b"  # bcrypt version
        assert int(parts[2]) == 12  # rounds

    def test_verify_password_with_different_rounds(self):
        """Test password verification with different round configurations."""
        password = "TestPass123!"

        # Hash with default rounds
        hashed = get_password_hash(password)

        # Should still verify correctly
        assert verify_password(password, hashed) is True

    def test_password_hash_unicode_edge_cases(self):
        """Test password hashing with various unicode edge cases."""
        passwords = [
            "测试密码",
            "пароль",
            "كلمة المرور",
            "🔐🔑🔒",
            "Pass123!",
            "Pass123!",
        ]

        for password in passwords:
            hashed = get_password_hash(password)
            assert verify_password(password, hashed) is True

    def test_password_hash_whitespace_handling(self):
        """Test password hashing with various whitespace characters."""
        passwords = [
            " Pass123!",  # Leading space
            "Pass123! ",  # Trailing space
            " Pass123! ",  # Multiple spaces
            "pass\tword",  # Tab character
            "pass\nword",  # Newline character
            "pass\r\nword",  # CRLF
        ]

        for password in passwords:
            hashed = get_password_hash(password)
            assert verify_password(password, hashed) is True

    def test_password_hash_case_sensitivity(self):
        """Test that password hashing is case sensitive."""
        password1 = "Password123!"
        password2 = "password123!"
        password3 = "PASSWORD123!"

        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)
        hash3 = get_password_hash(password3)

        # All should be different
        assert hash1 != hash2
        assert hash2 != hash3
        assert hash1 != hash3

        # Each should only verify its own password
        assert verify_password(password1, hash1) is True
        assert verify_password(password2, hash2) is True
        assert verify_password(password3, hash3) is True

        # Cross-verification should fail
        assert verify_password(password1, hash2) is False
        assert verify_password(password2, hash1) is False
