"""
Expense schemas for request/response validation.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, field_validator


class ExpenseBase(BaseModel):
    """Base expense schema."""

    amount: Decimal
    currency: str = "USD"
    description: str
    category_id: int
    expense_date: date
    status: Literal["pending", "approved", "rejected"] = "pending"
    is_recurring: bool = False
    recurring_frequency: Optional[Literal["daily", "weekly", "monthly", "yearly"]] = (
        None
    )

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        if v > Decimal("999999.99"):
            raise ValueError("Amount must be less than 1,000,000")
        return v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v):
        valid_currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"]
        if v not in valid_currencies:
            raise ValueError(f'Currency must be one of: {", ".join(valid_currencies)}')
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if not v or len(v.strip()) < 1:
            raise ValueError("Description cannot be empty")
        if len(v.strip()) > 500:
            raise ValueError("Description must be 500 characters or less")
        return v.strip()

    @field_validator("category_id")
    @classmethod
    def validate_category_id(cls, v):
        if v <= 0:
            raise ValueError("Category ID must be a positive integer")
        return v


class ExpenseCreate(ExpenseBase):
    """Expense creation schema."""

    pass


class ExpenseUpdate(BaseModel):
    """Expense update schema."""

    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    expense_date: Optional[date] = None
    status: Optional[Literal["pending", "approved", "rejected"]] = None
    is_recurring: Optional[bool] = None
    recurring_frequency: Optional[Literal["daily", "weekly", "monthly", "yearly"]] = (
        None
    )

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError("Amount must be greater than 0")
            if v > Decimal("999999.99"):
                raise ValueError("Amount must be less than 1,000,000")
        return v

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v):
        if v is not None:
            valid_currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"]
            if v not in valid_currencies:
                raise ValueError(
                    f'Currency must be one of: {", ".join(valid_currencies)}'
                )
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v):
        if v is not None:
            if not v or len(v.strip()) < 1:
                raise ValueError("Description cannot be empty")
            if len(v.strip()) > 500:
                raise ValueError("Description must be 500 characters or less")
            return v.strip()
        return v

    @field_validator("category_id")
    @classmethod
    def validate_category_id(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Category ID must be a positive integer")
        return v


class ExpenseInDB(ExpenseBase):
    """Expense in database schema."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Expense(ExpenseBase):
    """Expense response schema."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Analytics schemas
class ExpenseStatsQuery(BaseModel):
    """Expense statistics query schema."""

    user_id: int


class CategoryStatsQuery(BaseModel):
    """Category statistics query schema."""

    user_id: int


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


# Import query schemas
