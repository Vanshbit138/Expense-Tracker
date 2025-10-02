"""
Tests for the expense validation service.
"""

from datetime import date
from decimal import Decimal

from src.services.expense.expense_validation import ExpenseValidationService


class TestExpenseValidationService:
    """Test cases for expense validation service."""

    def test_validate_amount_valid(self):
        """Test amount validation with valid amounts."""
        assert ExpenseValidationService.validate_amount(Decimal("10.00")) is True
        assert ExpenseValidationService.validate_amount(Decimal("0.01")) is True
        assert ExpenseValidationService.validate_amount(Decimal("1000")) is True

    def test_validate_amount_invalid(self):
        """Test amount validation with invalid amounts."""
        assert ExpenseValidationService.validate_amount(Decimal("0")) is False
        assert ExpenseValidationService.validate_amount(Decimal("-10.00")) is False
        assert ExpenseValidationService.validate_amount(Decimal("-0.01")) is False

    def test_validate_date_range_valid(self):
        """Test date range validation with valid ranges."""
        start = date(2024, 1, 1)
        end = date(2024, 12, 31)
        assert ExpenseValidationService.validate_date_range(start, end) is True
        assert ExpenseValidationService.validate_date_range(start, start) is True
        assert ExpenseValidationService.validate_date_range(None, None) is True
        assert ExpenseValidationService.validate_date_range(start, None) is True
        assert ExpenseValidationService.validate_date_range(None, end) is True

    def test_validate_date_range_invalid(self):
        """Test date range validation with invalid ranges."""
        start = date(2024, 12, 31)
        end = date(2024, 1, 1)
        assert ExpenseValidationService.validate_date_range(start, end) is False

    def test_validate_currency_valid(self):
        """Test currency validation with valid codes."""
        assert ExpenseValidationService.validate_currency("USD") is True
        assert ExpenseValidationService.validate_currency("EUR") is True
        assert ExpenseValidationService.validate_currency("GBP") is True
        assert ExpenseValidationService.validate_currency("JPY") is True

    def test_validate_currency_invalid(self):
        """Test currency validation with invalid codes."""
        assert ExpenseValidationService.validate_currency("US") is False  # Too short
        assert ExpenseValidationService.validate_currency("USDD") is False  # Too long
        assert ExpenseValidationService.validate_currency("US1") is False  # Has number
        assert ExpenseValidationService.validate_currency("12") is False
        assert ExpenseValidationService.validate_currency("") is False

    def test_validate_status_valid(self):
        """Test status validation with valid statuses."""
        assert ExpenseValidationService.validate_status("pending") is True
        assert ExpenseValidationService.validate_status("completed") is True
        assert ExpenseValidationService.validate_status("cancelled") is True
        assert ExpenseValidationService.validate_status("PENDING") is True
        assert ExpenseValidationService.validate_status("Completed") is True

    def test_validate_status_invalid(self):
        """Test status validation with invalid statuses."""
        assert ExpenseValidationService.validate_status("invalid") is False
        assert ExpenseValidationService.validate_status("") is False
        assert ExpenseValidationService.validate_status("active") is False

    def test_validate_recurring_frequency_non_recurring(self):
        """Test recurring frequency validation for non-recurring expenses."""
        assert (
            ExpenseValidationService.validate_recurring_frequency(False, None) is True
        )
        assert (
            ExpenseValidationService.validate_recurring_frequency(False, "daily")
            is True
        )

    def test_validate_recurring_frequency_valid(self):
        """Test recurring frequency validation with valid frequencies."""
        assert (
            ExpenseValidationService.validate_recurring_frequency(True, "daily") is True
        )
        assert (
            ExpenseValidationService.validate_recurring_frequency(True, "weekly")
            is True
        )
        assert (
            ExpenseValidationService.validate_recurring_frequency(True, "monthly")
            is True
        )
        assert (
            ExpenseValidationService.validate_recurring_frequency(True, "yearly")
            is True
        )
        assert (
            ExpenseValidationService.validate_recurring_frequency(True, "DAILY") is True
        )

    def test_validate_recurring_frequency_invalid(self):
        """Test recurring frequency validation with invalid frequencies."""
        assert (
            ExpenseValidationService.validate_recurring_frequency(True, None) is False
        )
        assert ExpenseValidationService.validate_recurring_frequency(True, "") is False
        assert (
            ExpenseValidationService.validate_recurring_frequency(True, "invalid")
            is False
        )
        assert (
            ExpenseValidationService.validate_recurring_frequency(True, "hourly")
            is False
        )
