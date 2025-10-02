"""
Security utilities for password hashing and JWT token management.
"""

from datetime import datetime, timedelta
from typing import Any, Union

import bcrypt
from jose import jwt

from src.core.config import settings


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """Create JWT access token."""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        if plain_password is None or hashed_password is None:
            return False

        # Ensure password is string and truncate if too long
        plain_password = str(plain_password)
        if len(plain_password) > 72:
            plain_password = plain_password[:72]

        # Use bcrypt directly for verification
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    try:
        if password is None:
            raise ValueError("Password cannot be None")

        # Ensure password is string and truncate if too long
        password = str(password)
        if len(password) > 72:
            password = password[:72]

        # Use bcrypt directly for hashing
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
    except Exception as e:
        print(f"Password hashing error: {e}")
        raise


def verify_token(token: str) -> Union[str, None]:
    """Verify JWT token and return subject."""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload.get("sub")
    except jwt.JWTError:
        return None
