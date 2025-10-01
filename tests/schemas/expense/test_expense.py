"""
Tests for expense schemas.
"""

from datetime import date, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas.expense.expense import (
    Expense,
    ExpenseBase,
    ExpenseCreate,
    ExpenseInDB,
    ExpenseUpdate,
)


class TestExpenseBase:
    """Test cases for ExpenseBase schema."""

    def test_expense_base_valid_data(self):
        """Test ExpenseBase with valid data."""
        expense_data = {
            "amount": Decimal("100.50"),
            "currency": "USD",
            "description": "Test expense",
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
            "status": "pending",
            "is_recurring": False,
            "recurring_frequency": None,
        }

        expense = ExpenseBase(**expense_data)

        assert expense.amount == Decimal("100.50")
        assert expense.currency == "USD"
        assert expense.description == "Test expense"
        assert expense.category_id == 1
        assert expense.expense_date == date(2024, 1, 15)
        assert expense.status == "pending"
        assert expense.is_recurring is False
        assert expense.recurring_frequency is None

    def test_expense_base_minimal_data(self):
        """Test ExpenseBase with minimal required data."""
        expense_data = {
            "amount": Decimal("50.00"),
            "description": "Test expense",
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
        }

        expense = ExpenseBase(**expense_data)

        assert expense.amount == Decimal("50.00")
        assert expense.currency == "USD"  # Default value
        assert expense.description == "Test expense"
        assert expense.category_id == 1
        assert expense.expense_date == date(2024, 1, 15)
        assert expense.status == "pending"  # Default value
        assert expense.is_recurring is False  # Default value
        assert expense.recurring_frequency is None  # Default value

    def test_expense_base_amount_required(self):
        """Test ExpenseBase amount is required."""
        expense_data = {
            "description": "Test expense",
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
        }

        with pytest.raises(ValidationError) as exc_info:
            ExpenseBase(**expense_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "missing" for error in errors)
        assert any(error["loc"] == ("amount",) for error in errors)

    def test_expense_base_amount_positive(self):
        """Test ExpenseBase amount must be positive."""
        expense_data = {
            "amount": Decimal("-10.00"),
            "description": "Test expense",
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
        }

        with pytest.raises(ValidationError) as exc_info:
            ExpenseBase(**expense_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)

    def test_expense_base_currency_validation(self):
        """Test ExpenseBase currency validation."""
        expense_data = {
            "amount": Decimal("100.00"),
            "currency": "INVALID",
            "description": "Test expense",
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
        }

        with pytest.raises(ValidationError) as exc_info:
            ExpenseBase(**expense_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)

    def test_expense_base_status_validation(self):
        """Test ExpenseBase status validation."""
        expense_data = {
            "amount": Decimal("100.00"),
            "status": "invalid_status",
            "description": "Test expense",
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
        }

        with pytest.raises(ValidationError) as exc_info:
            ExpenseBase(**expense_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "literal_error" for error in errors)

    def test_expense_base_recurring_frequency_validation(self):
        """Test ExpenseBase recurring frequency validation."""
        expense_data = {
            "amount": Decimal("100.00"),
            "recurring_frequency": "invalid_frequency",
            "description": "Test expense",
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
        }

        with pytest.raises(ValidationError) as exc_info:
            ExpenseBase(**expense_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "literal_error" for error in errors)

    def test_expense_base_recurring_consistency(self):
        """Test ExpenseBase recurring consistency validation."""
        expense_data = {
            "amount": Decimal("100.00"),
            "is_recurring": True,
            "recurring_frequency": "monthly",
            "description": "Test expense",
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
        }

        expense = ExpenseBase(**expense_data)
        assert expense.is_recurring is True
        assert expense.recurring_frequency == "monthly"

    def test_expense_base_decimal_precision(self):
        """Test ExpenseBase decimal precision handling."""
        expense_data = {
            "amount": Decimal("0.01"),
            "description": "Test expense",
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
        }

        expense = ExpenseBase(**expense_data)
        assert expense.amount == Decimal("0.01")

    def test_expense_base_description_required(self):
        """Test ExpenseBase description is required."""
        expense_data = {
            "amount": Decimal("100.00"),
            "description": None,
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
        }

        with pytest.raises(ValidationError) as exc_info:
            ExpenseBase(**expense_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "string_type" for error in errors)

    def test_expense_base_long_description(self):
        """Test ExpenseBase with long description."""
        long_description = "A" * 1000
        expense_data = {
            "amount": Decimal("100.00"),
            "description": long_description,
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
        }

        with pytest.raises(ValidationError) as exc_info:
            ExpenseBase(**expense_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)

    def test_expense_base_category_id_validation(self):
        """Test ExpenseBase category_id validation."""
        expense_data = {
            "amount": Decimal("100.00"),
            "description": "Test expense",
            "category_id": 0,  # Invalid - must be positive
            "expense_date": date(2024, 1, 15),
        }

        with pytest.raises(ValidationError) as exc_info:
            ExpenseBase(**expense_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)

    def test_expense_base_amount_maximum(self):
        """Test ExpenseBase amount maximum validation."""
        expense_data = {
            "amount": Decimal("1000000.00"),  # Too large
            "description": "Test expense",
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
        }

        with pytest.raises(ValidationError) as exc_info:
            ExpenseBase(**expense_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "value_error" for error in errors)


