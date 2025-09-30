"""
Unit tests for custom exceptions module.
"""

import pytest
from fastapi import HTTPException, status

from src.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DatabaseError,
    ExpenseTrackerException,
    ExternalServiceError,
    NotFoundError,
    ValidationError,
    handle_exception,
)


class TestExpenseTrackerException:
    """Test cases for base ExpenseTrackerException."""

    def test_basic_exception_creation(self):
        """Test basic exception creation."""
        exc = ExpenseTrackerException("Test message")

        assert exc.message == "Test message"
        assert exc.error_code == "UNKNOWN_ERROR"
        assert exc.details == {}
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert str(exc) == "Test message"

    def test_exception_with_custom_values(self):
        """Test exception creation with custom values."""
        details = {"field": "email", "value": "invalid"}
        exc = ExpenseTrackerException(
            message="Custom error",
            error_code="CUSTOM_ERROR",
            details=details,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

        assert exc.message == "Custom error"
        assert exc.error_code == "CUSTOM_ERROR"
        assert exc.details == details
        assert exc.status_code == status.HTTP_400_BAD_REQUEST

    def test_exception_inheritance(self):
        """Test that exception inherits from Exception."""
        exc = ExpenseTrackerException("Test")
        assert isinstance(exc, Exception)


class TestValidationError:
    """Test cases for ValidationError."""

    def test_validation_error_creation(self):
        """Test validation error creation."""
        exc = ValidationError("Invalid email format")

        assert exc.message == "Invalid email format"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_validation_error_with_field(self):
        """Test validation error with field information."""
        exc = ValidationError("Invalid email format", field="email")

        assert exc.message == "Invalid email format"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.details["field"] == "email"

    def test_validation_error_with_details(self):
        """Test validation error with additional details."""
        details = {"min_length": 5, "max_length": 50}
        exc = ValidationError("Invalid length", field="username", details=details)

        assert exc.details["field"] == "username"
        assert exc.details["min_length"] == 5
        assert exc.details["max_length"] == 50


class TestAuthenticationError:
    """Test cases for AuthenticationError."""

    def test_authentication_error_default(self):
        """Test default authentication error."""
        exc = AuthenticationError()

        assert exc.message == "Authentication failed"
        assert exc.error_code == "AUTHENTICATION_ERROR"
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authentication_error_custom(self):
        """Test custom authentication error."""
        exc = AuthenticationError("Invalid token", {"token_type": "bearer"})

        assert exc.message == "Invalid token"
        assert exc.error_code == "AUTHENTICATION_ERROR"
        assert exc.details["token_type"] == "bearer"


class TestAuthorizationError:
    """Test cases for AuthorizationError."""

    def test_authorization_error_default(self):
        """Test default authorization error."""
        exc = AuthorizationError()

        assert exc.message == "Access denied"
        assert exc.error_code == "AUTHORIZATION_ERROR"
        assert exc.status_code == status.HTTP_403_FORBIDDEN

    def test_authorization_error_custom(self):
        """Test custom authorization error."""
        exc = AuthorizationError("Insufficient permissions", {"required_role": "admin"})

        assert exc.message == "Insufficient permissions"
        assert exc.error_code == "AUTHORIZATION_ERROR"
        assert exc.details["required_role"] == "admin"


class TestNotFoundError:
    """Test cases for NotFoundError."""

    def test_not_found_error_creation(self):
        """Test not found error creation."""
        exc = NotFoundError("User", 123)

        assert exc.message == "User with ID '123' not found."
        assert exc.error_code == "NOT_FOUND_ERROR"
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.details["resource"] == "User"
        assert exc.details["identifier"] == 123

    def test_not_found_error_with_details(self):
        """Test not found error with additional details."""
        details = {"context": "search_by_email"}
        exc = NotFoundError("User", "test@example.com", details)

        assert exc.message == "User with ID 'test@example.com' not found."
        assert exc.details["resource"] == "User"
        assert exc.details["identifier"] == "test@example.com"
        assert exc.details["context"] == "search_by_email"


class TestConflictError:
    """Test cases for ConflictError."""

    def test_conflict_error_creation(self):
        """Test conflict error creation."""
        exc = ConflictError("Email already exists")

        assert exc.message == "Email already exists"
        assert exc.error_code == "CONFLICT_ERROR"
        assert exc.status_code == status.HTTP_409_CONFLICT

    def test_conflict_error_with_details(self):
        """Test conflict error with details."""
        details = {"existing_user_id": 456}
        exc = ConflictError("Email already exists", details)

        assert exc.message == "Email already exists"
        assert exc.details["existing_user_id"] == 456


class TestDatabaseError:
    """Test cases for DatabaseError."""

    def test_database_error_creation(self):
        """Test database error creation."""
        exc = DatabaseError("INSERT", "Connection timeout")

        assert exc.message == "Database operation 'INSERT' failed: Connection timeout"
        assert exc.error_code == "DATABASE_ERROR"
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc.details["operation"] == "INSERT"

    def test_database_error_with_details(self):
        """Test database error with additional details."""
        details = {"table": "users", "constraint": "unique_email"}
        exc = DatabaseError("UPDATE", "Constraint violation", details)

        assert exc.message == "Database operation 'UPDATE' failed: Constraint violation"
        assert exc.details["operation"] == "UPDATE"
        assert exc.details["table"] == "users"
        assert exc.details["constraint"] == "unique_email"


class TestExternalServiceError:
    """Test cases for ExternalServiceError."""

    def test_external_service_error_creation(self):
        """Test external service error creation."""
        exc = ExternalServiceError("PaymentGateway", "Service unavailable")

        assert (
            exc.message
            == "External service 'PaymentGateway' failed: Service unavailable"
        )
        assert exc.error_code == "EXTERNAL_SERVICE_ERROR"
        assert exc.status_code == status.HTTP_502_BAD_GATEWAY
        assert exc.details["service"] == "PaymentGateway"

    def test_external_service_error_with_details(self):
        """Test external service error with additional details."""
        details = {"endpoint": "/api/payments", "status_code": 503}
        exc = ExternalServiceError("EmailService", "Rate limit exceeded", details)

        assert (
            exc.message == "External service 'EmailService' failed: Rate limit exceeded"
        )
        assert exc.details["service"] == "EmailService"
        assert exc.details["endpoint"] == "/api/payments"
        assert exc.details["status_code"] == 503


class TestHandleException:
    """Test cases for handle_exception function."""

    def test_handle_expense_tracker_exception(self):
        """Test handling of ExpenseTrackerException."""
        exc = ValidationError("Invalid input", field="email")
        http_exc = handle_exception(exc)

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert http_exc.detail["error_code"] == "VALIDATION_ERROR"
        assert http_exc.detail["message"] == "Invalid input"
        assert http_exc.detail["details"]["field"] == "email"

    def test_handle_generic_exception(self):
        """Test handling of generic exceptions."""
        exc = ValueError("Generic error")
        http_exc = handle_exception(exc)

        assert isinstance(http_exc, HTTPException)
        assert http_exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert http_exc.detail["error_code"] == "INTERNAL_SERVER_ERROR"
        assert http_exc.detail["message"] == "An unexpected error occurred"

    def test_handle_exception_with_logging(self, mock_logger):
        """Test that exceptions are properly logged."""
        with pytest.MonkeyPatch().context() as m:
            m.setattr("src.core.exceptions.logger", mock_logger)

            exc = ValueError("Test error")
            handle_exception(exc)

            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args
            assert "Unexpected exception" in call_args[0][0]
            assert call_args[1]["exception_type"] == "ValueError"
            assert call_args[1]["exception_message"] == "Test error"
