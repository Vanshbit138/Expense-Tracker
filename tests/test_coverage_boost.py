"""
Quick tests to boost coverage to 80%+.
"""

from src.core.config import settings
from src.core.exceptions import (
    ConflictError,
    ExpenseTrackerException,
    NotFoundError,
    ValidationError,
)


class TestCoverageBoost:
    """Tests to boost overall coverage."""

    def test_custom_exceptions(self):
        """Test custom exception classes."""
        # Test ValidationError
        exc = ValidationError("Test validation error", field="test_field")
        assert exc.message == "Test validation error"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.status_code == 400

        # Test NotFoundError
        exc = NotFoundError("User", 123)
        assert "User not found" in exc.message
        assert exc.error_code == "NOT_FOUND_ERROR"
        assert exc.status_code == 404

        # Test ConflictError
        exc = ConflictError("Resource conflict")
        assert exc.message == "Resource conflict"
        assert exc.error_code == "CONFLICT_ERROR"
        assert exc.status_code == 409

        # Test base exception
        exc = ExpenseTrackerException("Base error", "BASE_ERROR", {"key": "value"}, 500)
        assert exc.message == "Base error"
        assert exc.error_code == "BASE_ERROR"
        assert exc.details == {"key": "value"}
        assert exc.status_code == 500

    def test_settings_config(self):
        """Test settings configuration."""
        # Test basic settings
        assert settings.app_name == "Expense Tracker API"
        # Note: debug might be True in test environment
        assert isinstance(settings.debug, bool)
        assert settings.version == "1.0.0"
        assert settings.api_v1_str == "/api/v1"

        # Test database URLs
        assert "postgresql://" in settings.database_url
        assert "postgresql://" in settings.database_url_test

        # Test JWT settings
        assert settings.secret_key is not None
        assert settings.algorithm == "HS256"
        assert settings.access_token_expire_minutes == 1440

        # Test CORS settings
        assert isinstance(settings.backend_cors_origins, list)
        assert len(settings.backend_cors_origins) > 0

        # Test pagination settings
        assert settings.default_page_size == 20
        assert settings.max_page_size == 100
