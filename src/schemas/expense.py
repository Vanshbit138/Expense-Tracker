"""
Expense schemas for request/response validation.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ExpenseBase(BaseModel):
    """Base expense schema."""

    amount: Decimal
    currency: str = "USD"
    description: Optional[str] = None
    status: str = "pending"
    is_recurring: bool = False
    recurring_frequency: Optional[str] = None
    expense_date: datetime
    category_id: int


class ExpenseCreate(ExpenseBase):
    """Expense creation schema."""

    pass


class ExpenseUpdate(BaseModel):
    """Expense update schema."""

    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurring_frequency: Optional[str] = None
    expense_date: Optional[datetime] = None
    category_id: Optional[int] = None


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


class ExpenseWithCategory(Expense):
    """Expense response schema with category details."""

    category: Optional[dict] = None


class ExpenseStats(BaseModel):
    """Expense statistics schema."""

    total_amount: Decimal
    total_count: int
    average_amount: Decimal
    currency: str
