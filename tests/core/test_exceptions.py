"""
Tests for custom exceptions.
"""

from fastapi import status

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
    """Test base ExpenseTrackerException."""

    def test_base_exception_creation(self):
        """Test creating base exception with default values."""
        exc = ExpenseTrackerException("Test error")
        assert exc.message == "Test error"
        assert exc.error_code == "UNKNOWN_ERROR"
        assert exc.details == {}
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_base_exception_with_all_params(self):
        """Test creating base exception with all parameters."""
        details = {"key": "value"}
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


class TestValidationError:
    """Test ValidationError."""

    def test_validation_error_without_field(self):
        """Test ValidationError without field specified."""
        exc = ValidationError("Validation failed")
        assert exc.message == "Validation failed"
        assert exc.error_code == "VALIDATION_ERROR"
        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_validation_error_with_field(self):
        """Test ValidationError with field specified."""
        exc = ValidationError("Invalid email", field="email")
        assert exc.message == "Invalid email"
        assert exc.details["field"] == "email"

    def test_validation_error_with_details(self):
        """Test ValidationError with additional details."""
        details = {"reason": "too_short"}
        exc = ValidationError("Invalid value", field="username", details=details)
        assert exc.details["field"] == "username"
        assert exc.details["reason"] == "too_short"


class TestAuthenticationError:
    """Test AuthenticationError."""

    def test_authentication_error_default_message(self):
        """Test AuthenticationError with default message."""
        exc = AuthenticationError()
        assert exc.message == "Authentication failed"
        assert exc.error_code == "AUTHENTICATION_ERROR"
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authentication_error_custom_message(self):
        """Test AuthenticationError with custom message."""
        exc = AuthenticationError("Invalid token")
        assert exc.message == "Invalid token"

    def test_authentication_error_with_details(self):
        """Test AuthenticationError with details."""
        details = {"token": "expired"}
        exc = AuthenticationError("Token expired", details=details)
        assert exc.details == details


class TestAuthorizationError:
    """Test AuthorizationError."""

    def test_authorization_error_default_message(self):
        """Test AuthorizationError with default message."""
        exc = AuthorizationError()
        assert exc.message == "Access denied"
        assert exc.error_code == "AUTHORIZATION_ERROR"
        assert exc.status_code == status.HTTP_403_FORBIDDEN

    def test_authorization_error_custom_message(self):
        """Test AuthorizationError with custom message."""
        exc = AuthorizationError("Insufficient permissions")
        assert exc.message == "Insufficient permissions"


class TestNotFoundError:
    """Test NotFoundError."""

    def test_not_found_error(self):
        """Test NotFoundError with resource and identifier."""
        exc = NotFoundError("User", 123)
        assert "User" in exc.message
        assert "123" in exc.message
        assert exc.error_code == "NOT_FOUND_ERROR"
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.details["resource"] == "User"
        assert exc.details["identifier"] == 123

    def test_not_found_error_with_string_identifier(self):
        """Test NotFoundError with string identifier."""
        exc = NotFoundError("Category", "abc-123")
        assert "Category" in exc.message
        assert "abc-123" in exc.message


class TestConflictError:
    """Test ConflictError."""

    def test_conflict_error(self):
        """Test ConflictError."""
        exc = ConflictError("Email already exists")
        assert exc.message == "Email already exists"
        assert exc.error_code == "CONFLICT_ERROR"
        assert exc.status_code == status.HTTP_409_CONFLICT

    def test_conflict_error_with_details(self):
        """Test ConflictError with details."""
        details = {"field": "email", "value": "test@example.com"}
        exc = ConflictError("Duplicate entry", details=details)
        assert exc.details == details


class TestDatabaseError:
    """Test DatabaseError."""

    def test_database_error(self):
        """Test DatabaseError."""
        exc = DatabaseError("insert", "Connection failed")
        assert "insert" in exc.message
        assert "Connection failed" in exc.message
        assert exc.error_code == "DATABASE_ERROR"
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc.details["operation"] == "insert"

    def test_database_error_with_details(self):
        """Test DatabaseError with additional details."""
        details = {"table": "users", "error_code": "23505"}
        exc = DatabaseError("update", "Unique constraint violation", details=details)
        assert exc.details["operation"] == "update"
        assert exc.details["table"] == "users"
        assert exc.details["error_code"] == "23505"


class TestExternalServiceError:
    """Test ExternalServiceError."""

    def test_external_service_error(self):
        """Test ExternalServiceError."""
        exc = ExternalServiceError("payment_gateway", "Timeout")
        assert "payment_gateway" in exc.message
        assert "Timeout" in exc.message
        assert exc.error_code == "EXTERNAL_SERVICE_ERROR"
        assert exc.status_code == status.HTTP_502_BAD_GATEWAY
        assert exc.details["service"] == "payment_gateway"

    def test_external_service_error_with_details(self):
        """Test ExternalServiceError with additional details."""
        details = {"status_code": 503, "retry_after": 60}
        exc = ExternalServiceError("api", "Service unavailable", details=details)
        assert exc.details["service"] == "api"
        assert exc.details["status_code"] == 503
        assert exc.details["retry_after"] == 60


class TestHandleException:
    """Test handle_exception function."""

    def test_handle_expense_tracker_exception(self):
        """Test handling ExpenseTrackerException."""
        exc = ValidationError("Invalid data", field="email")
        http_exc = handle_exception(exc)

        assert http_exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert http_exc.detail["error_code"] == "VALIDATION_ERROR"
        assert http_exc.detail["message"] == "Invalid data"
        assert "field" in http_exc.detail["details"]

    def test_handle_generic_exception(self):
        """Test handling generic Exception."""
        exc = Exception("Unexpected error")
        http_exc = handle_exception(exc)

        assert http_exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert http_exc.detail["error_code"] == "INTERNAL_SERVER_ERROR"
        assert http_exc.detail["message"] == "An unexpected error occurred"

    def test_handle_not_found_exception(self):
        """Test handling NotFoundError."""
        exc = NotFoundError("Expense", 999)
        http_exc = handle_exception(exc)

        assert http_exc.status_code == status.HTTP_404_NOT_FOUND
        assert http_exc.detail["error_code"] == "NOT_FOUND_ERROR"

    def test_handle_authentication_exception(self):
        """Test handling AuthenticationError."""
        exc = AuthenticationError("Invalid credentials")
        http_exc = handle_exception(exc)

        assert http_exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert http_exc.detail["error_code"] == "AUTHENTICATION_ERROR"
