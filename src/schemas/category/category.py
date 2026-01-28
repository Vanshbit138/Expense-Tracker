"""
Category schemas for request/response validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class CategoryBase(BaseModel):
    """Base category schema."""

    name: str
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError("Category name cannot be empty")
        if len(v.strip()) > 100:
            raise ValueError("Category name must be 100 characters or less")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if v is not None and len(v.strip()) > 500:
            raise ValueError("Description must be 500 characters or less")
        return v.strip() if v else v


class CategoryCreate(CategoryBase):
    """Category creation schema."""

    pass


class CategoryUpdate(CategoryBase):
    """Category update schema."""

    name: Optional[str] = None
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            if not v or len(v.strip()) < 1:
                raise ValueError("Category name cannot be empty")
            if len(v.strip()) > 100:
                raise ValueError("Category name must be 100 characters or less")
            return v.strip()
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if v is not None and len(v.strip()) > 500:
            raise ValueError("Description must be 500 characters or less")
        return v.strip() if v else v


class CategoryInDB(CategoryBase):
    """Category in database schema."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Category(CategoryBase):
    """Category response schema."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
