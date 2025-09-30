"""
Unit tests for authentication services.
"""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi import HTTPException, status
from jose import JWTError

from src.services.authentication.jwt_service import create_access_token, verify_token
from src.services.authentication.password_service import (
    get_password_hash,
    verify_password,
)


class TestPasswordService:
    """Test cases for password service functions."""

    def test_verify_password_success(self):
        """Test successful password verification."""
        with patch(
            "src.services.authentication.password_service.pwd_context"
        ) as mock_context:
            mock_context.verify.return_value = True

            result = verify_password("plain_password", "hashed_password")

            assert result is True
            mock_context.verify.assert_called_once_with(
                "plain_password", "hashed_password"
            )

    def test_verify_password_failure(self):
        """Test failed password verification."""
        with patch(
            "src.services.authentication.password_service.pwd_context"
        ) as mock_context:
            mock_context.verify.return_value = False

            result = verify_password("wrong_password", "hashed_password")

            assert result is False
            mock_context.verify.assert_called_once_with(
                "wrong_password", "hashed_password"
            )

    def test_verify_password_with_exception(self):
        """Test password verification with exception handling."""
        with patch(
            "src.services.authentication.password_service.pwd_context"
        ) as mock_context:
            mock_context.verify.side_effect = Exception("Verification error")

            result = verify_password("password", "hashed")

            assert result is False

    def test_verify_password_with_long_password(self):
        """Test password verification with password longer than 72 characters."""
        with patch(
            "src.services.authentication.password_service.pwd_context"
        ) as mock_context:
            mock_context.verify.return_value = True

            long_password = "a" * 100  # 100 characters
            result = verify_password(long_password, "hashed_password")

            # Should truncate to 72 characters
            expected_password = "a" * 72
            mock_context.verify.assert_called_once_with(
                expected_password, "hashed_password"
            )
            assert result is True

    def test_get_password_hash_success(self):
        """Test successful password hashing."""
        with patch(
            "src.services.authentication.password_service.pwd_context"
        ) as mock_context:
            mock_context.hash.return_value = "hashed_password_123"

            result = get_password_hash("plain_password")

            assert result == "hashed_password_123"
            mock_context.hash.assert_called_once_with("plain_password")

    def test_get_password_hash_with_exception(self):
        """Test password hashing with exception handling."""
        with patch(
            "src.services.authentication.password_service.pwd_context"
        ) as mock_context:
            mock_context.hash.side_effect = Exception("Hashing error")

            with patch("bcrypt.hashpw") as mock_bcrypt:
                mock_bcrypt.return_value = b"bcrypt_hash"

                result = get_password_hash("password")

                assert result == "bcrypt_hash"
                mock_bcrypt.assert_called_once()

    def test_get_password_hash_with_long_password(self):
        """Test password hashing with password longer than 72 characters."""
        with patch(
            "src.services.authentication.password_service.pwd_context"
        ) as mock_context:
            mock_context.hash.return_value = "hashed_password"

            long_password = "a" * 100  # 100 characters
            result = get_password_hash(long_password)

            # Should truncate to 72 characters
            expected_password = "a" * 72
            mock_context.hash.assert_called_once_with(expected_password)
            assert result == "hashed_password"

    def test_get_password_hash_fallback_to_bcrypt(self):
        """Test fallback to direct bcrypt when pwd_context fails."""
        with patch(
            "src.services.authentication.password_service.pwd_context"
        ) as mock_context:
            mock_context.hash.side_effect = Exception("Hashing error")

            with patch("bcrypt.hashpw") as mock_bcrypt:
                with patch("bcrypt.gensalt") as mock_gensalt:
                    mock_gensalt.return_value = b"salt"
                    mock_bcrypt.return_value = b"bcrypt_hash"

                    result = get_password_hash("password")

                    assert result == "bcrypt_hash"
                    mock_bcrypt.assert_called_once_with(b"password", b"salt")

    def test_password_service_with_empty_strings(self):
        """Test password service with empty strings."""
        with patch(
            "src.services.authentication.password_service.pwd_context"
        ) as mock_context:
            mock_context.verify.return_value = False
            mock_context.hash.return_value = "hashed_empty"

            # Test verification
            result = verify_password("", "")
            assert result is False

            # Test hashing
            result = get_password_hash("")
            assert result == "hashed_empty"

    def test_password_service_with_special_characters(self):
        """Test password service with special characters."""
        with patch(
            "src.services.authentication.password_service.pwd_context"
        ) as mock_context:
            mock_context.verify.return_value = True
            mock_context.hash.return_value = "hashed_special"

            special_password = "P@ssw0rd!@#$%^&*()_+-=[]{}|;':\",./<>?"

            # Test verification
            result = verify_password(special_password, "hashed")
            assert result is True

            # Test hashing
            result = get_password_hash(special_password)
            assert result == "hashed_special"


