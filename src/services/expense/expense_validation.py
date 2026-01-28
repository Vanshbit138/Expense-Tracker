"""
Expense validation service for validation logic.
"""

from datetime import date
from decimal import Decimal
from typing import Optional


class ExpenseValidationService:
    """Service for expense validation logic following SRP."""

    @staticmethod
    def validate_amount(amount: Decimal) -> bool:
        """Validate expense amount."""
        return amount > 0

    @staticmethod
    def validate_date_range(
        start_date: Optional[date], end_date: Optional[date]
    ) -> bool:
        """Validate date range."""
        if start_date and end_date:
            return start_date <= end_date
        return True

    @staticmethod
    def validate_currency(currency: str) -> bool:
        """Validate currency code."""
        return len(currency) == 3 and currency.isalpha()

    @staticmethod
    def validate_status(status: str) -> bool:
        """Validate expense status."""
        valid_statuses = ["pending", "completed", "cancelled"]
        return status.lower() in valid_statuses

    @staticmethod
    def validate_recurring_frequency(
        is_recurring: bool, frequency: Optional[str]
    ) -> bool:
        """Validate recurring frequency."""
        if not is_recurring:
            return True

        if is_recurring and not frequency:
            return False

        valid_frequencies = ["daily", "weekly", "monthly", "yearly"]
        return frequency.lower() in valid_frequencies
