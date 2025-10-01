"""
Tests for the security module.
"""

from datetime import datetime, timedelta
from unittest.mock import patch

from src.core.config import settings
from src.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    verify_token,
)


class TestSecurity:
    """Test cases for security utilities."""

    def test_create_access_token_default_expiry(self):
        """Test creating access token with default expiry."""
        subject = "test_user_id"

        with patch("src.core.security.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)

            with patch("src.core.security.jwt.encode") as mock_jwt_encode:
                mock_jwt_encode.return_value = "test_token"

                result = create_access_token(subject)

                assert result == "test_token"
                mock_jwt_encode.assert_called_once()

                # Check the call arguments
                call_args = mock_jwt_encode.call_args

                # Check the payload
                payload = call_args[0][0]
                assert payload["sub"] == str(subject)
                assert "exp" in payload

                # Check the key and algorithm
                assert call_args[0][1] == settings.secret_key
                # Check if algorithm is passed as keyword argument
                if len(call_args[0]) > 2:
                    assert call_args[0][2] == settings.algorithm
                else:
                    # Check if algorithm is in kwargs
                    assert call_args[1]["algorithm"] == settings.algorithm

    def test_create_access_token_custom_expiry(self):
        """Test creating access token with custom expiry."""
        subject = "test_user_id"
        custom_expiry = timedelta(hours=2)

        with patch("src.core.security.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)

            with patch("src.core.security.jwt.encode") as mock_jwt_encode:
                mock_jwt_encode.return_value = "test_token"

                result = create_access_token(subject, custom_expiry)

                assert result == "test_token"
                mock_jwt_encode.assert_called_once()

                # Check the call arguments
                call_args = mock_jwt_encode.call_args

                # Check the payload
                payload = call_args[0][0]
                assert payload["sub"] == str(subject)
                assert "exp" in payload

                # Check the key and algorithm
                assert call_args[0][1] == settings.secret_key
                # Check if algorithm is passed as keyword argument
                if len(call_args[0]) > 2:
                    assert call_args[0][2] == settings.algorithm
                else:
                    # Check if algorithm is in kwargs
                    assert call_args[1]["algorithm"] == settings.algorithm

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "test_password"
        hashed = get_password_hash(password)

        result = verify_password(password, hashed)
        assert result is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "test_password"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)

        result = verify_password(wrong_password, hashed)
        assert result is False

    def test_get_password_hash(self):
        """Test password hashing."""
        password = "test_password"

        result = get_password_hash(password)

        assert isinstance(result, str)
        assert result != password  # Should be hashed
        assert len(result) > 0

    def test_get_password_hash_different_passwords(self):
        """Test that different passwords produce different hashes."""
        password1 = "password1"
        password2 = "password2"

        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)

        assert hash1 != hash2

    def test_get_password_hash_same_password_different_hashes(self):
        """Test that same password produces different hashes (due to salt)."""
        password = "same_password"

        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Should be different due to salt
        assert hash1 != hash2

    def test_verify_token_valid(self):
        """Test token verification with valid token."""
        subject = "test_user_id"
        token = create_access_token(subject)

        result = verify_token(token)
        assert result == subject

    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        invalid_token = "invalid_token"

        result = verify_token(invalid_token)
        assert result is None

    def test_verify_token_expired(self):
        """Test token verification with expired token."""
        subject = "test_user_id"
        # Create token with very short expiry
        short_expiry = timedelta(seconds=-1)  # Already expired
        token = create_access_token(subject, short_expiry)

        result = verify_token(token)
        assert result is None

    def test_password_hash_length(self):
        """Test that password hash has reasonable length."""
        password = "test_password"
        hashed = get_password_hash(password)

        # Bcrypt hashes are typically 60 characters
        assert len(hashed) == 60

    def test_password_hash_structure(self):
        """Test that password hash has expected structure."""
        password = "test_password"
        hashed = get_password_hash(password)

        # Bcrypt hashes start with $2b$
        assert hashed.startswith("$2b$")

    def test_create_access_token_string_subject(self):
        """Test creating access token with string subject."""
        subject = "string_user_id"
        token = create_access_token(subject)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_numeric_subject(self):
        """Test creating access token with numeric subject."""
        subject = 12345
        token = create_access_token(subject)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_object_subject(self):
        """Test creating access token with object subject."""

        class TestObject:
            def __str__(self):
                return "object_user_id"

        subject = TestObject()
        token = create_access_token(subject)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_get_password_hash_empty_string(self):
        """Test password hashing with empty string."""
        password = ""
        hashed = get_password_hash(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_get_password_hash_very_long_password(self):
        """Test password hashing with very long password."""
        password = "a" * 1000  # Very long password
        hashed = get_password_hash(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_create_access_token_with_none_expiry(self):
        """Test creating access token with None expiry (should use default)."""
        subject = "test_user_id"

        with patch("src.core.security.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2024, 1, 1, 12, 0, 0)

            with patch("src.core.security.jwt.encode") as mock_jwt_encode:
                mock_jwt_encode.return_value = "test_token"

                result = create_access_token(subject, None)

                assert result == "test_token"
                mock_jwt_encode.assert_called_once()

    def test_verify_token_malformed_token(self):
        """Test token verification with malformed token."""
        malformed_tokens = [
            "not.a.token",
            "too.many.parts.here.token",
            "invalid",
            "",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid.signature",
        ]

        for token in malformed_tokens:
            result = verify_token(token)
            assert result is None

    def test_verify_token_missing_subject(self):
        """Test token verification with token missing subject."""
        # Create a token without subject
        with patch("src.core.security.jwt.encode") as mock_jwt_encode:
            mock_jwt_encode.return_value = "token_without_subject"

            # Mock jwt.decode to return payload without 'sub'
            with patch("src.core.security.jwt.decode") as mock_jwt_decode:
                mock_jwt_decode.return_value = {"exp": 1234567890}  # No 'sub' field

                result = verify_token("token_without_subject")
                assert result is None

    def test_verify_token_jwt_error_handling(self):
        """Test token verification when jwt.decode raises JWTError."""
        from jose import jwt

        with patch("src.core.security.jwt.decode") as mock_jwt_decode:
            mock_jwt_decode.side_effect = jwt.JWTError("JWT error")

            # Should not raise exception, should return None
            result = verify_token("any_token")
            assert result is None
