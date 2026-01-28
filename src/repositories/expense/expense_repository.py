"""
Expense repository for database operations.
"""

from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, extract, func
from sqlalchemy.orm import Session

from src.models.expense.expense import Expense


class ExpenseRepository:
    """Expense repository for database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, expense: Expense) -> Expense:
        """Create a new expense."""
        self.db.add(expense)
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def get_by_id(self, expense_id: int, user_id: int) -> Optional[Expense]:
        """Get expense by ID for a specific user."""
        return (
            self.db.query(Expense)
            .filter(and_(Expense.id == expense_id, Expense.user_id == user_id))
            .first()
        )

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
        query = self.db.query(Expense).filter(Expense.user_id == user_id)

        if category_id:
            query = query.filter(Expense.category_id == category_id)

        if status:
            query = query.filter(Expense.status == status)

        if start_date:
            query = query.filter(Expense.expense_date >= start_date)

        if end_date:
            query = query.filter(Expense.expense_date <= end_date)

        return query.offset(skip).limit(limit).all()

    def get_monthly_expenses(
        self, user_id: int, year: int, month: int
    ) -> List[Expense]:
        """Get expenses for a specific month."""
        return (
            self.db.query(Expense)
            .filter(
                and_(
                    Expense.user_id == user_id,
                    extract("year", Expense.expense_date) == year,
                    extract("month", Expense.expense_date) == month,
                )
            )
            .all()
        )

    def get_expense_stats(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        currency: str = "USD",
    ) -> Dict[str, Any]:
        """Get expense statistics for a user."""
        query = self.db.query(Expense).filter(
            and_(Expense.user_id == user_id, Expense.currency == currency)
        )

        if start_date:
            query = query.filter(Expense.expense_date >= start_date)

        if end_date:
            query = query.filter(Expense.expense_date <= end_date)

        result = query.with_entities(
            func.sum(Expense.amount).label("total_amount"),
            func.count(Expense.id).label("total_count"),
            func.avg(Expense.amount).label("average_amount"),
        ).first()

        return {
            "total_amount": result.total_amount or Decimal("0"),
            "total_count": result.total_count or 0,
            "average_amount": result.average_amount or Decimal("0"),
            "currency": currency,
        }

    def get_category_stats(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get expense statistics by category."""
        query = self.db.query(Expense).filter(Expense.user_id == user_id)

        if start_date:
            query = query.filter(Expense.expense_date >= start_date)

        if end_date:
            query = query.filter(Expense.expense_date <= end_date)

        result = (
            query.with_entities(
                Expense.category_id,
                func.sum(Expense.amount).label("total_amount"),
                func.count(Expense.id).label("total_count"),
            )
            .group_by(Expense.category_id)
            .order_by(func.sum(Expense.amount).desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "category_id": row.category_id,
                "total_amount": row.total_amount or Decimal("0"),
                "total_count": row.total_count or 0,
            }
            for row in result
        ]

    def update(self, expense: Expense) -> Expense:
        """Update expense."""
        self.db.commit()
        self.db.refresh(expense)
        return expense

    def delete(self, expense_id: int, user_id: int) -> bool:
        """Delete expense by ID for a specific user."""
        expense = self.get_by_id(expense_id, user_id)
        if expense:
            self.db.delete(expense)
            self.db.commit()
            return True
        return False
