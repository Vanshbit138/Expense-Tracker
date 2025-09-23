"""
Authentication schemas for request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """JWT token response schema."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema."""

    user_id: Optional[int] = None


class UserLogin(BaseModel):
    """User login request schema."""

    email: EmailStr
    password: str


class UserRegister(BaseModel):
    """User registration request schema."""

    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema."""

    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Password change request schema."""

    current_password: str
    new_password: str
