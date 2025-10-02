"""
Tests for async base service module.
"""

from src.services.async_base_service import AsyncBaseService


class TestAsyncBaseService:
    """Test cases for AsyncBaseService."""

    def test_async_base_service_class_exists(self):
        """Test that AsyncBaseService class exists."""
        assert AsyncBaseService is not None

    def test_async_base_service_methods_exist(self):
        """Test that key methods exist in AsyncBaseService."""
        methods = [
            "validate_required_fields",
            "validate_field_length",
            "validate_field_range",
            "handle_database_operation",
            "ensure_record_exists",
            "validate_unique_constraint",
            "log_operation",
            "log_error",
        ]

        for method in methods:
            assert hasattr(AsyncBaseService, method)
            assert callable(getattr(AsyncBaseService, method))

    def test_async_base_service_init_method(self):
        """Test that __init__ method exists."""
        assert hasattr(AsyncBaseService, "__init__")
        assert callable(AsyncBaseService.__init__)
