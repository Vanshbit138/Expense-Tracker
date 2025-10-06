"""
Analytics router for expense statistics and reporting.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.core.auth_bypass import get_current_active_user_with_bypass
from src.core.database import get_db
from src.core.logging_config import get_logger
from src.models.user.user import User
from src.services.expense.expense_service import ExpenseService

# Initialize router and logger
router = APIRouter()
logger = get_logger(__name__)


@router.get("/stats")
def get_expense_stats(
    start_date: Optional[date] = Query(None, description="Start date for statistics"),
    end_date: Optional[date] = Query(None, description="End date for statistics"),
    currency: Optional[str] = Query(None, description="Currency filter"),
    current_user: User = Depends(get_current_active_user_with_bypass),
    db: Session = Depends(get_db),
):
    """Get expense statistics for the user."""
    logger.info(
        "Fetching expense statistics",
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        currency=currency,
    )

    expense_service = ExpenseService(db)
    return expense_service.get_expense_stats(
        current_user.id, start_date=start_date, end_date=end_date
    )


@router.get("/category-stats")
def get_category_stats(
    start_date: Optional[date] = Query(None, description="Start date for statistics"),
    end_date: Optional[date] = Query(None, description="End date for statistics"),
    limit: int = Query(10, ge=1, le=50, description="Number of categories to return"),
    current_user: User = Depends(get_current_active_user_with_bypass),
    db: Session = Depends(get_db),
):
    """Get expense statistics by category."""
    logger.info(
        "Fetching category statistics",
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )

    expense_service = ExpenseService(db)
    return expense_service.get_category_stats(
        current_user.id, start_date=start_date, end_date=end_date
    )


@router.get("/monthly/{year}/{month}")
def get_monthly_analytics(
    year: int,
    month: int,
    current_user: User = Depends(get_current_active_user_with_bypass),
    db: Session = Depends(get_db),
):
    """Get monthly analytics for a specific month."""
    if not (1 <= month <= 12):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Month must be between 1 and 12",
        )

    logger.info(
        "Fetching monthly analytics",
        user_id=current_user.id,
        year=year,
        month=month,
    )

    expense_service = ExpenseService(db)
    return expense_service.get_monthly_analytics(current_user.id, year, month)
