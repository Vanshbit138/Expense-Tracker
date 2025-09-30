"""
Expense service for business logic operations.
"""

from datetime import date
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.core.logging_config import get_logger
from src.models.expense.expense import Expense
from src.repositories.expense.expense_repository import ExpenseRepository
from src.schemas.expense.expense import ExpenseCreate, ExpenseUpdate
from src.schemas.expense.expense_queries import ExpenseFilter

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
            "Creating new expense", amount=expense_data.amount, user_id=user_id
        )

        try:
            # Validate category access
            self._validate_category_access(expense_data.category_id, user_id)

            expense = self.expense_repo.create(
                Expense(
                    amount=expense_data.amount,
                    currency=expense_data.currency,
                    description=expense_data.description,
                    category_id=expense_data.category_id,
                    user_id=user_id,
                    expense_date=expense_data.expense_date,
                    status=expense_data.status,
                    is_recurring=expense_data.is_recurring,
                    recurring_frequency=expense_data.recurring_frequency,
                )
            )

            self.logger.info(
                "Expense created successfully",
                expense_id=expense.id,
                amount=expense.amount,
            )
            return expense
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to create expense",
                amount=expense_data.amount,
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create expense",
            )

    def get_expense_by_id(self, expense_id: int, user_id: int) -> Expense:
        """Get expense by ID."""
        self.logger.debug(
            "Getting expense by ID", expense_id=expense_id, user_id=user_id
        )
        expense = self.expense_repo.get_by_id(expense_id, user_id)
        if not expense:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
            )
        return expense

    def get_user_expenses(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Expense]:
        """Get expenses for a user."""
        self.logger.debug(
            "Getting user expenses", user_id=user_id, skip=skip, limit=limit
        )
        return self.expense_repo.get_user_expenses(user_id, skip=skip, limit=limit)

    def update_expense(
        self, expense_id: int, expense_data: ExpenseUpdate, user_id: int
    ) -> Expense:
        """Update expense information."""
        self.logger.info("Updating expense", expense_id=expense_id, user_id=user_id)

        try:
            # Fetch existing expense first
            expense = self.expense_repo.get_by_id(expense_id, user_id)
            if not expense:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
                )

            # Update fields if provided
            if expense_data.amount is not None:
                expense.amount = expense_data.amount

            if expense_data.currency is not None:
                expense.currency = expense_data.currency

            if expense_data.description is not None:
                expense.description = expense_data.description

            if expense_data.category_id is not None:
                self._validate_category_access(expense_data.category_id, user_id)
                expense.category_id = expense_data.category_id

            if expense_data.expense_date is not None:
                expense.expense_date = expense_data.expense_date

            if expense_data.status is not None:
                expense.status = expense_data.status

            if expense_data.is_recurring is not None:
                expense.is_recurring = expense_data.is_recurring

            if expense_data.recurring_frequency is not None:
                expense.recurring_frequency = expense_data.recurring_frequency

            # Save changes
            updated_expense = self.expense_repo.update(expense)
            self.logger.info(
                "Expense updated successfully", expense_id=updated_expense.id
            )
            return updated_expense

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to update expense",
                expense_id=expense_id,
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update expense",
            )

    def delete_expense(self, expense_id: int, user_id: int) -> bool:
        """Delete expense."""
        self.logger.info("Deleting expense", expense_id=expense_id, user_id=user_id)

        try:
            success = self.expense_repo.delete(expense_id, user_id)

            if success:
                self.logger.info("Expense deleted successfully", expense_id=expense_id)
            else:
                self.logger.warning("Failed to delete expense", expense_id=expense_id)

            return success

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to delete expense",
                expense_id=expense_id,
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete expense",
            )

    def get_all_expenses(self, query: ExpenseFilter) -> List[Expense]:
        """Get all expenses with filtering and pagination."""
        self.logger.debug("Getting all expenses", filters=query.model_dump())

        try:
            expenses = self.expense_repo.get_all(skip=query.skip, limit=query.limit)

            self.logger.debug("Expenses retrieved successfully", count=len(expenses))
            return expenses

        except Exception as e:
            self.logger.error("Failed to get expenses", error=str(e), exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve expenses",
            )

    def get_expense_stats(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        currency: str = "USD",
    ) -> dict:
        """Get expense statistics for user."""
        self.logger.debug(
            "Fetching expense statistics", user_id=user_id, currency=currency
        )

        try:
            stats = self.expense_repo.get_expense_stats(
                user_id, start_date=start_date, end_date=end_date, currency=currency
            )
            self.logger.debug(
                "Expense statistics fetched successfully",
                user_id=user_id,
                total_amount=stats.get("total_amount", 0),
                currency=currency,
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

    def get_category_stats(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[dict]:
        """Get expense statistics by category."""
        self.logger.debug(
            "Fetching category statistics",
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )

        try:
            stats = self.expense_repo.get_category_stats(
                user_id, start_date=start_date, end_date=end_date
            )
            self.logger.debug(
                "Category statistics fetched successfully",
                user_id=user_id,
                category_count=len(stats),
            )
            return stats
        except Exception as e:
            self.logger.error(
                "Failed to fetch category statistics",
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            raise

    def get_monthly_expenses(
        self, user_id: int, year: int, month: int
    ) -> List[Expense]:
        """Get expenses for a specific month."""
        self.logger.debug(
            "Fetching monthly expenses", user_id=user_id, year=year, month=month
        )

        try:
            expenses = self.expense_repo.get_monthly_expenses(
                user_id, year=year, month=month
            )
            self.logger.debug(
                "Monthly expenses fetched successfully",
                user_id=user_id,
                year=year,
                month=month,
                count=len(expenses),
            )
            return expenses
        except Exception as e:
            self.logger.error(
                "Failed to fetch monthly expenses",
                user_id=user_id,
                year=year,
                month=month,
                error=str(e),
                exc_info=True,
            )
            raise

    def get_monthly_analytics(self, user_id: int, year: int, month: int) -> dict:
        """Get monthly analytics for user."""
        self.logger.debug(
            "Fetching monthly analytics", user_id=user_id, year=year, month=month
        )

        try:
            analytics = self.expense_repo.get_monthly_expenses(
                user_id, year=year, month=month
            )
            self.logger.debug(
                "Monthly analytics fetched successfully",
                user_id=user_id,
                year=year,
                month=month,
            )
            return analytics
        except Exception as e:
            self.logger.error(
                "Failed to fetch monthly analytics",
                user_id=user_id,
                error=str(e),
                exc_info=True,
            )
            raise

    def _validate_category_access(self, category_id: int, user_id: int) -> None:
        """Validate user access to category."""
        from src.repositories.category.category_repository import CategoryRepository

        category_repo = CategoryRepository(self.db)
        category = category_repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )
        if category.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to category",
            )
