"""
Expense query schemas for filtering and pagination.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, field_validator


class ExpenseFilter(BaseModel):
    """Expense filter schema."""

    skip: int = 0
    limit: int = 20
    category_id: Optional[int] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    user_id: Optional[int] = None

    @field_validator("skip")
    @classmethod
    def validate_skip(cls, v):
        if v < 0:
            raise ValueError("Skip must be non-negative")
        return v

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v):
        if v <= 0 or v > 100:
            raise ValueError("Limit must be between 1 and 100")
        return v


class ExpenseQuery(BaseModel):
    """Expense query schema."""

    expense_id: int
    user_id: int

    @field_validator("expense_id")
    @classmethod
    def validate_expense_id(cls, v):
        if v <= 0:
            raise ValueError("Expense ID must be positive")
        return v

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v):
        if v <= 0:
            raise ValueError("User ID must be positive")
        return v


class MonthlyExpenseQuery(BaseModel):
    """Monthly expense query schema."""

    user_id: int
    year: int
    month: int

    @field_validator("year")
    @classmethod
    def validate_year(cls, v):
        if v < 2000 or v > 2100:
            raise ValueError("Year must be between 2000 and 2100")
        return v

    @field_validator("month")
    @classmethod
    def validate_month(cls, v):
        if v < 1 or v > 12:
            raise ValueError("Month must be between 1 and 12")
        return v


class ExpenseStatsQuery(BaseModel):
    """Expense statistics query schema."""

    user_id: int

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v):
        if v <= 0:
            raise ValueError("User ID must be positive")
        return v


class CategoryStatsQuery(BaseModel):
    """Category statistics query schema."""

    user_id: int

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v):
        if v <= 0:
            raise ValueError("User ID must be positive")
        return v


class MonthlyAnalyticsQuery(BaseModel):
    """Monthly analytics query schema."""

    user_id: int
    year: int
    month: int

    @field_validator("year")
    @classmethod
    def validate_year(cls, v):
        if v < 2000 or v > 2100:
            raise ValueError("Year must be between 2000 and 2100")
        return v

    @field_validator("month")
    @classmethod
    def validate_month(cls, v):
        if v < 1 or v > 12:
            raise ValueError("Month must be between 1 and 12")
        return v
