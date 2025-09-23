"""
Expense service for business logic operations.
"""

from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.expense import Expense
from src.repositories.category_repository import CategoryRepository
from src.repositories.expense_repository import ExpenseRepository
from src.schemas.expense import ExpenseCreate, ExpenseUpdate


class ExpenseService:
    """Expense service for business logic operations."""

    def __init__(self, db: Session):
        self.db = db
        self.expense_repo = ExpenseRepository(db)
        self.category_repo = CategoryRepository(db)

    def create_expense(self, user_id: int, expense_data: ExpenseCreate) -> Expense:
        """Create a new expense."""
        # Verify category exists and user has access to it
        category = self.category_repo.get_by_id(expense_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        # Check if user has access to this category
        if not (category.is_system or category.user_id == user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this category",
            )

        # Create expense
        expense = Expense(
            amount=expense_data.amount,
            currency=expense_data.currency,
            description=expense_data.description,
            status=expense_data.status,
            is_recurring=expense_data.is_recurring,
            recurring_frequency=expense_data.recurring_frequency,
            expense_date=expense_data.expense_date,
            user_id=user_id,
            category_id=expense_data.category_id,
        )

        return self.expense_repo.create(expense)

    def get_expense_by_id(self, expense_id: int, user_id: int) -> Optional[Expense]:
        """Get expense by ID for a specific user."""
        return self.expense_repo.get_by_id(expense_id, user_id)

    def get_user_expenses(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Expense]:
        """Get user expenses with optional filters."""
        return self.expense_repo.get_user_expenses(
            user_id, skip, limit, category_id, status, start_date, end_date
        )

    def get_monthly_expenses(
        self, user_id: int, year: int, month: int
    ) -> List[Expense]:
        """Get expenses for a specific month."""
        return self.expense_repo.get_monthly_expenses(user_id, year, month)

    def update_expense(
        self, expense_id: int, user_id: int, expense_data: ExpenseUpdate
    ) -> Optional[Expense]:
        """Update expense."""
        expense = self.expense_repo.get_by_id(expense_id, user_id)
        if not expense:
            return None

        # Verify category if category_id is being updated
        if expense_data.category_id and expense_data.category_id != expense.category_id:
            category = self.category_repo.get_by_id(expense_data.category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
                )

            # Check if user has access to this category
            if not (category.is_system or category.user_id == user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this category",
                )

        # Update expense fields
        update_data = expense_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(expense, field, value)

        return self.expense_repo.update(expense)

    def delete_expense(self, expense_id: int, user_id: int) -> bool:
        """Delete expense."""
        return self.expense_repo.delete(expense_id, user_id)

    def get_expense_stats(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        currency: str = "USD",
    ) -> Dict[str, Any]:
        """Get expense statistics for a user."""
        return self.expense_repo.get_expense_stats(
            user_id, start_date, end_date, currency
        )

    def get_category_stats(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get expense statistics by category."""
        return self.expense_repo.get_category_stats(
            user_id, start_date, end_date, limit
        )

    def get_monthly_analytics(
        self, user_id: int, year: int, month: int
    ) -> Dict[str, Any]:
        """Get monthly analytics for a user."""
        expenses = self.get_monthly_expenses(user_id, year, month)

        if not expenses:
            return {
                "total_amount": Decimal("0"),
                "total_count": 0,
                "average_amount": Decimal("0"),
                "currency": "USD",
                "top_categories": [],
                "recurring_count": 0,
            }

        # Calculate basic stats
        total_amount = sum(expense.amount for expense in expenses)
        total_count = len(expenses)
        average_amount = total_amount / total_count if total_count > 0 else Decimal("0")

        # Get currency (assuming all expenses have the same currency)
        currency = expenses[0].currency if expenses else "USD"

        # Get top categories
        category_stats = self.get_category_stats(user_id, limit=5)

        # Count recurring expenses
        recurring_count = sum(1 for expense in expenses if expense.is_recurring)

        return {
            "total_amount": total_amount,
            "total_count": total_count,
            "average_amount": average_amount,
            "currency": currency,
            "top_categories": category_stats,
            "recurring_count": recurring_count,
        }
