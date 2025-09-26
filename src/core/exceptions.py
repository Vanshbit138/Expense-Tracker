"""
Custom exceptions for the Expense Tracker API.
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException, status

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class ExpenseTrackerException(Exception):
    """Base exception for Expense Tracker API."""

    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)

        # Log the exception
        logger.error(
            "Exception raised",
            error_code=error_code,
            message=message,
            details=self.details,
            status_code=status_code,
        )


class ValidationError(ExpenseTrackerException):
    """Raised when validation fails."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class AuthenticationError(ExpenseTrackerException):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details or {},
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class AuthorizationError(ExpenseTrackerException):
    """Raised when authorization fails."""

    def __init__(
        self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=details or {},
            status_code=status.HTTP_403_FORBIDDEN,
        )


class NotFoundError(ExpenseTrackerException):
    """Raised when a resource is not found."""

    def __init__(
        self, resource: str, identifier: Any, details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details.update({"resource": resource, "identifier": identifier})
        super().__init__(
            message=f"{resource} not found",
            error_code="NOT_FOUND_ERROR",
            details=details,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ConflictError(ExpenseTrackerException):
    """Raised when there's a conflict with existing data."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFLICT_ERROR",
            details=details or {},
            status_code=status.HTTP_409_CONFLICT,
        )


class DatabaseError(ExpenseTrackerException):
    """Raised when database operations fail."""

    def __init__(
        self, message: str, operation: str, details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details["operation"] = operation
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details=details,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class ExternalServiceError(ExpenseTrackerException):
    """Raised when external service calls fail."""

    def __init__(
        self, service: str, message: str, details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details["service"] = service
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
            status_code=status.HTTP_502_BAD_GATEWAY,
        )


def handle_exception(exception: Exception) -> HTTPException:
    """Convert custom exceptions to HTTP exceptions."""

    if isinstance(exception, ExpenseTrackerException):
        return HTTPException(
            status_code=exception.status_code,
            detail={
                "error_code": exception.error_code,
                "message": exception.message,
                "details": exception.details,
            },
        )

    # Handle unexpected exceptions
    logger.error(
        "Unexpected exception",
        exception_type=type(exception).__name__,
        exception_message=str(exception),
        exc_info=True,
    )

    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": {},
        },
    )
