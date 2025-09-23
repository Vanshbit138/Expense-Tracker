"""
Expenses router for expense management operations.
"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.dependencies import get_current_active_user
from src.models.user import User
from src.schemas.expense import Expense, ExpenseCreate, ExpenseUpdate
from src.services.expense_service import ExpenseService

router = APIRouter()


@router.post("/", response_model=Expense, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new expense."""
    expense_service = ExpenseService(db)
    return expense_service.create_expense(current_user.id, expense_data)


@router.get("/", response_model=List[Expense])
def get_expenses(
    skip: int = Query(0, ge=0, description="Number of expenses to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of expenses to return"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get user expenses with optional filters."""
    expense_service = ExpenseService(db)
    return expense_service.get_user_expenses(
        current_user.id, skip, limit, category_id, status, start_date, end_date
    )


@router.get("/{expense_id}", response_model=Expense)
def get_expense(
    expense_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get expense by ID."""
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
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update expense."""
    expense_service = ExpenseService(db)
    expense = expense_service.update_expense(expense_id, current_user.id, expense_data)

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
        )

    return expense


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete expense."""
    expense_service = ExpenseService(db)
    success = expense_service.delete_expense(expense_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
        )

    return {"message": "Expense deleted successfully"}


@router.get("/monthly/{year}/{month}", response_model=List[Expense])
def get_monthly_expenses(
    year: int,
    month: int,
    current_user: User = Depends(get_current_active_user),
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
