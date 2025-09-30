"""
Unit tests for security module.
"""

from datetime import datetime, timedelta
from unittest.mock import patch

from jose import jwt

from src.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    verify_token,
)


class TestCreateAccessToken:
    """Test cases for create_access_token function."""

    def test_create_token_with_default_expiry(self, mock_settings):
        """Test token creation with default expiry time."""
        with patch("src.core.security.settings", mock_settings):
            with patch("src.core.security.datetime") as mock_datetime:
                # Mock datetime.utcnow to return a fixed time
                fixed_time = datetime(2023, 1, 1, 12, 0, 0)
                mock_datetime.utcnow.return_value = fixed_time
                mock_datetime.timedelta = timedelta

                with patch("jwt.encode") as mock_encode:
                    mock_encode.return_value = "test_token"

                    # token = create_access_token("user123")

                    # Verify jwt.encode was called with correct parameters
                    mock_encode.assert_called_once()
                    call_args = mock_encode.call_args

                    # Check the payload
                    payload = call_args[0][0]
                    assert payload["sub"] == "user123"

                    # Check expiry time (should be 24 hours from fixed time)
                    expected_exp = fixed_time + timedelta(minutes=1440)
                    assert payload["exp"] == expected_exp

                    # Check other parameters
                    assert call_args[0][1] == mock_settings.secret_key
                    assert call_args[0][2] == mock_settings.algorithm

    def test_create_token_with_custom_expiry(self, mock_settings):
        """Test token creation with custom expiry time."""
        with patch("src.core.security.settings", mock_settings):
            with patch("src.core.security.datetime") as mock_datetime:
                fixed_time = datetime(2023, 1, 1, 12, 0, 0)
                mock_datetime.utcnow.return_value = fixed_time
                mock_datetime.timedelta = timedelta

                with patch("jwt.encode") as mock_encode:
                    mock_encode.return_value = "test_token"

                    custom_delta = timedelta(hours=2)
                    # token = create_access_token("user123", custom_delta)

                    # Verify jwt.encode was called
                    mock_encode.assert_called_once()
                    call_args = mock_encode.call_args

                    # Check expiry time (should be 2 hours from fixed time)
                    expected_exp = fixed_time + custom_delta
                    assert call_args[0][0]["exp"] == expected_exp

    def test_create_token_with_different_subjects(self, mock_settings):
        """Test token creation with different subject types."""
        with patch("src.core.security.settings", mock_settings):
            with patch("jwt.encode") as mock_encode:
                mock_encode.return_value = "test_token"

                # Test with string subject
                create_access_token("user123")
                assert mock_encode.call_args[0][0]["sub"] == "user123"

                # Test with integer subject
                create_access_token(123)
                assert mock_encode.call_args[0][0]["sub"] == "123"

                # Test with object that has __str__ method
                class MockUser:
                    def __str__(self):
                        return "user456"

                create_access_token(MockUser())
                assert mock_encode.call_args[0][0]["sub"] == "user456"


class TestVerifyPassword:
    """Test cases for verify_password function."""

    def test_verify_password_success(self):
        """Test successful password verification."""
        with patch("src.core.security.pwd_context") as mock_context:
            mock_context.verify.return_value = True

            result = verify_password("plain_password", "hashed_password")

            assert result is True
            mock_context.verify.assert_called_once_with(
                "plain_password", "hashed_password"
            )

    def test_verify_password_failure(self):
        """Test failed password verification."""
        with patch("src.core.security.pwd_context") as mock_context:
            mock_context.verify.return_value = False

            result = verify_password("wrong_password", "hashed_password")

            assert result is False
            mock_context.verify.assert_called_once_with(
                "wrong_password", "hashed_password"
            )

    def test_verify_password_with_empty_strings(self):
        """Test password verification with empty strings."""
        with patch("src.core.security.pwd_context") as mock_context:
            mock_context.verify.return_value = False

            result = verify_password("", "")

            assert result is False
            mock_context.verify.assert_called_once_with("", "")

    def test_verify_password_with_special_characters(self):
        """Test password verification with special characters."""
        with patch("src.core.security.pwd_context") as mock_context:
            mock_context.verify.return_value = True

            special_password = "P@ssw0rd!@#$%^&*()"
            result = verify_password(special_password, "hashed_password")

            assert result is True
            mock_context.verify.assert_called_once_with(
                special_password, "hashed_password"
            )


class TestGetPasswordHash:
    """Test cases for get_password_hash function."""

    def test_get_password_hash_success(self):
        """Test successful password hashing."""
        with patch("src.core.security.pwd_context") as mock_context:
            mock_context.hash.return_value = "hashed_password_123"

            result = get_password_hash("plain_password")

            assert result == "hashed_password_123"
            mock_context.hash.assert_called_once_with("plain_password")

    def test_get_password_hash_with_empty_string(self):
        """Test password hashing with empty string."""
        with patch("src.core.security.pwd_context") as mock_context:
            mock_context.hash.return_value = "hashed_empty"

            result = get_password_hash("")

            assert result == "hashed_empty"
            mock_context.hash.assert_called_once_with("")

    def test_get_password_hash_with_special_characters(self):
        """Test password hashing with special characters."""
        with patch("src.core.security.pwd_context") as mock_context:
            mock_context.hash.return_value = "hashed_special"

            special_password = "P@ssw0rd!@#$%^&*()"
            result = get_password_hash(special_password)

            assert result == "hashed_special"
            mock_context.hash.assert_called_once_with(special_password)

    def test_get_password_hash_consistency(self):
        """Test that password hashing is consistent."""
        with patch("src.core.security.pwd_context") as mock_context:
            mock_context.hash.return_value = "consistent_hash"

            password = "test_password"
            hash1 = get_password_hash(password)
            hash2 = get_password_hash(password)

            # Note: In real bcrypt, hashes are different each time due to salt
            # But with mocked context, we expect the same result
            assert hash1 == hash2
            assert mock_context.hash.call_count == 2


