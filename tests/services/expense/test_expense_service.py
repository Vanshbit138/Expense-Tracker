"""
Tests for expense service module.
"""

from datetime import date
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.expense.expense import Expense
from src.schemas.expense.expense import ExpenseCreate, ExpenseUpdate
from src.schemas.expense.expense_queries import ExpenseFilter
from src.services.expense.expense_service import ExpenseService


class TestExpenseService:
    """Test cases for ExpenseService."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = Mock(spec=Session)
        return session

    @pytest.fixture
    def mock_expense_repo(self):
        """Create a mock expense repository."""
        repo = Mock()
        return repo

    @pytest.fixture
    def expense_service(self, mock_db_session, mock_expense_repo):
        """Create an ExpenseService instance for testing."""
        with patch(
            "src.services.expense.expense_service.ExpenseRepository",
            return_value=mock_expense_repo,
        ):
            service = ExpenseService(mock_db_session)
            service.expense_repo = mock_expense_repo
            return service

    @pytest.fixture
    def sample_expense_data(self):
        """Create sample expense data for testing."""
        return ExpenseCreate(
            amount=100.50,
            currency="USD",
            description="Test expense",
            category_id=1,
            expense_date=date(2024, 1, 15),
            status="pending",
            is_recurring=False,
            recurring_frequency=None,
        )

    @pytest.fixture
    def sample_expense(self):
        """Create a sample expense model instance."""
        expense = Mock(spec=Expense)
        expense.id = 1
        expense.amount = 100.50
        expense.currency = "USD"
        expense.description = "Test expense"
        expense.category_id = 1
        expense.user_id = 1
        expense.expense_date = date(2024, 1, 15)
        expense.status = "pending"
        expense.is_recurring = False
        expense.recurring_frequency = None
        return expense

    def test_expense_service_initialization(self, mock_db_session):
        """Test ExpenseService initialization."""
        with patch(
            "src.services.expense.expense_service.ExpenseRepository"
        ) as mock_repo_class:
            service = ExpenseService(mock_db_session)
            assert service.db == mock_db_session
            mock_repo_class.assert_called_once_with(mock_db_session)

    def test_create_expense_success(
        self, expense_service, sample_expense_data, sample_expense
    ):
        """Test successful expense creation."""
        # Mock category validation
        with patch.object(expense_service, "_validate_category_access"):
            expense_service.expense_repo.create.return_value = sample_expense

            result = expense_service.create_expense(sample_expense_data, user_id=1)

            expense_service.expense_repo.create.assert_called_once()
            assert result == sample_expense

    def test_create_expense_category_validation_failure(
        self, expense_service, sample_expense_data
    ):
        """Test expense creation with category validation failure."""
        with patch.object(
            expense_service, "_validate_category_access"
        ) as mock_validate:
            mock_validate.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

            with pytest.raises(HTTPException) as exc_info:
                expense_service.create_expense(sample_expense_data, user_id=1)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            expense_service.expense_repo.create.assert_not_called()

    def test_create_expense_repository_exception(
        self, expense_service, sample_expense_data
    ):
        """Test expense creation with repository exception."""
        with patch.object(expense_service, "_validate_category_access"):
            expense_service.expense_repo.create.side_effect = Exception(
                "Database error"
            )

            with pytest.raises(HTTPException) as exc_info:
                expense_service.create_expense(sample_expense_data, user_id=1)

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert exc_info.value.detail == "Failed to create expense"

    def test_get_expense_by_id_success(self, expense_service, sample_expense):
        """Test successful get expense by ID."""
        expense_service.expense_repo.get_by_id.return_value = sample_expense

        result = expense_service.get_expense_by_id(expense_id=1, user_id=1)

        expense_service.expense_repo.get_by_id.assert_called_once_with(1, 1)
        assert result == sample_expense

    def test_get_expense_by_id_not_found(self, expense_service):
        """Test get expense by ID when not found."""
        expense_service.expense_repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            expense_service.get_expense_by_id(expense_id=999, user_id=1)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Expense not found"

    def test_get_user_expenses(self, expense_service, sample_expense):
        """Test get user expenses."""
        expense_service.expense_repo.get_user_expenses.return_value = [sample_expense]

        result = expense_service.get_user_expenses(user_id=1, skip=0, limit=10)

        expense_service.expense_repo.get_user_expenses.assert_called_once_with(
            1, skip=0, limit=10
        )
        assert result == [sample_expense]

    def test_update_expense_success(self, expense_service, sample_expense):
        """Test successful expense update."""
        update_data = ExpenseUpdate(amount=150.75, description="Updated expense")
        updated_expense = Mock(spec=Expense)
        updated_expense.id = 1

        expense_service.expense_repo.get_by_id.return_value = sample_expense
        expense_service.expense_repo.update.return_value = updated_expense

        with patch.object(expense_service, "_validate_category_access"):
            result = expense_service.update_expense(
                expense_id=1, expense_data=update_data, user_id=1
            )

        assert result == updated_expense
        assert sample_expense.amount == 150.75
        assert sample_expense.description == "Updated expense"

    def test_update_expense_not_found(self, expense_service):
        """Test update expense when not found."""
        update_data = ExpenseUpdate(amount=150.75)
        expense_service.expense_repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            expense_service.update_expense(
                expense_id=999, expense_data=update_data, user_id=1
            )

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert exc_info.value.detail == "Expense not found"

    def test_update_expense_category_validation_failure(
        self, expense_service, sample_expense
    ):
        """Test update expense with category validation failure."""
        update_data = ExpenseUpdate(category_id=999)
        expense_service.expense_repo.get_by_id.return_value = sample_expense

        with patch.object(
            expense_service, "_validate_category_access"
        ) as mock_validate:
            mock_validate.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

            with pytest.raises(HTTPException) as exc_info:
                expense_service.update_expense(
                    expense_id=1, expense_data=update_data, user_id=1
                )

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    def test_update_expense_repository_exception(self, expense_service, sample_expense):
        """Test update expense with repository exception."""
        update_data = ExpenseUpdate(amount=150.75)
        expense_service.expense_repo.get_by_id.return_value = sample_expense
        expense_service.expense_repo.update.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc_info:
            expense_service.update_expense(
                expense_id=1, expense_data=update_data, user_id=1
            )

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Failed to update expense"

    def test_update_expense_partial_fields(self, expense_service, sample_expense):
        """Test update expense with partial fields."""
        update_data = ExpenseUpdate(amount=200.00)  # Only amount, other fields None
        updated_expense = Mock(spec=Expense)
        updated_expense.id = 1

        expense_service.expense_repo.get_by_id.return_value = sample_expense
        expense_service.expense_repo.update.return_value = updated_expense

        result = expense_service.update_expense(
            expense_id=1, expense_data=update_data, user_id=1
        )

        assert result == updated_expense
        assert sample_expense.amount == 200.00
        # Other fields should remain unchanged
        assert sample_expense.description == "Test expense"

    def test_delete_expense_success(self, expense_service):
        """Test successful expense deletion."""
        expense_service.expense_repo.delete.return_value = True

        result = expense_service.delete_expense(expense_id=1, user_id=1)

        expense_service.expense_repo.delete.assert_called_once_with(1, 1)
        assert result is True

    def test_delete_expense_failure(self, expense_service):
        """Test expense deletion failure."""
        expense_service.expense_repo.delete.return_value = False

        result = expense_service.delete_expense(expense_id=999, user_id=1)

        assert result is False

    def test_delete_expense_repository_exception(self, expense_service):
        """Test delete expense with repository exception."""
        expense_service.expense_repo.delete.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc_info:
            expense_service.delete_expense(expense_id=1, user_id=1)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Failed to delete expense"

    def test_delete_expense_http_exception(self, expense_service):
        """Test delete expense with HTTPException (should be re-raised)."""
        expense_service.expense_repo.delete.side_effect = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

        with pytest.raises(HTTPException) as exc_info:
            expense_service.delete_expense(expense_id=1, user_id=1)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Access denied"

    def test_get_all_expenses_success(self, expense_service, sample_expense):
        """Test successful get all expenses."""
        query = ExpenseFilter(skip=0, limit=10)
        expense_service.expense_repo.get_all.return_value = [sample_expense]

        result = expense_service.get_all_expenses(query)

        expense_service.expense_repo.get_all.assert_called_once_with(skip=0, limit=10)
        assert result == [sample_expense]

    def test_get_all_expenses_repository_exception(self, expense_service):
        """Test get all expenses with repository exception."""
        query = ExpenseFilter(skip=0, limit=10)
        expense_service.expense_repo.get_all.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc_info:
            expense_service.get_all_expenses(query)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Failed to retrieve expenses"

    def test_get_expense_stats_success(self, expense_service):
        """Test successful get expense stats."""
        stats_data = {"total_amount": 1000.00, "count": 5}
        expense_service.expense_repo.get_expense_stats.return_value = stats_data

        result = expense_service.get_expense_stats(
            user_id=1,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            currency="USD",
        )

        expense_service.expense_repo.get_expense_stats.assert_called_once_with(
            1, start_date=date(2024, 1, 1), end_date=date(2024, 1, 31), currency="USD"
        )
        assert result == stats_data

    def test_get_expense_stats_repository_exception(self, expense_service):
        """Test get expense stats with repository exception."""
        expense_service.expense_repo.get_expense_stats.side_effect = Exception(
            "Database error"
        )

        with pytest.raises(Exception) as exc_info:
            expense_service.get_expense_stats(user_id=1)

        assert str(exc_info.value) == "Database error"

    def test_get_category_stats_success(self, expense_service):
        """Test successful get category stats."""
        stats_data = [
            {"category": "Food", "amount": 500.00},
            {"category": "Transport", "amount": 300.00},
        ]
        expense_service.expense_repo.get_category_stats.return_value = stats_data

        result = expense_service.get_category_stats(
            user_id=1, start_date=date(2024, 1, 1), end_date=date(2024, 1, 31)
        )

        expense_service.expense_repo.get_category_stats.assert_called_once_with(
            1, start_date=date(2024, 1, 1), end_date=date(2024, 1, 31)
        )
        assert result == stats_data

    def test_get_category_stats_repository_exception(self, expense_service):
        """Test get category stats with repository exception."""
        expense_service.expense_repo.get_category_stats.side_effect = Exception(
            "Database error"
        )

        with pytest.raises(Exception) as exc_info:
            expense_service.get_category_stats(user_id=1)

        assert str(exc_info.value) == "Database error"

    def test_get_monthly_expenses_success(self, expense_service, sample_expense):
        """Test successful get monthly expenses."""
        expense_service.expense_repo.get_monthly_expenses.return_value = [
            sample_expense
        ]

        result = expense_service.get_monthly_expenses(user_id=1, year=2024, month=1)

        expense_service.expense_repo.get_monthly_expenses.assert_called_once_with(
            1, year=2024, month=1
        )
        assert result == [sample_expense]

    def test_get_monthly_expenses_repository_exception(self, expense_service):
        """Test get monthly expenses with repository exception."""
        expense_service.expense_repo.get_monthly_expenses.side_effect = Exception(
            "Database error"
        )

        with pytest.raises(Exception) as exc_info:
            expense_service.get_monthly_expenses(user_id=1, year=2024, month=1)

        assert str(exc_info.value) == "Database error"

    def test_get_monthly_analytics_success(self, expense_service, sample_expense):
        """Test successful get monthly analytics."""
        expense_service.expense_repo.get_monthly_expenses.return_value = [
            sample_expense
        ]

        result = expense_service.get_monthly_analytics(user_id=1, year=2024, month=1)

        expense_service.expense_repo.get_monthly_expenses.assert_called_once_with(
            1, year=2024, month=1
        )
        assert result == [sample_expense]

    def test_get_monthly_analytics_repository_exception(self, expense_service):
        """Test get monthly analytics with repository exception."""
        expense_service.expense_repo.get_monthly_expenses.side_effect = Exception(
            "Database error"
        )

        with pytest.raises(Exception) as exc_info:
            expense_service.get_monthly_analytics(user_id=1, year=2024, month=1)

        assert str(exc_info.value) == "Database error"

    def test_validate_category_access_success(self, expense_service, mock_db_session):
        """Test successful category access validation."""
        mock_category = Mock()
        mock_category.user_id = 1

        with patch(
            "src.repositories.category.category_repository.CategoryRepository"
        ) as mock_cat_repo_class:
            mock_cat_repo = Mock()
            mock_cat_repo_class.return_value = mock_cat_repo
            mock_cat_repo.get_by_id.return_value = mock_category

            # Should not raise exception
            expense_service._validate_category_access(category_id=1, user_id=1)

            mock_cat_repo.get_by_id.assert_called_once_with(1)

    def test_validate_category_access_category_not_found(
        self, expense_service, mock_db_session
    ):
        """Test category access validation when category not found."""
        with patch(
            "src.repositories.category.category_repository.CategoryRepository"
        ) as mock_cat_repo_class:
            mock_cat_repo = Mock()
            mock_cat_repo_class.return_value = mock_cat_repo
            mock_cat_repo.get_by_id.return_value = None

            with pytest.raises(HTTPException) as exc_info:
                expense_service._validate_category_access(category_id=999, user_id=1)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert exc_info.value.detail == "Category not found"

    def test_validate_category_access_wrong_user(
        self, expense_service, mock_db_session
    ):
        """Test category access validation when user doesn't own category."""
        mock_category = Mock()
        mock_category.user_id = 2  # Different user

        with patch(
            "src.repositories.category.category_repository.CategoryRepository"
        ) as mock_cat_repo_class:
            mock_cat_repo = Mock()
            mock_cat_repo_class.return_value = mock_cat_repo
            mock_cat_repo.get_by_id.return_value = mock_category

            with pytest.raises(HTTPException) as exc_info:
                expense_service._validate_category_access(category_id=1, user_id=1)

            assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
            assert exc_info.value.detail == "Access denied to category"

    def test_update_expense_all_fields(self, expense_service, sample_expense):
        """Test update expense with all fields provided."""
        update_data = ExpenseUpdate(
            amount=200.00,
            currency="EUR",
            description="Updated description",
            category_id=2,
            expense_date=date(2024, 2, 1),
            status="rejected",
            is_recurring=True,
            recurring_frequency="monthly",
        )
        updated_expense = Mock(spec=Expense)
        updated_expense.id = 1

        expense_service.expense_repo.get_by_id.return_value = sample_expense
        expense_service.expense_repo.update.return_value = updated_expense

        with patch.object(expense_service, "_validate_category_access"):
            result = expense_service.update_expense(
                expense_id=1, expense_data=update_data, user_id=1
            )

        assert result == updated_expense
        assert sample_expense.amount == 200.00
        assert sample_expense.currency == "EUR"
        assert sample_expense.description == "Updated description"
        assert sample_expense.category_id == 2
        assert sample_expense.expense_date == date(2024, 2, 1)
        assert sample_expense.status == "rejected"
        assert sample_expense.is_recurring is True
        assert sample_expense.recurring_frequency == "monthly"

    def test_update_expense_none_fields(self, expense_service, sample_expense):
        """Test update expense with None fields (should not update)."""
        update_data = ExpenseUpdate()  # All fields None
        updated_expense = Mock(spec=Expense)
        updated_expense.id = 1

        expense_service.expense_repo.get_by_id.return_value = sample_expense
        expense_service.expense_repo.update.return_value = updated_expense

        result = expense_service.update_expense(
            expense_id=1, expense_data=update_data, user_id=1
        )

        assert result == updated_expense
        # Original values should remain unchanged
        assert sample_expense.amount == 100.50
        assert sample_expense.description == "Test expense"
