"""
Category schemas for request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    """Base category schema."""

    name: str = Field(..., min_length=1, description="Category name cannot be empty")
    description: Optional[str] = None
    color: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Category creation schema."""

    pass


class CategoryUpdate(BaseModel):
    """Category update schema."""

    name: Optional[str] = Field(None, min_length=1, description="Category name cannot be empty")
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


class Category(CategoryInDB):
    """Category response schema."""

    pass


class CategoryList(BaseModel):
    """Category list response schema."""

    categories: list[Category]
    total: int
    page: int
    per_page: int

    class Config:
        from_attributes = True
