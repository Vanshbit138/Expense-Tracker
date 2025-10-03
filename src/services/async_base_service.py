"""
Async base service with common business logic patterns.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import DatabaseError, NotFoundError, ValidationError
from src.core.logging_config import LoggerMixin

ServiceType = TypeVar("ServiceType")


class AsyncBaseService(Generic[ServiceType], LoggerMixin):
    """Async base service with common business logic patterns."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def validate_required_fields(
        self, data: Dict[str, Any], required_fields: List[str]
    ) -> None:
        """Validate that all required fields are present."""
        missing_fields = [
            field
            for field in required_fields
            if field not in data or data[field] is None
        ]

        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                details={"missing_fields": missing_fields},
            )

    async def validate_field_length(
        self, field_value: str, field_name: str, max_length: int
    ) -> None:
        """Validate field length."""
        if field_value and len(field_value) > max_length:
            raise ValidationError(
                f"{field_name} exceeds maximum length of {max_length} characters",
                field=field_name,
                details={"max_length": max_length, "actual_length": len(field_value)},
            )

    async def validate_field_range(
        self, field_value: float, field_name: str, min_value: float, max_value: float
    ) -> None:
        """Validate field is within specified range."""
        if field_value < min_value or field_value > max_value:
            raise ValidationError(
                f"{field_name} must be between {min_value} and {max_value}",
                field=field_name,
                details={
                    "min_value": min_value,
                    "max_value": max_value,
                    "actual_value": field_value,
                },
            )

    async def handle_database_operation(self, operation_name: str, operation_func):
        """Handle database operations with proper error handling and logging."""
        try:
            self.logger.info(f"Starting {operation_name}")
            result = await operation_func()
            self.logger.info(f"Successfully completed {operation_name}")
            return result
        except Exception as e:
            self.logger.error(f"Failed {operation_name}", error=str(e), exc_info=True)
            raise DatabaseError(
                operation=operation_name,
                message=f"Database operation failed: {operation_name}",
                details={"error": str(e)},
            )

    async def ensure_record_exists(
        self, record_id: Any, get_func, resource_name: str
    ) -> Any:
        """Ensure a record exists, raise NotFoundError if not."""
        record = await get_func(record_id)
        if not record:
            raise NotFoundError(resource_name, record_id)
        return record

    async def validate_unique_constraint(
        self,
        field_value: Any,
        field_name: str,
        check_func,
        exclude_id: Optional[Any] = None,
    ) -> None:
        """Validate that a field value is unique."""
        exists = await check_func(field_value, exclude_id)
        if exists:
            raise ValidationError(
                f"{field_name} already exists",
                field=field_name,
                details={"field_value": field_value},
            )

    async def log_operation(self, operation: str, **kwargs) -> None:
        """Log an operation with context."""
        self.logger.info(f"Operation: {operation}", **kwargs)

    async def log_error(self, operation: str, error: Exception, **kwargs) -> None:
        """Log an error with context."""
        self.logger.error(
            f"Operation failed: {operation}", error=str(error), exc_info=True, **kwargs
        )
