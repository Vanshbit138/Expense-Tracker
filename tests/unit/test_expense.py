"""
Unit tests for expense service and repository.
"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.expense.expense import Expense
from src.schemas.expense.expense import ExpenseCreate, ExpenseUpdate
from src.schemas.expense.expense_queries import ExpenseFilter
from src.services.expense.expense_service import ExpenseService


class TestExpenseService:
    """Test cases for ExpenseService class."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return MagicMock(spec=Session)

    @pytest.fixture
    def expense_service(self, mock_db_session):
        """Create an ExpenseService instance with mocked dependencies."""
        with patch(
            "src.services.expense.expense_service.ExpenseRepository"
        ) as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            service = ExpenseService(mock_db_session)
            service.expense_repo = mock_repo
            return service

    def test_create_expense_success(self, expense_service, sample_expense_create):
        """Test successful expense creation."""
        # Arrange
        mock_expense = Expense(
            id=1,
            amount=sample_expense_create.amount,
            currency=sample_expense_create.currency,
            description=sample_expense_create.description,
            status=sample_expense_create.status,
            is_recurring=sample_expense_create.is_recurring,
            recurring_frequency=sample_expense_create.recurring_frequency,
            expense_date=sample_expense_create.expense_date,
            user_id=1,
            category_id=sample_expense_create.category_id,
        )
        expense_service.expense_repo.create.return_value = mock_expense

        # Act
        result = expense_service.create_expense(sample_expense_create, user_id=1)

        # Assert
        assert result == mock_expense
        expense_service.expense_repo.create.assert_called_once()

    def test_create_expense_database_error(
        self, expense_service, sample_expense_create
    ):
        """Test expense creation with database error."""
        # Arrange
        expense_service.expense_repo.create.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            expense_service.create_expense(sample_expense_create, user_id=1)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to create expense" in exc_info.value.detail

    def test_get_expense_by_id_success(self, expense_service):
        """Test successful expense retrieval by ID."""
        # Arrange
        mock_expense = Expense(
            id=1, amount=Decimal("100.00"), currency="USD", user_id=1, category_id=1
        )
        expense_service.expense_repo.get_by_id.return_value = mock_expense

        # Act
        result = expense_service.get_expense_by_id(1, user_id=1)

        # Assert
        assert result == mock_expense
        expense_service.expense_repo.get_by_id.assert_called_once_with(1)

    def test_get_expense_by_id_not_found(self, expense_service):
        """Test expense retrieval by ID when expense not found."""
        # Arrange
        expense_service.expense_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            expense_service.get_expense_by_id(1, user_id=1)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Expense not found" in exc_info.value.detail

    def test_get_expense_by_id_wrong_user(self, expense_service):
        """Test expense retrieval by ID when user doesn't own expense."""
        # Arrange
        mock_expense = Expense(
            id=1, amount=Decimal("100.00"), user_id=2  # Different user
        )
        expense_service.expense_repo.get_by_id.return_value = mock_expense

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            expense_service.get_expense_by_id(1, user_id=1)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Access denied to expense" in exc_info.value.detail

    def test_get_user_expenses_success(self, expense_service):
        """Test successful user expenses retrieval."""
        # Arrange
        mock_expenses = [
            Expense(id=1, amount=Decimal("50.00"), user_id=1, category_id=1),
            Expense(id=2, amount=Decimal("75.00"), user_id=1, category_id=2),
        ]
        expense_service.expense_repo.get_user_expenses.return_value = mock_expenses

        # Act
        result = expense_service.get_user_expenses(user_id=1, skip=0, limit=10)

        # Assert
        assert result == mock_expenses
        expense_service.expense_repo.get_user_expenses.assert_called_once_with(
            1, skip=0, limit=10
        )

    def test_get_user_expenses_with_filters(self, expense_service):
        """Test user expenses retrieval with date filters."""
        # Arrange
        mock_expenses = [
            Expense(id=1, amount=Decimal("50.00"), user_id=1, category_id=1)
        ]
        expense_service.expense_repo.get_user_expenses.return_value = mock_expenses

        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)

        # Act
        result = expense_service.get_user_expenses(
            user_id=1, skip=0, limit=10, start_date=start_date, end_date=end_date
        )

        # Assert
        assert result == mock_expenses
        expense_service.expense_repo.get_user_expenses.assert_called_once_with(
            1, skip=0, limit=10, start_date=start_date, end_date=end_date
        )

    def test_update_expense_success(self, expense_service):
        """Test successful expense update."""
        # Arrange
        existing_expense = Expense(
            id=1,
            amount=Decimal("100.00"),
            description="Old description",
            user_id=1,
            category_id=1,
        )
        expense_service.expense_repo.get_by_id.return_value = existing_expense
        expense_service.expense_repo.update.return_value = existing_expense

        update_data = ExpenseUpdate(
            amount=Decimal("150.00"), description="New description"
        )

        # Act
        result = expense_service.update_expense(1, update_data, user_id=1)

        # Assert
        assert result == existing_expense
        assert existing_expense.amount == Decimal("150.00")
        assert existing_expense.description == "New description"
        expense_service.expense_repo.update.assert_called_once_with(existing_expense)

    def test_update_expense_not_found(self, expense_service):
        """Test expense update when expense not found."""
        # Arrange
        expense_service.expense_repo.get_by_id.return_value = None
        update_data = ExpenseUpdate(amount=Decimal("150.00"))

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            expense_service.update_expense(1, update_data, user_id=1)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Expense not found" in exc_info.value.detail

    def test_update_expense_wrong_user(self, expense_service):
        """Test expense update when user doesn't own expense."""
        # Arrange
        existing_expense = Expense(
            id=1, amount=Decimal("100.00"), user_id=2  # Different user
        )
        expense_service.expense_repo.get_by_id.return_value = existing_expense
        update_data = ExpenseUpdate(amount=Decimal("150.00"))

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            expense_service.update_expense(1, update_data, user_id=1)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Access denied to expense" in exc_info.value.detail

    def test_delete_expense_success(self, expense_service):
        """Test successful expense deletion."""
        # Arrange
        expense_service.expense_repo.delete.return_value = True

        # Act
        result = expense_service.delete_expense(1, user_id=1)

        # Assert
        assert result is True
        expense_service.expense_repo.delete.assert_called_once_with(1)

    def test_delete_expense_not_found(self, expense_service):
        """Test expense deletion when expense not found."""
        # Arrange
        expense_service.expense_repo.delete.return_value = False

        # Act
        result = expense_service.delete_expense(1, user_id=1)

        # Assert
        assert result is False

    def test_delete_expense_database_error(self, expense_service):
        """Test expense deletion with database error."""
        # Arrange
        expense_service.expense_repo.delete.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            expense_service.delete_expense(1, user_id=1)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to delete expense" in exc_info.value.detail

    def test_get_all_expenses_success(self, expense_service):
        """Test successful all expenses retrieval with filtering."""
        # Arrange
        mock_expenses = [
            Expense(id=1, amount=Decimal("50.00"), user_id=1, category_id=1),
            Expense(id=2, amount=Decimal("75.00"), user_id=2, category_id=2),
        ]
        expense_service.expense_repo.get_all.return_value = mock_expenses

        expense_filter = ExpenseFilter(skip=0, limit=10)

        # Act
        result = expense_service.get_all_expenses(expense_filter)

        # Assert
        assert result == mock_expenses
        expense_service.expense_repo.get_all.assert_called_once_with(skip=0, limit=10)

    def test_get_all_expenses_database_error(self, expense_service):
        """Test all expenses retrieval with database error."""
        # Arrange
        expense_service.expense_repo.get_all.side_effect = Exception("Database error")

        expense_filter = ExpenseFilter(skip=0, limit=10)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            expense_service.get_all_expenses(expense_filter)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to retrieve expenses" in exc_info.value.detail

    def test_get_expenses_by_category_success(self, expense_service):
        """Test successful expenses retrieval by category."""
        # Arrange
        mock_expenses = [
            Expense(id=1, amount=Decimal("50.00"), user_id=1, category_id=1),
            Expense(id=2, amount=Decimal("75.00"), user_id=1, category_id=1),
        ]
        expense_service.expense_repo.get_by_category.return_value = mock_expenses

        # Act
        result = expense_service.get_expenses_by_category(category_id=1, user_id=1)

        # Assert
        assert result == mock_expenses
        expense_service.expense_repo.get_by_category.assert_called_once_with(1, 1)

    def test_get_expenses_by_category_not_found(self, expense_service):
        """Test expenses retrieval by category when no expenses found."""
        # Arrange
        expense_service.expense_repo.get_by_category.return_value = []

        # Act
        result = expense_service.get_expenses_by_category(category_id=1, user_id=1)

        # Assert
        assert result == []

    def test_get_expenses_by_category_database_error(self, expense_service):
        """Test expenses retrieval by category with database error."""
        # Arrange
        expense_service.expense_repo.get_by_category.side_effect = Exception(
            "Database error"
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            expense_service.get_expenses_by_category(category_id=1, user_id=1)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to retrieve expenses by category" in exc_info.value.detail

    def test_get_expenses_by_status_success(self, expense_service):
        """Test successful expenses retrieval by status."""
        # Arrange
        mock_expenses = [
            Expense(
                id=1,
                amount=Decimal("50.00"),
                status="pending",
                user_id=1,
                category_id=1,
            ),
            Expense(
                id=2,
                amount=Decimal("75.00"),
                status="pending",
                user_id=1,
                category_id=2,
            ),
        ]
        expense_service.expense_repo.get_by_status.return_value = mock_expenses

        # Act
        result = expense_service.get_expenses_by_status(status="pending", user_id=1)

        # Assert
        assert result == mock_expenses
        expense_service.expense_repo.get_by_status.assert_called_once_with("pending", 1)

    def test_get_expenses_by_status_not_found(self, expense_service):
        """Test expenses retrieval by status when no expenses found."""
        # Arrange
        expense_service.expense_repo.get_by_status.return_value = []

        # Act
        result = expense_service.get_expenses_by_status(status="approved", user_id=1)

        # Assert
        assert result == []

    def test_get_expenses_by_status_database_error(self, expense_service):
        """Test expenses retrieval by status with database error."""
        # Arrange
        expense_service.expense_repo.get_by_status.side_effect = Exception(
            "Database error"
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            expense_service.get_expenses_by_status(status="pending", user_id=1)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to retrieve expenses by status" in exc_info.value.detail

    def test_get_expenses_by_date_range_success(self, expense_service):
        """Test successful expenses retrieval by date range."""
        # Arrange
        mock_expenses = [
            Expense(id=1, amount=Decimal("50.00"), user_id=1, category_id=1),
            Expense(id=2, amount=Decimal("75.00"), user_id=1, category_id=2),
        ]
        expense_service.expense_repo.get_by_date_range.return_value = mock_expenses

        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)

        # Act
        result = expense_service.get_expenses_by_date_range(
            start_date=start_date, end_date=end_date, user_id=1
        )

        # Assert
        assert result == mock_expenses
        expense_service.expense_repo.get_by_date_range.assert_called_once_with(
            start_date, end_date, 1
        )

    def test_get_expenses_by_date_range_not_found(self, expense_service):
        """Test expenses retrieval by date range when no expenses found."""
        # Arrange
        expense_service.expense_repo.get_by_date_range.return_value = []

        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)

        # Act
        result = expense_service.get_expenses_by_date_range(
            start_date=start_date, end_date=end_date, user_id=1
        )

        # Assert
        assert result == []

    def test_get_expenses_by_date_range_database_error(self, expense_service):
        """Test expenses retrieval by date range with database error."""
        # Arrange
        expense_service.expense_repo.get_by_date_range.side_effect = Exception(
            "Database error"
        )

        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            expense_service.get_expenses_by_date_range(
                start_date=start_date, end_date=end_date, user_id=1
            )

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to retrieve expenses by date range" in exc_info.value.detail

    def test_get_expenses_by_amount_range_success(self, expense_service):
        """Test successful expenses retrieval by amount range."""
        # Arrange
        mock_expenses = [
            Expense(id=1, amount=Decimal("50.00"), user_id=1, category_id=1),
            Expense(id=2, amount=Decimal("75.00"), user_id=1, category_id=2),
        ]
        expense_service.expense_repo.get_by_amount_range.return_value = mock_expenses

        min_amount = Decimal("40.00")
        max_amount = Decimal("100.00")

        # Act
        result = expense_service.get_expenses_by_amount_range(
            min_amount=min_amount, max_amount=max_amount, user_id=1
        )

        # Assert
        assert result == mock_expenses
        expense_service.expense_repo.get_by_amount_range.assert_called_once_with(
            min_amount, max_amount, 1
        )

    def test_get_expenses_by_amount_range_not_found(self, expense_service):
        """Test expenses retrieval by amount range when no expenses found."""
        # Arrange
        expense_service.expense_repo.get_by_amount_range.return_value = []

        min_amount = Decimal("200.00")
        max_amount = Decimal("300.00")

        # Act
        result = expense_service.get_expenses_by_amount_range(
            min_amount=min_amount, max_amount=max_amount, user_id=1
        )

        # Assert
        assert result == []

    def test_get_expenses_by_amount_range_database_error(self, expense_service):
        """Test expenses retrieval by amount range with database error."""
        # Arrange
        expense_service.expense_repo.get_by_amount_range.side_effect = Exception(
            "Database error"
        )

        min_amount = Decimal("40.00")
        max_amount = Decimal("100.00")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            expense_service.get_expenses_by_amount_range(
                min_amount=min_amount, max_amount=max_amount, user_id=1
            )

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to retrieve expenses by amount range" in exc_info.value.detail


