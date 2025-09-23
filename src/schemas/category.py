"""
Category schemas for request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CategoryBase(BaseModel):
    """Base category schema."""

    name: str
    description: Optional[str] = None
    color: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Category creation schema."""

    pass


class CategoryUpdate(BaseModel):
    """Category update schema."""

    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None


class CategoryInDB(CategoryBase):
    """Category in database schema."""

    id: int
    is_system: bool
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Category(CategoryBase):
    """Category response schema."""

    id: int
    is_system: bool
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
