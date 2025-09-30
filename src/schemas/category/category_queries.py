"""
Category query schemas for parameter validation.
"""

from typing import Optional

from pydantic import BaseModel


class CategoryQuery(BaseModel):
    """Query parameters for category operations."""

    category_id: int
    user_id: int


class CategoryFilter(BaseModel):
    """Filter parameters for category queries."""

    user_id: int
    skip: int = 0
    limit: int = 100


class CategoryValidation(BaseModel):
    """Category validation parameters."""

    name: str
    user_id: int
    exclude_category_id: Optional[int] = None