class TestExpenseServiceIntegration:
    """Integration tests for ExpenseService."""

    def test_expense_lifecycle(self, expense_service):
        """Test complete expense lifecycle: create, read, update, delete."""
        # Create expense
        expense_create = ExpenseCreate(
            amount=Decimal("100.00"),
            currency="USD",
            description="Test expense",
            status="pending",
            is_recurring=False,
            recurring_frequency=None,
            expense_date=datetime(2023, 1, 1),
            category_id=1,
        )

        created_expense = Expense(
            id=1,
            amount=expense_create.amount,
            currency=expense_create.currency,
            description=expense_create.description,
            status=expense_create.status,
            is_recurring=expense_create.is_recurring,
            recurring_frequency=expense_create.recurring_frequency,
            expense_date=expense_create.expense_date,
            user_id=1,
            category_id=expense_create.category_id,
        )

        expense_service.expense_repo.create.return_value = created_expense

        result = expense_service.create_expense(expense_create, user_id=1)
        assert result == created_expense

        # Read expense
        expense_service.expense_repo.get_by_id.return_value = created_expense
        result = expense_service.get_expense_by_id(1, user_id=1)
        assert result == created_expense

        # Update expense
        update_data = ExpenseUpdate(description="Updated description")
        expense_service.expense_repo.update.return_value = created_expense
        result = expense_service.update_expense(1, update_data, user_id=1)
        assert result == created_expense

        # Delete expense
        expense_service.expense_repo.delete.return_value = True
        result = expense_service.delete_expense(1, user_id=1)
        assert result is True

    def test_expense_filtering_workflow(self, expense_service):
        """Test expense filtering workflow with various criteria."""
        # Create multiple expenses
        expenses_data = [
            ExpenseCreate(
                amount=Decimal("50.00"),
                currency="USD",
                description="Food expense",
                status="pending",
                category_id=1,
            ),
            ExpenseCreate(
                amount=Decimal("100.00"),
                currency="USD",
                description="Transport expense",
                status="approved",
                category_id=2,
            ),
            ExpenseCreate(
                amount=Decimal("75.00"),
                currency="USD",
                description="Entertainment expense",
                status="pending",
                category_id=3,
            ),
        ]

        created_expenses = []
        for i, exp_data in enumerate(expenses_data, 1):
            expense = Expense(
                id=i,
                amount=exp_data.amount,
                currency=exp_data.currency,
                description=exp_data.description,
                status=exp_data.status,
                user_id=1,
                category_id=exp_data.category_id,
            )
            created_expenses.append(expense)

        # Mock repository responses
        expense_service.expense_repo.create.side_effect = created_expenses

        # Create expenses
        for exp_data in expenses_data:
            result = expense_service.create_expense(exp_data, user_id=1)
            assert result.amount == exp_data.amount

        # Get all user expenses
        expense_service.expense_repo.get_user_expenses.return_value = created_expenses
        result = expense_service.get_user_expenses(user_id=1)
        assert len(result) == 3

        # Get expenses by status
        pending_expenses = [exp for exp in created_expenses if exp.status == "pending"]
        expense_service.expense_repo.get_by_status.return_value = pending_expenses
        result = expense_service.get_expenses_by_status(status="pending", user_id=1)
        assert len(result) == 2

        # Get expenses by category
        category_1_expenses = [exp for exp in created_expenses if exp.category_id == 1]
        expense_service.expense_repo.get_by_category.return_value = category_1_expenses
        result = expense_service.get_expenses_by_category(category_id=1, user_id=1)
        assert len(result) == 1

        # Get expenses by amount range
        amount_range_expenses = [
            exp
            for exp in created_expenses
            if Decimal("40.00") <= exp.amount <= Decimal("80.00")
        ]
        expense_service.expense_repo.get_by_amount_range.return_value = (
            amount_range_expenses
        )
        result = expense_service.get_expenses_by_amount_range(
            min_amount=Decimal("40.00"), max_amount=Decimal("80.00"), user_id=1
        )
        assert len(result) == 2

        # Update one expense
        update_data = ExpenseUpdate(status="approved")
        expense_service.expense_repo.get_by_id.return_value = created_expenses[0]
        expense_service.expense_repo.update.return_value = created_expenses[0]

        result = expense_service.update_expense(1, update_data, user_id=1)
        assert result == created_expenses[0]

        # Delete one expense
        expense_service.expense_repo.delete.return_value = True
        result = expense_service.delete_expense(1, user_id=1)
        assert result is True
