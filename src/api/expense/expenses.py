"""
Expense router for CRUD operations and analytics.
"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.core.auth_bypass import get_current_active_user_with_bypass
from src.core.database import get_db
from src.core.logging_config import get_logger
from src.models.user.user import User
from src.schemas.expense.expense import Expense, ExpenseCreate, ExpenseUpdate
from src.services.expense.expense_service import ExpenseService

# Initialize router and logger
router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=Expense, status_code=201)
def create_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_active_user_with_bypass),
    db: Session = Depends(get_db),
):
    """Create a new expense."""
    logger.info(
        "Creating expense",
        user_id=current_user.id,
        amount=expense_data.amount,
        description=expense_data.description,
    )

    try:
        expense_service = ExpenseService(db)
        expense = expense_service.create_expense(expense_data, current_user.id)

        logger.info(
            "Expense created successfully",
            expense_id=expense.id,
            user_id=current_user.id,
        )
        return expense
    except HTTPException as e:
        logger.error("Expense creation failed", user_id=current_user.id, error=e.detail)
        raise
    except Exception as e:
        logger.error(
            "Expense creation failed with unexpected error",
            user_id=current_user.id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during expense creation",
        )


@router.get("/", response_model=List[Expense])
def get_expenses(
    skip: int = Query(0, ge=0, description="Number of expenses to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of expenses to return"),
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    current_user: User = Depends(get_current_active_user_with_bypass),
    db: Session = Depends(get_db),
):
    """Get user's expenses with optional filtering."""
    logger.info(
        "Fetching expenses",
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )

    expense_service = ExpenseService(db)
    return expense_service.get_user_expenses(current_user.id, skip=skip, limit=limit)


@router.get("/{expense_id}", response_model=Expense)
def get_expense(
    expense_id: int,
    current_user: User = Depends(get_current_active_user_with_bypass),
    db: Session = Depends(get_db),
):
    """Get a specific expense by ID."""
    logger.info("Fetching expense", expense_id=expense_id, user_id=current_user.id)

    expense_service = ExpenseService(db)
    expense = expense_service.get_expense_by_id(expense_id, current_user.id)

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
        )

    return expense


@router.put("/{expense_id}", response_model=Expense)
def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    current_user: User = Depends(get_current_active_user_with_bypass),
    db: Session = Depends(get_db),
):
    """Update an existing expense."""
    logger.info("Updating expense", expense_id=expense_id, user_id=current_user.id)

    try:
        expense_service = ExpenseService(db)
        updated_expense = expense_service.update_expense(
            expense_id, expense_data, current_user.id
        )

        logger.info(
            "Expense updated successfully",
            expense_id=expense_id,
            user_id=current_user.id,
        )
        return updated_expense
    except HTTPException as e:
        logger.warning("Expense update failed", expense_id=expense_id, error=e.detail)
        raise
    except Exception as e:
        logger.error(
            "Expense update failed with unexpected error",
            expense_id=expense_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during expense update",
        )


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_active_user_with_bypass),
    db: Session = Depends(get_db),
):
    """Delete an expense."""
    logger.info("Deleting expense", expense_id=expense_id, user_id=current_user.id)

    try:
        expense_service = ExpenseService(db)
        success = expense_service.delete_expense(expense_id, current_user.id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
            )

        logger.info(
            "Expense deleted successfully",
            expense_id=expense_id,
            user_id=current_user.id,
        )
        return {"message": "Expense deleted successfully"}
    except HTTPException as e:
        logger.warning("Expense deletion failed", expense_id=expense_id, error=e.detail)
        raise
    except Exception as e:
        logger.error(
            "Expense deletion failed with unexpected error",
            expense_id=expense_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during expense deletion",
        )


@router.get("/monthly/{year}/{month}", response_model=List[Expense])
def get_monthly_expenses(
    year: int,
    month: int,
    current_user: User = Depends(get_current_active_user_with_bypass),
    db: Session = Depends(get_db),
):
    """Get expenses for a specific month."""
    if not (1 <= month <= 12):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Month must be between 1 and 12",
        )

    expense_service = ExpenseService(db)
    return expense_service.get_monthly_expenses(current_user.id, year, month)
