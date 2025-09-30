"""
Categories router for category management operations.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.dependencies import get_current_active_user
from src.models.user.user import User
from src.schemas.category.category import Category, CategoryCreate, CategoryUpdate
from src.services.category.category_service import CategoryService

router = APIRouter()


@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new category."""
    category_service = CategoryService(db)
    return category_service.create_category(category_data, current_user.id)


@router.get("/", response_model=List[Category])
def get_categories(
    skip: int = Query(0, ge=0, description="Number of categories to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of categories to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get user categories."""
    category_service = CategoryService(db)

    # Use Pydantic model for parameter validation
    return category_service.get_user_categories(current_user.id, skip=skip, limit=limit)


@router.get("/{category_id}", response_model=Category)
def get_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get category by ID."""
    category_service = CategoryService(db)

    # Use Pydantic model for parameter validation
    category = category_service.get_category_by_id(category_id, current_user.id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    return category


@router.put("/{category_id}", response_model=Category)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update category."""
    category_service = CategoryService(db)
    category = category_service.update_category(
        category_id, category_data, current_user.id
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    return category


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete category."""
    category_service = CategoryService(db)

    # Use Pydantic model for parameter validation
    success = category_service.delete_category(category_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    return {"message": "Category deleted successfully"}


@router.post("/init-system-categories")
def init_system_categories(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """Initialize system categories (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    category_service = CategoryService(db)
    categories = category_service.create_system_categories(current_user.id)

    return {
        "message": f"Created {len(categories)} system categories",
        "categories": categories,
    }
