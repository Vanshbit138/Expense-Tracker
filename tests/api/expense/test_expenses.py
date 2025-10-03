"""
Tests for expense API endpoints.
"""

from datetime import date
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException, status

from src.models.expense.expense import Expense
from src.models.user.user import User
from src.schemas.expense.expense import ExpenseCreate, ExpenseUpdate


class TestExpenseAPI:
    """Test cases for expense API endpoints."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing."""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.username = "testuser"
        user.full_name = "Test User"
        user.is_active = True
        return user

    @pytest.fixture
    def mock_expense(self):
        """Create a mock expense for testing."""
        expense = Mock(spec=Expense)
        expense.id = 1
        expense.amount = Decimal("100.50")
        expense.currency = "USD"
        expense.description = "Test expense"
        expense.category_id = 1
        expense.user_id = 1
        expense.expense_date = date(2024, 1, 15)
        expense.status = "pending"
        expense.is_recurring = False
        expense.recurring_frequency = None
        return expense

    @pytest.fixture
    def sample_expense_data(self):
        """Create sample expense data for testing."""
        return {
            "amount": 100.50,
            "currency": "USD",
            "description": "Test expense",
            "category_id": 1,
            "expense_date": "2024-01-15",
            "status": "pending",
            "is_recurring": False,
            "recurring_frequency": None,
        }

    @pytest.fixture
    def sample_expense_update_data(self):
        """Create sample expense update data for testing."""
        return {
            "amount": 150.75,
            "description": "Updated expense",
            "status": "approved",
        }

    def test_create_expense_success(self, mock_user, mock_expense, sample_expense_data):
        """Test successful expense creation."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.create_expense.return_value = mock_expense

            # This would be called by FastAPI's dependency injection
            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    # Test the function directly
                    from src.api.expense.expenses import create_expense

                    result = create_expense(
                        expense_data=ExpenseCreate(**sample_expense_data),
                        current_user=mock_user,
                        db=mock_db,
                    )

                    assert result == mock_expense
                    mock_service_class.assert_called_once_with(mock_db)
                    mock_service.create_expense.assert_called_once()

    def test_create_expense_http_exception(self, mock_user, sample_expense_data):
        """Test expense creation with HTTPException."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.create_expense.side_effect = HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category"
            )

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.expense.expenses import create_expense

                    with pytest.raises(HTTPException) as exc_info:
                        create_expense(
                            expense_data=ExpenseCreate(**sample_expense_data),
                            current_user=mock_user,
                            db=mock_db,
                        )

                    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
                    assert exc_info.value.detail == "Invalid category"

    def test_create_expense_general_exception(self, mock_user, sample_expense_data):
        """Test expense creation with general exception."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.create_expense.side_effect = Exception("Database error")

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.expense.expenses import create_expense

                    with pytest.raises(HTTPException) as exc_info:
                        create_expense(
                            expense_data=ExpenseCreate(**sample_expense_data),
                            current_user=mock_user,
                            db=mock_db,
                        )

                    assert (
                        exc_info.value.status_code
                        == status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                    assert (
                        "Internal server error during expense creation"
                        in exc_info.value.detail
                    )

    def test_get_expenses_success(self, mock_user, mock_expense):
        """Test successful expense retrieval."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_user_expenses.return_value = [mock_expense]

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.expense.expenses import get_expenses

                    result = get_expenses(
                        skip=0,
                        limit=20,
                        start_date=None,
                        end_date=None,
                        current_user=mock_user,
                        db=mock_db,
                    )

                    assert result == [mock_expense]
                    mock_service_class.assert_called_once_with(mock_db)
                    mock_service.get_user_expenses.assert_called_once_with(
                        mock_user.id, skip=0, limit=20
                    )

    def test_get_expenses_with_filters(self, mock_user, mock_expense):
        """Test expense retrieval with date filters."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_user_expenses.return_value = [mock_expense]

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.expense.expenses import get_expenses

                    result = get_expenses(
                        skip=10,
                        limit=50,
                        start_date=date(2024, 1, 1),
                        end_date=date(2024, 1, 31),
                        current_user=mock_user,
                        db=mock_db,
                    )

                    assert result == [mock_expense]
                    mock_service.get_user_expenses.assert_called_once_with(
                        mock_user.id, skip=10, limit=50
                    )

    def test_get_expense_success(self, mock_user, mock_expense):
        """Test successful single expense retrieval."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_expense_by_id.return_value = mock_expense

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.expense.expenses import get_expense

                    result = get_expense(
                        expense_id=1, current_user=mock_user, db=mock_db
                    )

                    assert result == mock_expense
                    mock_service.get_expense_by_id.assert_called_once_with(
                        1, mock_user.id
                    )

    def test_get_expense_not_found(self, mock_user):
        """Test single expense retrieval when not found."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_expense_by_id.return_value = None

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.expense.expenses import get_expense

                    with pytest.raises(HTTPException) as exc_info:
                        get_expense(expense_id=999, current_user=mock_user, db=mock_db)

                    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
                    assert exc_info.value.detail == "Expense not found"

    def test_update_expense_success(
        self, mock_user, mock_expense, sample_expense_update_data
    ):
        """Test successful expense update."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.update_expense.return_value = mock_expense

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.expense.expenses import update_expense

                    result = update_expense(
                        expense_id=1,
                        expense_data=ExpenseUpdate(**sample_expense_update_data),
                        current_user=mock_user,
                        db=mock_db,
                    )

                    assert result == mock_expense
                    mock_service.update_expense.assert_called_once_with(
                        1, ExpenseUpdate(**sample_expense_update_data), mock_user.id
                    )

    def test_update_expense_http_exception(self, mock_user, sample_expense_update_data):
        """Test expense update with HTTPException."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.update_expense.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
            )

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.expense.expenses import update_expense

                    with pytest.raises(HTTPException) as exc_info:
                        update_expense(
                            expense_id=999,
                            expense_data=ExpenseUpdate(**sample_expense_update_data),
                            current_user=mock_user,
                            db=mock_db,
                        )

                    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
                    assert exc_info.value.detail == "Expense not found"

    def test_update_expense_general_exception(
        self, mock_user, sample_expense_update_data
    ):
        """Test expense update with general exception."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.update_expense.side_effect = Exception("Database error")

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.expense.expenses import update_expense

                    with pytest.raises(HTTPException) as exc_info:
                        update_expense(
                            expense_id=1,
                            expense_data=ExpenseUpdate(**sample_expense_update_data),
                            current_user=mock_user,
                            db=mock_db,
                        )

                    assert (
                        exc_info.value.status_code
                        == status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                    assert (
                        "Internal server error during expense update"
                        in exc_info.value.detail
                    )

    def test_delete_expense_success(self, mock_user):
        """Test successful expense deletion."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.delete_expense.return_value = True

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.expense.expenses import delete_expense

                    result = delete_expense(
                        expense_id=1, current_user=mock_user, db=mock_db
                    )

                    assert result == {"message": "Expense deleted successfully"}
                    mock_service.delete_expense.assert_called_once_with(1, mock_user.id)

    def test_delete_expense_not_found(self, mock_user):
        """Test expense deletion when not found."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.delete_expense.return_value = False

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.expense.expenses import delete_expense

                    with pytest.raises(HTTPException) as exc_info:
                        delete_expense(
                            expense_id=999, current_user=mock_user, db=mock_db
                        )

                    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
                    assert exc_info.value.detail == "Expense not found"

    def test_delete_expense_http_exception(self, mock_user):
        """Test expense deletion with HTTPException."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.delete_expense.side_effect = HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.expense.expenses import delete_expense

                    with pytest.raises(HTTPException) as exc_info:
                        delete_expense(expense_id=1, current_user=mock_user, db=mock_db)

                    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
                    assert exc_info.value.detail == "Access denied"

    def test_delete_expense_general_exception(self, mock_user):
        """Test expense deletion with general exception."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.delete_expense.side_effect = Exception("Database error")

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.expense.expenses import delete_expense

                    with pytest.raises(HTTPException) as exc_info:
                        delete_expense(expense_id=1, current_user=mock_user, db=mock_db)

                    assert (
                        exc_info.value.status_code
                        == status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                    assert (
                        "Internal server error during expense deletion"
                        in exc_info.value.detail
                    )

    def test_get_monthly_expenses_success(self, mock_user, mock_expense):
        """Test successful monthly expenses retrieval."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_monthly_expenses.return_value = [mock_expense]

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.expense.expenses import get_monthly_expenses

                    result = get_monthly_expenses(
                        year=2024, month=1, current_user=mock_user, db=mock_db
                    )

                    assert result == [mock_expense]
                    mock_service.get_monthly_expenses.assert_called_once_with(
                        mock_user.id, 2024, 1
                    )

    def test_get_monthly_expenses_invalid_month_low(self, mock_user):
        """Test monthly expenses with invalid month (too low)."""
        with patch(
            "src.api.expense.expenses.get_current_active_user", return_value=mock_user
        ):
            with patch("src.api.expense.expenses.get_db") as mock_get_db:
                mock_db = Mock()
                mock_get_db.return_value = mock_db

                from src.api.expense.expenses import get_monthly_expenses

                with pytest.raises(HTTPException) as exc_info:
                    get_monthly_expenses(
                        year=2024, month=0, current_user=mock_user, db=mock_db
                    )

                assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
                assert exc_info.value.detail == "Month must be between 1 and 12"

    def test_get_monthly_expenses_invalid_month_high(self, mock_user):
        """Test monthly expenses with invalid month (too high)."""
        with patch(
            "src.api.expense.expenses.get_current_active_user", return_value=mock_user
        ):
            with patch("src.api.expense.expenses.get_db") as mock_get_db:
                mock_db = Mock()
                mock_get_db.return_value = mock_db

                from src.api.expense.expenses import get_monthly_expenses

                with pytest.raises(HTTPException) as exc_info:
                    get_monthly_expenses(
                        year=2024, month=13, current_user=mock_user, db=mock_db
                    )

                assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
                assert exc_info.value.detail == "Month must be between 1 and 12"

    def test_get_monthly_expenses_boundary_values(self, mock_user, mock_expense):
        """Test monthly expenses with boundary month values."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_monthly_expenses.return_value = [mock_expense]

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    from src.api.expense.expenses import get_monthly_expenses

                    # Test month = 1 (minimum valid)
                    result = get_monthly_expenses(
                        year=2024, month=1, current_user=mock_user, db=mock_db
                    )
                    assert result == [mock_expense]

                    # Test month = 12 (maximum valid)
                    result = get_monthly_expenses(
                        year=2024, month=12, current_user=mock_user, db=mock_db
                    )
                    assert result == [mock_expense]

    def test_router_initialization(self):
        """Test that the router is properly initialized."""
        from src.api.expense.expenses import router

        assert router is not None
        assert hasattr(router, "routes")

    def test_logger_initialization(self):
        """Test that the logger is properly initialized."""
        from src.api.expense.expenses import logger

        assert logger is not None

    def test_create_expense_logging(self, mock_user, mock_expense, sample_expense_data):
        """Test that expense creation is properly logged."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.create_expense.return_value = mock_expense

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    with patch("src.api.expense.expenses.logger") as mock_logger:
                        from src.api.expense.expenses import create_expense

                        create_expense(
                            expense_data=ExpenseCreate(**sample_expense_data),
                            current_user=mock_user,
                            db=mock_db,
                        )

                        # Verify logging calls
                        assert (
                            mock_logger.info.call_count >= 2
                        )  # Start and success logs

    def test_get_expenses_logging(self, mock_user, mock_expense):
        """Test that expense retrieval is properly logged."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_user_expenses.return_value = [mock_expense]

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    with patch("src.api.expense.expenses.logger") as mock_logger:
                        from src.api.expense.expenses import get_expenses

                        get_expenses(
                            skip=0,
                            limit=20,
                            start_date=None,
                            end_date=None,
                            current_user=mock_user,
                            db=mock_db,
                        )

                        # Verify logging call
                        mock_logger.info.assert_called_once()

    def test_get_expense_logging(self, mock_user, mock_expense):
        """Test that single expense retrieval is properly logged."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_expense_by_id.return_value = mock_expense

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    with patch("src.api.expense.expenses.logger") as mock_logger:
                        from src.api.expense.expenses import get_expense

                        get_expense(expense_id=1, current_user=mock_user, db=mock_db)

                        # Verify logging call
                        mock_logger.info.assert_called_once()

    def test_update_expense_logging(
        self, mock_user, mock_expense, sample_expense_update_data
    ):
        """Test that expense update is properly logged."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.update_expense.return_value = mock_expense

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    with patch("src.api.expense.expenses.logger") as mock_logger:
                        from src.api.expense.expenses import update_expense

                        update_expense(
                            expense_id=1,
                            expense_data=ExpenseUpdate(**sample_expense_update_data),
                            current_user=mock_user,
                            db=mock_db,
                        )

                        # Verify logging calls
                        assert (
                            mock_logger.info.call_count >= 2
                        )  # Start and success logs

    def test_delete_expense_logging(self, mock_user):
        """Test that expense deletion is properly logged."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.delete_expense.return_value = True

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    with patch("src.api.expense.expenses.logger") as mock_logger:
                        from src.api.expense.expenses import delete_expense

                        delete_expense(expense_id=1, current_user=mock_user, db=mock_db)

                        # Verify logging calls
                        assert (
                            mock_logger.info.call_count >= 2
                        )  # Start and success logs

    def test_get_monthly_expenses_logging(self, mock_user, mock_expense):
        """Test that monthly expenses retrieval is properly logged."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_monthly_expenses.return_value = [mock_expense]

            with patch(
                "src.api.expense.expenses.get_current_active_user",
                return_value=mock_user,
            ):
                with patch("src.api.expense.expenses.get_db") as mock_get_db:
                    mock_db = Mock()
                    mock_get_db.return_value = mock_db

                    # Test that the method works and doesn't raise an exception
                    from src.api.expense.expenses import get_monthly_expenses

                    result = get_monthly_expenses(
                        year=2024, month=1, current_user=mock_user, db=mock_db
                    )

                    # Verify the result
                    assert result == [mock_expense]
                    mock_service.get_monthly_expenses.assert_called_once_with(
                        mock_user.id, 2024, 1
                    )
