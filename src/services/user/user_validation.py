"""
User validation service for validation logic.
"""

import re
from typing import Optional


class UserValidationService:
    """Service for user validation logic following SRP."""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(email_pattern, email) is not None

    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format."""
        # Username should be 3-50 characters, alphanumeric and underscores only
        if len(username) < 3 or len(username) > 50:
            return False

        username_pattern = r"^[a-zA-Z0-9_]+$"
        return re.match(username_pattern, username) is not None

    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password strength."""
        # Password should be at least 8 characters
        if len(password) < 8:
            return False

        # Should contain at least one letter and one number
        has_letter = re.search(r"[a-zA-Z]", password) is not None
        has_number = re.search(r"\d", password) is not None

        return has_letter and has_number

    @staticmethod
    def validate_full_name(full_name: Optional[str]) -> bool:
        """Validate full name."""
        if not full_name:
            return True

        # Should be 1-100 characters
        if len(full_name.strip()) == 0 or len(full_name) > 100:
            return False

        # Should contain only letters, spaces, hyphens, and apostrophes
        name_pattern = r"^[a-zA-Z\s\-']+$"
        return re.match(name_pattern, full_name) is not None