class TestExpenseCreate:
    """Test cases for ExpenseCreate schema."""

    def test_expense_create_valid_data(self):
        """Test ExpenseCreate with valid data."""
        expense_data = {
            "amount": Decimal("100.50"),
            "currency": "USD",
            "description": "Test expense",
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
            "status": "pending",
            "is_recurring": False,
            "recurring_frequency": None,
        }

        expense = ExpenseCreate(**expense_data)

        assert expense.amount == Decimal("100.50")
        assert expense.currency == "USD"
        assert expense.description == "Test expense"
        assert expense.category_id == 1
        assert expense.expense_date == date(2024, 1, 15)
        assert expense.status == "pending"
        assert expense.is_recurring is False
        assert expense.recurring_frequency is None

    def test_expense_create_minimal_data(self):
        """Test ExpenseCreate with minimal required data."""
        expense_data = {
            "amount": Decimal("50.00"),
            "description": "Test expense",
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
        }

        expense = ExpenseCreate(**expense_data)

        assert expense.amount == Decimal("50.00")
        assert expense.currency == "USD"  # Default value
        assert expense.description == "Test expense"
        assert expense.category_id == 1
        assert expense.expense_date == date(2024, 1, 15)
        assert expense.status == "pending"  # Default value
        assert expense.is_recurring is False  # Default value
        assert expense.recurring_frequency is None  # Default value

    def test_expense_create_category_id_required(self):
        """Test ExpenseCreate category_id is required."""
        expense_data = {
            "amount": Decimal("50.00"),
            "description": "Test expense",
            "expense_date": date(2024, 1, 15),
        }

        with pytest.raises(ValidationError) as exc_info:
            ExpenseCreate(**expense_data)

        errors = exc_info.value.errors()
        assert any(error["type"] == "missing" for error in errors)
        assert any(error["loc"] == ("category_id",) for error in errors)

    def test_expense_create_inherits_expense_base(self):
        """Test that ExpenseCreate inherits ExpenseBase validation."""
        expense_data = {
            "amount": Decimal("-10.00"),  # Invalid - negative amount
            "description": "Test expense",
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
        }

        with pytest.raises(ValidationError):
            ExpenseCreate(**expense_data)


class TestExpenseUpdate:
    """Test cases for ExpenseUpdate schema."""

    def test_expense_update_all_fields(self):
        """Test ExpenseUpdate with all fields."""
        expense_data = {
            "amount": Decimal("200.00"),
            "currency": "EUR",
            "description": "Updated expense",
            "category_id": 2,
            "expense_date": date(2024, 2, 15),
            "status": "approved",
            "is_recurring": True,
            "recurring_frequency": "monthly",
        }

        expense = ExpenseUpdate(**expense_data)

        assert expense.amount == Decimal("200.00")
        assert expense.currency == "EUR"
        assert expense.description == "Updated expense"
        assert expense.category_id == 2
        assert expense.expense_date == date(2024, 2, 15)
        assert expense.status == "approved"
        assert expense.is_recurring is True
        assert expense.recurring_frequency == "monthly"

    def test_expense_update_partial_fields(self):
        """Test ExpenseUpdate with partial fields."""
        expense_data = {
            "amount": Decimal("150.00"),
            "description": "Updated description",
        }

        expense = ExpenseUpdate(**expense_data)

        assert expense.amount == Decimal("150.00")
        assert expense.description == "Updated description"
        assert expense.currency is None
        assert expense.category_id is None
        assert expense.expense_date is None
        assert expense.status is None
        assert expense.is_recurring is None
        assert expense.recurring_frequency is None

    def test_expense_update_empty(self):
        """Test ExpenseUpdate with no fields."""
        expense_data = {}

        expense = ExpenseUpdate(**expense_data)

        assert expense.amount is None
        assert expense.currency is None
        assert expense.description is None
        assert expense.category_id is None
        assert expense.expense_date is None
        assert expense.status is None
        assert expense.is_recurring is None
        assert expense.recurring_frequency is None

    def test_expense_update_inherits_expense_base(self):
        """Test that ExpenseUpdate inherits ExpenseBase validation."""
        expense_data = {"amount": Decimal("-10.00")}  # Invalid - negative amount

        with pytest.raises(ValidationError):
            ExpenseUpdate(**expense_data)


