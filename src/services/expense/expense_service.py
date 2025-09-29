"""
Expense service for business logic operations.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from src.core.logging_config import get_logger
from src.models.expense import Expense
from src.repositories.expense_repository import ExpenseRepository
from src.schemas.expense import ExpenseCreate, ExpenseUpdate
from src.schemas.expense_queries import ExpenseFilter, ExpenseQuery

# Initialize logger
logger = get_logger(__name__)


class ExpenseService:
    """Expense service for business logic operations following SOLID principles."""

    def __init__(self, db: Session):
        self.db = db
        self.expense_repo = ExpenseRepository(db)
        self.logger = get_logger(self.__class__.__name__)

    def create_expense(self, expense_data: ExpenseCreate, user_id: int) -> Expense:
        """Create a new expense."""
        self.logger.info(
            "Creating new expense",
            amount=expense_data.amount,
            user_id=user_id,
            category_id=expense_data.category_id,
        )

        try:
            expense = self.expense_repo.create_expense(expense_data, user_id)
            self.logger.info(
                "Expense created successfully",
                expense_id=expense.id,
                amount=expense.amount,
            )
            return expense
        except Exception as e:
            self.logger.error(
                "Failed to create expense",
                user_id=user_id,
                category_id=expense_data.category_id,
                error=str(e),
                exc_info=True,
            )
            raise

    def get_expense_by_id(self, expense_query: ExpenseQuery) -> Optional[Expense]:
        """Get expense by ID."""
        self.logger.debug(
            "Fetching expense by ID",
            expense_id=expense_query.expense_id,
            user_id=expense_query.user_id,
        )
        expense = self.expense_repo.get_expense_by_id(
            expense_query.expense_id, expense_query.user_id
        )
        if expense:
            self.logger.debug(
                "Expense found by ID", expense_id=expense.id, amount=expense.amount
            )
        else:
            self.logger.debug(
                "Expense not found by ID", expense_id=expense_query.expense_id
            )
        return expense

    def get_expenses(self, expense_filter: ExpenseFilter) -> List[Expense]:
        """Get all expenses with pagination and filters."""
        self.logger.debug(
            "Fetching expenses with filters",
            user_id=expense_filter.user_id,
            skip=expense_filter.skip,
            limit=expense_filter.limit,
        )
        expenses = self.expense_repo.get_expenses(expense_filter)
        self.logger.debug("Expenses fetched successfully", count=len(expenses))
        return expenses

    def update_expense(
        self, expense_id: int, expense_data: ExpenseUpdate, user_id: int
    ) -> Optional[Expense]:
        """Update an existing expense."""
        self.logger.info("Updating expense", expense_id=expense_id, user_id=user_id)

        try:
            expense = self.expense_repo.update_expense(
                expense_id, expense_data, user_id
            )
            if expense:
                self.logger.info(
                    "Expense updated successfully",
                    expense_id=expense.id,
                    amount=expense.amount,
                )
            else:
                self.logger.warning(
                    "Expense not found for update",
                    expense_id=expense_id,
                    user_id=user_id,
                )
            return expense
        except Exception as e:
            self.logger.error(
                "Failed to update expense",
                expense_id=expense_id,
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            raise

    def delete_expense(self, expense_query: ExpenseQuery) -> bool:
        """Delete an expense."""
        self.logger.info(
            "Deleting expense",
            expense_id=expense_query.expense_id,
            user_id=expense_query.user_id,
        )

        try:
            success = self.expense_repo.delete_expense(
                expense_query.expense_id, expense_query.user_id
            )
            if success:
                self.logger.info(
                    "Expense deleted successfully", expense_id=expense_query.expense_id
                )
            else:
                self.logger.warning(
                    "Expense not found for deletion",
                    expense_id=expense_query.expense_id,
                    user_id=expense_query.user_id,
                )
            return success
        except Exception as e:
            self.logger.error(
                "Failed to delete expense",
                expense_id=expense_query.expense_id,
                user_id=expense_query.user_id,
                error=str(e),
                exc_info=True,
            )
            raise

    def get_expense_stats(self, user_id: int) -> dict:
        """Get expense statistics for user."""
        self.logger.debug("Fetching expense statistics", user_id=user_id)

        try:
            stats = self.expense_repo.get_expense_stats(user_id)
            self.logger.debug(
                "Expense statistics fetched successfully",
                user_id=user_id,
                total_amount=stats.get("total_amount", 0),
            )
            return stats
        except Exception as e:
            self.logger.error(
                "Failed to fetch expense statistics",
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            raise

    def get_expenses_by_category(self, user_id: int) -> List[dict]:
        """Get expenses grouped by category."""
        self.logger.debug("Fetching expenses by category", user_id=user_id)

        try:
            category_stats = self.expense_repo.get_expenses_by_category(user_id)
            self.logger.debug(
                "Category statistics fetched successfully",
                user_id=user_id,
                categories=len(category_stats),
            )
            return category_stats
        except Exception as e:
            self.logger.error(
                "Failed to fetch category statistics",
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            raise
