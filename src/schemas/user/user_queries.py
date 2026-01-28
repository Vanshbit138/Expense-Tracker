"""
User query schemas for parameter validation.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr


class UserQuery(BaseModel):
    """Query parameters for user operations."""

    user_id: int


class UserFilter(BaseModel):
    """Filter parameters for user queries."""

    skip: int = 0
    limit: int = 100


class UserValidation(BaseModel):
    """User validation parameters."""

    email: Optional[EmailStr] = None
    username: Optional[str] = None
    exclude_user_id: Optional[int] = None


class AuthenticationQuery(BaseModel):
    """Authentication query parameters."""

    email: EmailStr
    password: str


class PasswordChangeQuery(BaseModel):
    """Password change query parameters."""

    user_id: int
    current_password: str
    new_password: str
