"""
Test service layer edge cases and error scenarios (Using organized structure).
"""

from datetime import date
from decimal import Decimal

import pytest
from fastapi import HTTPException

from src.schemas.category import CategoryCreate, CategoryUpdate
from src.schemas.category_queries import CategoryQuery
from src.schemas.expense import (
    ExpenseCreate,
    ExpenseQuery,
    ExpenseUpdate,
    MonthlyAnalyticsQuery,
)
from src.schemas.user import UserUpdate
from src.schemas.user_queries import AuthenticationQuery, UserQuery
from src.services.category.category_service import CategoryService
from src.services.expense.expense_service import ExpenseService
from src.services.user.user_service import UserService


class TestUserServiceRefactored:
    """Test UserService edge cases with refactored structure."""

    def test_get_user_by_id_not_found(self, db):
        """Test getting user by non-existent ID."""
        user_service = UserService(db)
        user_query = UserQuery(user_id=99999)
        user = user_service.get_user_by_id(user_query)
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
        # Try to update first user with second user's email
        update_data = UserUpdate(email="other@example.com")
        with pytest.raises(HTTPException) as exc_info:
            user_service.update_user(test_user["id"], update_data)
        assert exc_info.value.status_code == 400
        assert "Email already registered" in str(exc_info.value.detail)

    def test_delete_user_not_found(self, db):
        """Test deleting non-existent user."""
        user_service = UserService(db)
        user_query = UserQuery(user_id=99999)
        result = user_service.delete_user(user_query)
        assert result is False

    def test_authenticate_user_not_found(self, db):
        """Test authenticating non-existent user."""
        user_service = UserService(db)
        auth_query = AuthenticationQuery(
            email="nonexistent@example.com", password="password"
        )
        result = user_service.authenticate_user(auth_query)
        assert result is None

    def test_authenticate_user_wrong_password(self, db, test_user):
        """Test authenticating with wrong password."""
        user_service = UserService(db)
        auth_query = AuthenticationQuery(
            email=test_user["email"], password="wrongpassword"
        )
        result = user_service.authenticate_user(auth_query)
        assert result is None

    def test_change_password_user_not_found(self, db):
        """Test changing password for non-existent user."""
        from fastapi import HTTPException

        from src.schemas.user_queries import PasswordChangeQuery

        user_service = UserService(db)
        password_query = PasswordChangeQuery(
            user_id=99999, current_password="oldpass", new_password="newpass"
        )

        try:
            user_service.change_password(password_query)
            assert False, "Expected HTTPException to be raised"
        except HTTPException as e:
            assert e.status_code == 404
            assert "User not found" in e.detail


class TestCategoryServiceRefactored:
    """Test CategoryService edge cases with refactored structure."""

    def test_create_duplicate_category_name(self, db, test_user):
        """Test creating category with duplicate name."""
        category_service = CategoryService(db)

        # Create first category
        category_data = CategoryCreate(name="Food", description="Food expenses")
        category_service.create_category(test_user["id"], category_data)

        # Try to create duplicate
        with pytest.raises(HTTPException) as exc_info:
            category_service.create_category(test_user["id"], category_data)
        assert exc_info.value.status_code == 400
        assert "Category name already exists" in str(exc_info.value.detail)

    def test_get_category_by_id_not_found(self, db, test_user):
        """Test getting non-existent category."""
        category_service = CategoryService(db)
        category_query = CategoryQuery(category_id=99999, user_id=test_user["id"])
        result = category_service.get_category_by_id(category_query)
        assert result is None

    def test_update_category_not_found(self, db, test_user):
        """Test updating non-existent category."""
        category_service = CategoryService(db)
        update_data = CategoryUpdate(name="Updated Name")
        result = category_service.update_category(99999, test_user["id"], update_data)
        assert result is None

    def test_delete_category_not_found(self, db, test_user):
        """Test deleting non-existent category."""
        category_service = CategoryService(db)
        category_query = CategoryQuery(category_id=99999, user_id=test_user["id"])
        result = category_service.delete_category(category_query)
        assert result is False


class TestExpenseServiceRefactored:
    """Test ExpenseService edge cases with refactored structure."""

    def test_create_expense_invalid_category(self, db, test_user):
        """Test creating expense with invalid category."""
        expense_service = ExpenseService(db)

        expense_data = ExpenseCreate(
            description="Test Expense",
            amount=Decimal("100.00"),
            category_id=99999,  # Non-existent category
            expense_date=date.today(),
        )

        with pytest.raises(HTTPException) as exc_info:
            expense_service.create_expense(test_user["id"], expense_data)
        assert exc_info.value.status_code == 404
        assert "Category not found" in str(exc_info.value.detail)

    def test_get_expense_by_id_not_found(self, db, test_user):
        """Test getting non-existent expense."""
        expense_service = ExpenseService(db)
        expense_query = ExpenseQuery(expense_id=99999, user_id=test_user["id"])
        result = expense_service.get_expense_by_id(expense_query)
        assert result is None

    def test_update_expense_not_found(self, db, test_user):
        """Test updating non-existent expense."""
        expense_service = ExpenseService(db)
        update_data = ExpenseUpdate(description="Updated Description")
        result = expense_service.update_expense(99999, test_user["id"], update_data)
        assert result is None

    def test_delete_expense_not_found(self, db, test_user):
        """Test deleting non-existent expense."""
        expense_service = ExpenseService(db)
        expense_query = ExpenseQuery(expense_id=99999, user_id=test_user["id"])
        result = expense_service.delete_expense(expense_query)
        assert result is False

    def test_get_monthly_analytics_no_expenses(self, db, test_user):
        """Test monthly analytics with no expenses."""
        expense_service = ExpenseService(db)
        analytics_query = MonthlyAnalyticsQuery(
            user_id=test_user["id"], year=2024, month=1
        )
        result = expense_service.get_monthly_analytics(analytics_query)

        assert result["total_amount"] == Decimal("0")
        assert result["total_count"] == 0
        assert result["average_amount"] == Decimal("0")
        assert result["currency"] == "USD"
        assert result["top_categories"] == []
        assert result["recurring_count"] == 0