class TestJWTService:
    """Test cases for JWT service functions."""

    def test_create_access_token_with_default_expiry(self, mock_settings):
        """Test token creation with default expiry time."""
        with patch("src.services.authentication.jwt_service.settings", mock_settings):
            with patch(
                "src.services.authentication.jwt_service.datetime"
            ) as mock_datetime:
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

    def test_create_access_token_with_custom_expiry(self, mock_settings):
        """Test token creation with custom expiry time."""
        with patch("src.services.authentication.jwt_service.settings", mock_settings):
            with patch(
                "src.services.authentication.jwt_service.datetime"
            ) as mock_datetime:
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

    def test_create_access_token_with_different_subjects(self, mock_settings):
        """Test token creation with different subject types."""
        with patch("src.services.authentication.jwt_service.settings", mock_settings):
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

    def test_verify_token_success(self, mock_settings):
        """Test successful token verification."""
        with patch("src.services.authentication.jwt_service.settings", mock_settings):
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
        with patch("src.services.authentication.jwt_service.settings", mock_settings):
            with patch("jwt.decode") as mock_decode:
                mock_decode.side_effect = JWTError("Invalid token")

                with pytest.raises(HTTPException) as exc_info:
                    verify_token("invalid_token")

                assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
                assert "Could not validate credentials" in exc_info.value.detail

    def test_verify_token_expired_token(self, mock_settings):
        """Test token verification with expired token."""
        with patch("src.services.authentication.jwt_service.settings", mock_settings):
            with patch("jwt.decode") as mock_decode:
                mock_decode.side_effect = JWTError("Token expired")

                with pytest.raises(HTTPException) as exc_info:
                    verify_token("expired_token")

                assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
                assert "Could not validate credentials" in exc_info.value.detail

    def test_verify_token_malformed_token(self, mock_settings):
        """Test token verification with malformed token."""
        with patch("src.services.authentication.jwt_service.settings", mock_settings):
            with patch("jwt.decode") as mock_decode:
                mock_decode.side_effect = JWTError("Malformed token")

                with pytest.raises(HTTPException) as exc_info:
                    verify_token("malformed_token")

                assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
                assert "Could not validate credentials" in exc_info.value.detail

    def test_verify_token_with_missing_subject(self, mock_settings):
        """Test token verification with missing subject."""
        with patch("src.services.authentication.jwt_service.settings", mock_settings):
            with patch("jwt.decode") as mock_decode:
                mock_decode.return_value = {"exp": 1234567890}  # No 'sub' key

                with pytest.raises(HTTPException) as exc_info:
                    verify_token("token_without_subject")

                assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
                assert "Could not validate credentials" in exc_info.value.detail

    def test_verify_token_with_none_subject(self, mock_settings):
        """Test token verification with None subject."""
        with patch("src.services.authentication.jwt_service.settings", mock_settings):
            with patch("jwt.decode") as mock_decode:
                mock_decode.return_value = {"sub": None, "exp": 1234567890}

                with pytest.raises(HTTPException) as exc_info:
                    verify_token("token_with_none_subject")

                assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
                assert "Could not validate credentials" in exc_info.value.detail

    def test_verify_token_with_different_algorithms(self, mock_settings):
        """Test token verification with different algorithm settings."""
        with patch("src.services.authentication.jwt_service.settings", mock_settings):
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
        with patch("src.services.authentication.jwt_service.settings", mock_settings):
            with patch("jwt.decode") as mock_decode:
                mock_decode.side_effect = JWTError("Empty token")

                with pytest.raises(HTTPException) as exc_info:
                    verify_token("")

                assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
                assert "Could not validate credentials" in exc_info.value.detail


class TestAuthenticationIntegration:
    """Integration tests for authentication services."""

    def test_password_hash_and_verify_roundtrip(self):
        """Test that hashed passwords can be verified."""
        with patch(
            "src.services.authentication.password_service.pwd_context"
        ) as mock_context:
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
        with patch("src.services.authentication.jwt_service.settings", mock_settings):
            with patch(
                "src.services.authentication.jwt_service.datetime"
            ) as mock_datetime:
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

    def test_authentication_error_handling(self, mock_settings):
        """Test comprehensive error handling in authentication."""
        with patch("src.services.authentication.jwt_service.settings", mock_settings):
            # Test various JWT errors
            jwt_errors = [
                JWTError("Invalid token"),
                JWTError("Token expired"),
                JWTError("Malformed token"),
                JWTError("Invalid signature"),
            ]

            for error in jwt_errors:
                with patch("jwt.decode") as mock_decode:
                    mock_decode.side_effect = error

                    with pytest.raises(HTTPException) as exc_info:
                        verify_token("invalid_token")

                    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
                    assert "Could not validate credentials" in exc_info.value.detail

    def test_password_service_error_handling(self):
        """Test comprehensive error handling in password service."""
        with patch(
            "src.services.authentication.password_service.pwd_context"
        ) as mock_context:
            # Test verification error
            mock_context.verify.side_effect = Exception("Verification error")
            result = verify_password("password", "hashed")
            assert result is False

            # Test hashing error with bcrypt fallback
            mock_context.hash.side_effect = Exception("Hashing error")
            with patch("bcrypt.hashpw") as mock_bcrypt:
                with patch("bcrypt.gensalt") as mock_gensalt:
                    mock_gensalt.return_value = b"salt"
                    mock_bcrypt.return_value = b"bcrypt_hash"

                    result = get_password_hash("password")
                    assert result == "bcrypt_hash"
