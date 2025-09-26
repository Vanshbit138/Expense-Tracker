"""
Expense service for business logic operations.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.expense import Expense
from src.repositories.category_repository import CategoryRepository
from src.repositories.expense_repository import ExpenseRepository
from src.schemas.expense import (
    CategoryStatsQuery,
    ExpenseCreate,
    ExpenseFilter,
    ExpenseQuery,
    ExpenseStatsQuery,
    ExpenseUpdate,
    MonthlyAnalyticsQuery,
    MonthlyExpenseQuery,
)


class ExpenseService:
    """Expense service for business logic operations following SOLID principles."""

    def __init__(self, db: Session):
        self.db = db
        self.expense_repo = ExpenseRepository(db)
        self.category_repo = CategoryRepository(db)

    def create_expense(self, user_id: int, expense_data: ExpenseCreate) -> Expense:
        """Create a new expense."""
        # Validate category access
        self._validate_category_access(expense_data.category_id, user_id)

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

    def get_expense_by_id(self, data: ExpenseQuery) -> Optional[Expense]:
        """Get expense by ID for a specific user."""
        return self.expense_repo.get_by_id(data.expense_id, data.user_id)

    def get_user_expenses(self, data: ExpenseFilter) -> List[Expense]:
        """Get user expenses with optional filters."""
        return self.expense_repo.get_user_expenses(
            data.user_id,
            data.skip,
            data.limit,
            data.category_id,
            data.status,
            data.start_date,
            data.end_date,
        )

    def get_monthly_expenses(self, data: MonthlyExpenseQuery) -> List[Expense]:
        """Get expenses for a specific month."""
        return self.expense_repo.get_monthly_expenses(
            data.user_id, data.year, data.month
        )

    def update_expense(
        self, expense_id: int, user_id: int, expense_data: ExpenseUpdate
    ) -> Optional[Expense]:
        """Update expense."""
        expense = self.expense_repo.get_by_id(expense_id, user_id)
        if not expense:
            return None

        # Validate category if being updated
        if expense_data.category_id and expense_data.category_id != expense.category_id:
            self._validate_category_access(expense_data.category_id, user_id)

        # Update expense fields
        update_data = expense_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(expense, field, value)

        return self.expense_repo.update(expense)

    def delete_expense(self, data: ExpenseQuery) -> bool:
        """Delete expense."""
        return self.expense_repo.delete(data.expense_id, data.user_id)

    def get_expense_stats(self, data: ExpenseStatsQuery) -> Dict[str, Any]:
        """Get expense statistics for a user."""
        return self.expense_repo.get_expense_stats(
            data.user_id, data.start_date, data.end_date, data.currency
        )

    def get_category_stats(self, data: CategoryStatsQuery) -> List[Dict[str, Any]]:
        """Get expense statistics by category."""
        return self.expense_repo.get_category_stats(
            data.user_id, data.start_date, data.end_date, data.limit
        )

    def get_monthly_analytics(self, data: MonthlyAnalyticsQuery) -> Dict[str, Any]:
        """Get monthly analytics for a user."""
        expenses = self.get_monthly_expenses(data)

        if not expenses:
            return self._get_empty_analytics()

        return self._calculate_analytics(expenses, data.user_id)

    def _validate_category_access(self, category_id: int, user_id: int) -> None:
        """Validate user has access to category."""
        category = self.category_repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

        if not (category.is_system or category.user_id == user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this category",
            )

    def _get_empty_analytics(self) -> Dict[str, Any]:
        """Return empty analytics structure."""
        return {
            "total_amount": Decimal("0"),
            "total_count": 0,
            "average_amount": Decimal("0"),
            "currency": "USD",
            "top_categories": [],
            "recurring_count": 0,
        }

    def _calculate_analytics(
        self, expenses: List[Expense], user_id: int
    ) -> Dict[str, Any]:
        """Calculate analytics from expenses."""
        total_amount = sum(expense.amount for expense in expenses)
        total_count = len(expenses)
        average_amount = total_amount / total_count if total_count > 0 else Decimal("0")
        currency = expenses[0].currency if expenses else "USD"

        category_stats = self.get_category_stats(
            CategoryStatsQuery(user_id=user_id, limit=5)
        )

        recurring_count = sum(1 for expense in expenses if expense.is_recurring)

        return {
            "total_amount": total_amount,
            "total_count": total_count,
            "average_amount": average_amount,
            "currency": currency,
            "top_categories": category_stats,
            "recurring_count": recurring_count,
        }