class TestExpenseInDB:
    """Test cases for ExpenseInDB schema."""

    def test_expense_in_db_valid_data(self):
        """Test ExpenseInDB with valid data."""
        expense_data = {
            "id": 1,
            "amount": Decimal("100.50"),
            "currency": "USD",
            "description": "Test expense",
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
            "status": "pending",
            "is_recurring": False,
            "recurring_frequency": None,
            "user_id": 1,
            "created_at": datetime(2024, 1, 15, 10, 30, 0),
            "updated_at": datetime(2024, 1, 15, 10, 30, 0),
        }

        expense = ExpenseInDB(**expense_data)

        assert expense.id == 1
        assert expense.amount == Decimal("100.50")
        assert expense.currency == "USD"
        assert expense.description == "Test expense"
        assert expense.category_id == 1
        assert expense.expense_date == date(2024, 1, 15)
        assert expense.status == "pending"
        assert expense.is_recurring is False
        assert expense.recurring_frequency is None
        assert expense.user_id == 1
        assert expense.created_at == datetime(2024, 1, 15, 10, 30, 0)
        assert expense.updated_at == datetime(2024, 1, 15, 10, 30, 0)

    def test_expense_in_db_recurring_expense(self):
        """Test ExpenseInDB with recurring expense."""
        expense_data = {
            "id": 2,
            "amount": Decimal("200.00"),
            "currency": "USD",
            "description": "Recurring expense",
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
            "status": "approved",
            "is_recurring": True,
            "recurring_frequency": "monthly",
            "user_id": 1,
            "created_at": datetime(2024, 1, 15, 10, 30, 0),
            "updated_at": datetime(2024, 1, 15, 10, 30, 0),
        }

        expense = ExpenseInDB(**expense_data)

        assert expense.is_recurring is True
        assert expense.recurring_frequency == "monthly"

    def test_expense_in_db_inherits_expense_base(self):
        """Test that ExpenseInDB inherits ExpenseBase validation."""
        expense_data = {
            "id": 1,
            "amount": Decimal("-10.00"),  # Invalid - negative amount
            "description": "Test expense",
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
            "user_id": 1,
            "created_at": datetime(2024, 1, 15, 10, 30, 0),
            "updated_at": datetime(2024, 1, 15, 10, 30, 0),
        }

        with pytest.raises(ValidationError):
            ExpenseInDB(**expense_data)


class TestExpense:
    """Test cases for Expense schema."""

    def test_expense_valid_data(self):
        """Test Expense with valid data."""
        expense_data = {
            "id": 1,
            "amount": Decimal("100.50"),
            "currency": "USD",
            "description": "Test expense",
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
            "status": "pending",
            "is_recurring": False,
            "recurring_frequency": None,
            "user_id": 1,
            "created_at": datetime(2024, 1, 15, 10, 30, 0),
            "updated_at": datetime(2024, 1, 15, 10, 30, 0),
        }

        expense = Expense(**expense_data)

        assert expense.id == 1
        assert expense.amount == Decimal("100.50")
        assert expense.currency == "USD"
        assert expense.description == "Test expense"
        assert expense.category_id == 1
        assert expense.expense_date == date(2024, 1, 15)
        assert expense.status == "pending"
        assert expense.is_recurring is False
        assert expense.recurring_frequency is None
        assert expense.user_id == 1
        assert expense.created_at == datetime(2024, 1, 15, 10, 30, 0)
        assert expense.updated_at == datetime(2024, 1, 15, 10, 30, 0)

    def test_expense_inherits_expense_base(self):
        """Test that Expense inherits ExpenseBase validation."""
        expense_data = {
            "id": 1,
            "amount": Decimal("-10.00"),  # Invalid - negative amount
            "description": "Test expense",
            "category_id": 1,
            "expense_date": date(2024, 1, 15),
            "user_id": 1,
            "created_at": datetime(2024, 1, 15, 10, 30, 0),
            "updated_at": datetime(2024, 1, 15, 10, 30, 0),
        }

        with pytest.raises(ValidationError):
            Expense(**expense_data)

    def test_expense_from_attributes_config(self):
        """Test Expense from_attributes configuration."""

        # This tests the Config.from_attributes = True setting
        class MockExpense:
            def __init__(self):
                self.id = 1
                self.amount = Decimal("100.50")
                self.currency = "USD"
                self.description = "Test expense"
                self.category_id = 1
                self.expense_date = date(2024, 1, 15)
                self.status = "pending"
                self.is_recurring = False
                self.recurring_frequency = None
                self.user_id = 1
                self.created_at = datetime(2024, 1, 15, 10, 30, 0)
                self.updated_at = datetime(2024, 1, 15, 10, 30, 0)

        mock_expense = MockExpense()
        expense = Expense.model_validate(mock_expense)

        assert expense.id == 1
        assert expense.amount == Decimal("100.50")
        assert expense.currency == "USD"
        assert expense.description == "Test expense"
        assert expense.category_id == 1
        assert expense.expense_date == date(2024, 1, 15)
        assert expense.status == "pending"
        assert expense.is_recurring is False
        assert expense.recurring_frequency is None
        assert expense.user_id == 1
        assert expense.created_at == datetime(2024, 1, 15, 10, 30, 0)
        assert expense.updated_at == datetime(2024, 1, 15, 10, 30, 0)
