"""
Analytics router for expense analytics and reporting.
"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.dependencies import get_current_active_user
from src.models.user import User
from src.schemas.expense import (
    CategoryStatsQuery,
    ExpenseStatsQuery,
    MonthlyAnalyticsQuery,
)
from src.services.expense.expense_service import ExpenseService

router = APIRouter()


@router.get("/stats")
def get_expense_stats(
    start_date: date = Query(None, description="Start date for statistics"),
    end_date: date = Query(None, description="End date for statistics"),
    currency: str = Query("USD", description="Currency for statistics"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get expense statistics for a user."""
    expense_service = ExpenseService(db)

    # Use Pydantic model for parameter validation
    stats_query = ExpenseStatsQuery(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        currency=currency,
    )

    return expense_service.get_expense_stats(stats_query)


@router.get("/category-stats")
def get_category_stats(
    start_date: date = Query(None, description="Start date for statistics"),
    end_date: date = Query(None, description="End date for statistics"),
    limit: int = Query(
        10, ge=1, le=50, description="Number of top categories to return"
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get expense statistics by category."""
    expense_service = ExpenseService(db)

    # Use Pydantic model for parameter validation
    stats_query = CategoryStatsQuery(
        user_id=current_user.id, start_date=start_date, end_date=end_date, limit=limit
    )

    return expense_service.get_category_stats(stats_query)


@router.get("/monthly/{year}/{month}")
def get_monthly_analytics(
    year: int,
    month: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get monthly analytics for a user."""
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")

    expense_service = ExpenseService(db)

    # Use Pydantic model for parameter validation
    analytics_query = MonthlyAnalyticsQuery(
        user_id=current_user.id, year=year, month=month
    )

    return expense_service.get_monthly_analytics(analytics_query)
