"""
Expense query schemas for filtering and validation.
"""

from typing import Optional

from pydantic import BaseModel


class ExpenseQuery(BaseModel):
    """Expense query schema for single expense operations."""

    expense_id: int
    user_id: int


class ExpenseFilter(BaseModel):
    """Expense filter schema for listing expenses."""

    user_id: int
    skip: int = 0
    limit: int = 100
    category_id: Optional[int] = None
    status: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
