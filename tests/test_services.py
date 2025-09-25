"""
Test service layer edge cases and error scenarios (Fixed version).
"""

import pytest
from decimal import Decimal
from datetime import date, datetime
from fastapi import HTTPException

from src.models.user import User
from src.models.category import Category
from src.models.expense import Expense
from src.services.user_service import UserService
from src.services.category_service import CategoryService
from src.services.expense_service import ExpenseService
from src.schemas.user import UserCreate, UserUpdate
from src.schemas.category import CategoryCreate, CategoryUpdate
from src.schemas.expense import ExpenseCreate, ExpenseUpdate


class TestUserServiceFixed:
    """Test UserService edge cases (fixed)."""
    
    def test_get_user_by_id_not_found(self, db):
        """Test getting user by non-existent ID."""
        user_service = UserService(db)
        user = user_service.get_user_by_id(99999)
        assert user is None
        
    def test_get_user_by_email_not_found(self, db):
        """Test getting user by non-existent email."""
        user_service = UserService(db)
        user = user_service.get_user_by_email("nonexistent@example.com")
        assert user is None
        
    def test_get_user_by_username_not_found(self, db):
        """Test getting user by non-existent username."""
        user_service = UserService(db)
        user = user_service.get_user_by_username("nonexistentuser")
        assert user is None
        
    def test_update_user_not_found(self, db):
        """Test updating non-existent user."""
        user_service = UserService(db)
        user_data = UserUpdate(email="new@example.com")
        result = user_service.update_user(99999, user_data)
        assert result is None
        
    def test_update_user_email_conflict(self, db, test_user):
        """Test updating user with existing email."""
        user_service = UserService(db)
        
        # Create another user
        other_user_data = UserCreate(
            email="other@example.com",
            username="otheruser",
            password="password123"
        )
        other_user = user_service.create_user(other_user_data)
        
        # Try to update first user with second user's email
        update_data = UserUpdate(email="other@example.com")
        with pytest.raises(HTTPException) as exc_info:
            user_service.update_user(test_user["id"], update_data)  # Use dict access
        assert exc_info.value.status_code == 400
        assert "Email already registered" in str(exc_info.value.detail)
        
    def test_delete_user_not_found(self, db):
        """Test deleting non-existent user."""
        user_service = UserService(db)
        result = user_service.delete_user(99999)
        assert result is False
        
    def test_authenticate_user_not_found(self, db):
        """Test authenticating non-existent user."""
        user_service = UserService(db)
        result = user_service.authenticate_user("nonexistent@example.com", "password")
        assert result is None
        
    def test_authenticate_user_wrong_password(self, db, test_user):
        """Test authenticating with wrong password."""
        user_service = UserService(db)
        result = user_service.authenticate_user(test_user["email"], "wrongpassword")  # Use dict access
        assert result is None
        
    def test_change_password_user_not_found(self, db):
        """Test changing password for non-existent user."""
        user_service = UserService(db)
        result = user_service.change_password(99999, "oldpass", "newpass")
        assert result is False


class TestCategoryServiceFixed:
    """Test CategoryService edge cases (fixed)."""
    
    def test_create_duplicate_category_name(self, db, test_user):
        """Test creating category with duplicate name."""
        category_service = CategoryService(db)
        
        # Create first category
        category_data = CategoryCreate(name="Food", description="Food expenses")
        category_service.create_category(test_user["id"], category_data)  # Use dict access
        
        # Try to create duplicate
        with pytest.raises(HTTPException) as exc_info:
            category_service.create_category(test_user["id"], category_data)  # Use dict access
        assert exc_info.value.status_code == 400
        assert "Category name already exists" in str(exc_info.value.detail)
        
    def test_get_category_by_id_not_found(self, db, test_user):
        """Test getting non-existent category."""
        category_service = CategoryService(db)
        result = category_service.get_category_by_id(99999, test_user["id"])  # Use dict access
        assert result is None
        
    def test_update_category_not_found(self, db, test_user):
        """Test updating non-existent category."""
        category_service = CategoryService(db)
        update_data = CategoryUpdate(name="Updated Name")
        result = category_service.update_category(99999, test_user["id"], update_data)  # Use dict access
        assert result is None
        
    def test_delete_category_not_found(self, db, test_user):
        """Test deleting non-existent category."""
        category_service = CategoryService(db)
        result = category_service.delete_category(99999, test_user["id"])  # Use dict access
        assert result is False


class TestExpenseServiceFixed:
    """Test ExpenseService edge cases (fixed)."""
    
    def test_create_expense_invalid_category(self, db, test_user):
        """Test creating expense with invalid category."""
        expense_service = ExpenseService(db)
        
        expense_data = ExpenseCreate(
            title="Test Expense",
            amount=Decimal("100.00"),
            category_id=99999,  # Non-existent category
            expense_date=date.today()
        )
        
        with pytest.raises(HTTPException) as exc_info:
            expense_service.create_expense(test_user["id"], expense_data)  # Use dict access
        assert exc_info.value.status_code == 404
        assert "Category not found" in str(exc_info.value.detail)
        
    def test_get_expense_by_id_not_found(self, db, test_user):
        """Test getting non-existent expense."""
        expense_service = ExpenseService(db)
        result = expense_service.get_expense_by_id(99999, test_user["id"])  # Use dict access
        assert result is None
        
    def test_update_expense_not_found(self, db, test_user):
        """Test updating non-existent expense."""
        expense_service = ExpenseService(db)
        update_data = ExpenseUpdate(title="Updated Title")
        result = expense_service.update_expense(99999, test_user["id"], update_data)  # Use dict access
        assert result is None
        
    def test_delete_expense_not_found(self, db, test_user):
        """Test deleting non-existent expense."""
        expense_service = ExpenseService(db)
        result = expense_service.delete_expense(99999, test_user["id"])  # Use dict access
        assert result is False
        
    def test_get_monthly_analytics_no_expenses(self, db, test_user):
        """Test monthly analytics with no expenses."""
        expense_service = ExpenseService(db)
        result = expense_service.get_monthly_analytics(test_user["id"], 2024, 1)  # Use dict access
        
        assert result["total_amount"] == Decimal("0")
        assert result["total_count"] == 0
        assert result["average_amount"] == Decimal("0")
        assert result["currency"] == "USD"
        assert result["top_categories"] == []
        assert result["recurring_count"] == 0
