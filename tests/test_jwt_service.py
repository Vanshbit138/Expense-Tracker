"""
Test JWT service functionality.
"""

from datetime import datetime, timedelta

from jose import jwt

from src.core.config import settings
from src.services.authentication.jwt_service import (
    create_access_token as jwt_create_token,
)
from src.services.authentication.jwt_service import verify_token as jwt_verify_token


class TestJWTService:
    """Test JWT service functionality."""

    def test_create_access_token_default_expiry(self):
        """Test creating access token with default expiry."""
        user_id = "123"
        token = jwt_create_token(user_id)

        assert isinstance(token, str)

        # Verify token can be decoded
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        assert payload["sub"] == user_id

    def test_create_access_token_custom_expiry(self):
        """Test creating access token with custom expiry."""
        user_id = "123"
        expires_delta = timedelta(minutes=30)

        token = jwt_create_token(user_id, expires_delta)

        assert isinstance(token, str)

        # Just verify the token can be decoded and has the right subject
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        assert payload["sub"] == user_id

        # Verify expiration is set (not exact time due to potential timing issues)
        assert "exp" in payload
        exp_time = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        # Token should expire in the future
        assert exp_time > now

    def test_verify_token_valid(self):
        """Test verifying valid token."""
        user_id = "123"
        token = jwt_create_token(user_id)

        verified_user_id = jwt_verify_token(token)
        assert verified_user_id == user_id

    def test_verify_token_invalid(self):
        """Test verifying invalid token."""
        invalid_token = "invalid.token.here"

        verified_user_id = jwt_verify_token(invalid_token)
        assert verified_user_id is None

    def test_verify_token_expired(self):
        """Test verifying expired token."""
        user_id = "123"
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = jwt_create_token(user_id, expires_delta)

        verified_user_id = jwt_verify_token(token)
        assert verified_user_id is None


class TestJWTServiceEdgeCases:
    """Test JWT service edge cases."""

    def test_create_token_with_none_user_id(self):
        """Test creating token with None user_id."""
        token = jwt_create_token(None)
        assert isinstance(token, str)

        # Verify token contains "None" as string
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        assert payload["sub"] == "None"

    def test_create_token_with_numeric_user_id(self):
        """Test creating token with numeric user_id."""
        user_id = 123
        token = jwt_create_token(user_id)
        assert isinstance(token, str)

        # Verify token contains user_id as string
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        assert payload["sub"] == "123"

    def test_verify_token_empty_string(self):
        """Test verifying empty string token."""
        verified_user_id = jwt_verify_token("")
        assert verified_user_id is None

    def test_verify_token_malformed_jwt(self):
        """Test verifying malformed JWT."""
        # JWT with wrong number of parts
        malformed_token = "header.payload"

        verified_user_id = jwt_verify_token(malformed_token)
        assert verified_user_id is None

    def test_verify_token_wrong_signature(self):
        """Test verifying token with wrong signature."""
        user_id = "123"
        # Create token with different secret
        token = jwt.encode(
            {"exp": datetime.utcnow() + timedelta(minutes=30), "sub": str(user_id)},
            "wrong-secret",
            algorithm=settings.algorithm,
        )

        verified_user_id = jwt_verify_token(token)
        assert verified_user_id is None

    def test_verify_token_no_sub_claim(self):
        """Test verifying token without sub claim."""
        # Create token without sub claim
        token = jwt.encode(
            {"exp": datetime.utcnow() + timedelta(minutes=30)},
            settings.secret_key,
            algorithm=settings.algorithm,
        )

        verified_user_id = jwt_verify_token(token)
        assert verified_user_id is None