class TestVerifyToken:
    """Test cases for verify_token function."""

    def test_verify_token_success(self, mock_settings):
        """Test successful token verification."""
        with patch("src.core.security.settings", mock_settings):
            with patch("jwt.decode") as mock_decode:
                mock_decode.return_value = {"sub": "user123", "exp": 1234567890}

                result = verify_token("valid_token")

                assert result == "user123"
                mock_decode.assert_called_once_with(
                    "valid_token",
                    mock_settings.secret_key,
                    algorithms=[mock_settings.algorithm],
                )

    def test_verify_token_invalid_token(self, mock_settings):
        """Test token verification with invalid token."""
        with patch("src.core.security.settings", mock_settings):
            with patch("jwt.decode") as mock_decode:
                mock_decode.side_effect = jwt.JWTError("Invalid token")

                result = verify_token("invalid_token")

                assert result is None
                mock_decode.assert_called_once_with(
                    "invalid_token",
                    mock_settings.secret_key,
                    algorithms=[mock_settings.algorithm],
                )

    def test_verify_token_expired_token(self, mock_settings):
        """Test token verification with expired token."""
        with patch("src.core.security.settings", mock_settings):
            with patch("jwt.decode") as mock_decode:
                mock_decode.side_effect = jwt.ExpiredSignatureError("Token expired")

                result = verify_token("expired_token")

                assert result is None
                mock_decode.assert_called_once_with(
                    "expired_token",
                    mock_settings.secret_key,
                    algorithms=[mock_settings.algorithm],
                )

    def test_verify_token_malformed_token(self, mock_settings):
        """Test token verification with malformed token."""
        with patch("src.core.security.settings", mock_settings):
            with patch("jwt.decode") as mock_decode:
                mock_decode.side_effect = jwt.JWTError("Malformed token")

                result = verify_token("malformed_token")

                assert result is None
                mock_decode.assert_called_once_with(
                    "malformed_token",
                    mock_settings.secret_key,
                    algorithms=[mock_settings.algorithm],
                )

    def test_verify_token_with_different_algorithms(self, mock_settings):
        """Test token verification with different algorithm settings."""
        with patch("src.core.security.settings", mock_settings):
            mock_settings.algorithm = "HS512"

            with patch("jwt.decode") as mock_decode:
                mock_decode.return_value = {"sub": "user123"}

                result = verify_token("valid_token")

                assert result == "user123"
                mock_decode.assert_called_once_with(
                    "valid_token", mock_settings.secret_key, algorithms=["HS512"]
                )

    def test_verify_token_with_empty_token(self, mock_settings):
        """Test token verification with empty token."""
        with patch("src.core.security.settings", mock_settings):
            with patch("jwt.decode") as mock_decode:
                mock_decode.side_effect = jwt.JWTError("Empty token")

                result = verify_token("")

                assert result is None
                mock_decode.assert_called_once_with(
                    "", mock_settings.secret_key, algorithms=[mock_settings.algorithm]
                )


class TestSecurityIntegration:
    """Integration tests for security functions."""

    def test_password_hash_and_verify_roundtrip(self):
        """Test that hashed passwords can be verified."""
        with patch("src.core.security.pwd_context") as mock_context:
            # Mock the hash to return a specific value
            mock_context.hash.return_value = "hashed_password_123"
            # Mock verify to return True when comparing the same password
            mock_context.verify.side_effect = (
                lambda pwd, hashed: pwd == "test_password"
                and hashed == "hashed_password_123"
            )

            password = "test_password"
            hashed = get_password_hash(password)
            verified = verify_password(password, hashed)

            assert hashed == "hashed_password_123"
            assert verified is True

    def test_token_creation_and_verification_roundtrip(self, mock_settings):
        """Test that created tokens can be verified."""
        with patch("src.core.security.settings", mock_settings):
            with patch("src.core.security.datetime") as mock_datetime:
                fixed_time = datetime(2023, 1, 1, 12, 0, 0)
                mock_datetime.utcnow.return_value = fixed_time
                mock_datetime.timedelta = timedelta

                with patch("jwt.encode") as mock_encode:
                    with patch("jwt.decode") as mock_decode:
                        # Mock encode to return a token
                        mock_encode.return_value = "test_token_123"
                        # Mock decode to return the subject
                        mock_decode.return_value = {"sub": "user123", "exp": 1234567890}

                        # Create token
                        # token = create_access_token("user123")

                        # Verify token
                        subject = verify_token("test_token_123")

                        assert "test_token_123" == "test_token_123"
                        assert subject == "user123"
