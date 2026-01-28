"""
Category validation service for validation logic.
"""

from typing import Optional


class CategoryValidationService:
    """Service for category validation logic following SRP."""

    @staticmethod
    def validate_name(name: str) -> bool:
        """Validate category name."""
        return len(name.strip()) > 0 and len(name) <= 100

    @staticmethod
    def validate_color(color: Optional[str]) -> bool:
        """Validate category color (hex format)."""
        if not color:
            return True

        # Remove # if present
        color = color.lstrip("#")

        # Check if it's a valid hex color
        if len(color) != 6:
            return False

        try:
            int(color, 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_description(description: Optional[str]) -> bool:
        """Validate category description."""
        if not description:
            return True

        return len(description) <= 500
