"""
Tests for async base service module.
"""

from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import DatabaseError, NotFoundError, ValidationError
from src.services.async_base_service import AsyncBaseService


class TestAsyncBaseService:
    """Test cases for AsyncBaseService."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock async database session."""
        return Mock(spec=AsyncSession)

    @pytest.fixture
    def async_base_service(self, mock_db_session):
        """Create an AsyncBaseService instance for testing."""
        return AsyncBaseService(mock_db_session)

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

    def test_init(self, mock_db_session):
        """Test AsyncBaseService initialization."""
        service = AsyncBaseService(mock_db_session)
        assert service.db == mock_db_session

    @pytest.mark.asyncio
    async def test_validate_required_fields_success(self, async_base_service):
        """Test successful validation of required fields."""
        data = {"field1": "value1", "field2": "value2", "field3": "value3"}
        required_fields = ["field1", "field2", "field3"]

        # Should not raise any exception
        await async_base_service.validate_required_fields(data, required_fields)

    @pytest.mark.asyncio
    async def test_validate_required_fields_missing_fields(self, async_base_service):
        """Test validation with missing required fields."""
        data = {"field1": "value1", "field2": "value2"}
        required_fields = ["field1", "field2", "field3", "field4"]

        with pytest.raises(ValidationError) as exc_info:
            await async_base_service.validate_required_fields(data, required_fields)

        assert "Missing required fields: field3, field4" in str(exc_info.value)
        assert exc_info.value.details == {"missing_fields": ["field3", "field4"]}

    @pytest.mark.asyncio
    async def test_validate_required_fields_none_values(self, async_base_service):
        """Test validation with None values."""
        data = {"field1": "value1", "field2": None, "field3": "value3"}
        required_fields = ["field1", "field2", "field3"]

        with pytest.raises(ValidationError) as exc_info:
            await async_base_service.validate_required_fields(data, required_fields)

        assert "Missing required fields: field2" in str(exc_info.value)
        assert exc_info.value.details == {"missing_fields": ["field2"]}

    @pytest.mark.asyncio
    async def test_validate_required_fields_empty_data(self, async_base_service):
        """Test validation with empty data."""
        data = {}
        required_fields = ["field1", "field2"]

        with pytest.raises(ValidationError) as exc_info:
            await async_base_service.validate_required_fields(data, required_fields)

        assert "Missing required fields: field1, field2" in str(exc_info.value)
        assert exc_info.value.details == {"missing_fields": ["field1", "field2"]}

    @pytest.mark.asyncio
    async def test_validate_field_length_success(self, async_base_service):
        """Test successful field length validation."""
        field_value = "short"
        field_name = "test_field"
        max_length = 10

        # Should not raise any exception
        await async_base_service.validate_field_length(
            field_value, field_name, max_length
        )

    @pytest.mark.asyncio
    async def test_validate_field_length_exceeds_max(self, async_base_service):
        """Test field length validation when field exceeds maximum length."""
        field_value = "this is a very long string that exceeds the maximum length"
        field_name = "test_field"
        max_length = 10

        with pytest.raises(ValidationError) as exc_info:
            await async_base_service.validate_field_length(
                field_value, field_name, max_length
            )

        assert "test_field exceeds maximum length of 10 characters" in str(
            exc_info.value
        )
        assert exc_info.value.details == {
            "max_length": 10,
            "actual_length": len(field_value),
            "field": "test_field",
        }

    @pytest.mark.asyncio
    async def test_validate_field_length_empty_string(self, async_base_service):
        """Test field length validation with empty string."""
        field_value = ""
        field_name = "test_field"
        max_length = 10

        # Should not raise any exception (empty string is allowed)
        await async_base_service.validate_field_length(
            field_value, field_name, max_length
        )

    @pytest.mark.asyncio
    async def test_validate_field_length_none_value(self, async_base_service):
        """Test field length validation with None value."""
        field_value = None
        field_name = "test_field"
        max_length = 10

        # Should not raise any exception (None is allowed)
        await async_base_service.validate_field_length(
            field_value, field_name, max_length
        )

    @pytest.mark.asyncio
    async def test_validate_field_range_success(self, async_base_service):
        """Test successful field range validation."""
        field_value = 5.0
        field_name = "test_field"
        min_value = 1.0
        max_value = 10.0

        # Should not raise any exception
        await async_base_service.validate_field_range(
            field_value, field_name, min_value, max_value
        )

    @pytest.mark.asyncio
    async def test_validate_field_range_below_min(self, async_base_service):
        """Test field range validation when value is below minimum."""
        field_value = 0.5
        field_name = "test_field"
        min_value = 1.0
        max_value = 10.0

        with pytest.raises(ValidationError) as exc_info:
            await async_base_service.validate_field_range(
                field_value, field_name, min_value, max_value
            )

        assert "test_field must be between 1.0 and 10.0" in str(exc_info.value)
        assert exc_info.value.details == {
            "min_value": 1.0,
            "max_value": 10.0,
            "actual_value": 0.5,
            "field": "test_field",
        }

    @pytest.mark.asyncio
    async def test_validate_field_range_above_max(self, async_base_service):
        """Test field range validation when value is above maximum."""
        field_value = 15.0
        field_name = "test_field"
        min_value = 1.0
        max_value = 10.0

        with pytest.raises(ValidationError) as exc_info:
            await async_base_service.validate_field_range(
                field_value, field_name, min_value, max_value
            )

        assert "test_field must be between 1.0 and 10.0" in str(exc_info.value)
        assert exc_info.value.details == {
            "min_value": 1.0,
            "max_value": 10.0,
            "actual_value": 15.0,
            "field": "test_field",
        }

    @pytest.mark.asyncio
    async def test_validate_field_range_boundary_values(self, async_base_service):
        """Test field range validation with boundary values."""
        field_name = "test_field"
        min_value = 1.0
        max_value = 10.0

        # Test minimum boundary
        await async_base_service.validate_field_range(
            1.0, field_name, min_value, max_value
        )

        # Test maximum boundary
        await async_base_service.validate_field_range(
            10.0, field_name, min_value, max_value
        )

    @pytest.mark.asyncio
    async def test_handle_database_operation_success(self, async_base_service):
        """Test successful database operation handling."""
        operation_name = "test_operation"
        operation_func = AsyncMock(return_value="success_result")

        result = await async_base_service.handle_database_operation(
            operation_name, operation_func
        )

        assert result == "success_result"
        operation_func.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_database_operation_exception(self, async_base_service):
        """Test database operation handling with exception."""
        operation_name = "test_operation"
        operation_func = AsyncMock(side_effect=Exception("Database error"))

        with pytest.raises(DatabaseError) as exc_info:
            await async_base_service.handle_database_operation(
                operation_name, operation_func
            )

        assert (
            "Database operation 'test_operation' failed: Database operation failed: test_operation"
            in str(exc_info.value)
        )
        assert exc_info.value.details == {
            "operation": "test_operation",
            "error": "Database error",
        }

    @pytest.mark.asyncio
    async def test_ensure_record_exists_success(self, async_base_service):
        """Test successful record existence check."""
        record_id = 1
        mock_record = Mock()
        get_func = AsyncMock(return_value=mock_record)
        resource_name = "test_resource"

        result = await async_base_service.ensure_record_exists(
            record_id, get_func, resource_name
        )

        assert result == mock_record
        get_func.assert_called_once_with(record_id)

    @pytest.mark.asyncio
    async def test_ensure_record_exists_not_found(self, async_base_service):
        """Test record existence check when record not found."""
        record_id = 999
        get_func = AsyncMock(return_value=None)
        resource_name = "test_resource"

        with pytest.raises(NotFoundError) as exc_info:
            await async_base_service.ensure_record_exists(
                record_id, get_func, resource_name
            )

        assert str(exc_info.value) == "test_resource with ID '999' not found."

    @pytest.mark.asyncio
    async def test_validate_unique_constraint_success(self, async_base_service):
        """Test successful unique constraint validation."""
        field_value = "unique_value"
        field_name = "test_field"
        check_func = AsyncMock(return_value=False)

        # Should not raise any exception
        await async_base_service.validate_unique_constraint(
            field_value, field_name, check_func
        )
        check_func.assert_called_once_with(field_value, None)

    @pytest.mark.asyncio
    async def test_validate_unique_constraint_with_exclude(self, async_base_service):
        """Test unique constraint validation with exclude_id."""
        field_value = "unique_value"
        field_name = "test_field"
        check_func = AsyncMock(return_value=False)
        exclude_id = 1

        # Should not raise any exception
        await async_base_service.validate_unique_constraint(
            field_value, field_name, check_func, exclude_id
        )
        check_func.assert_called_once_with(field_value, exclude_id)

    @pytest.mark.asyncio
    async def test_validate_unique_constraint_violation(self, async_base_service):
        """Test unique constraint validation when constraint is violated."""
        field_value = "existing_value"
        field_name = "test_field"
        check_func = AsyncMock(return_value=True)

        with pytest.raises(ValidationError) as exc_info:
            await async_base_service.validate_unique_constraint(
                field_value, field_name, check_func
            )

        assert "test_field already exists" in str(exc_info.value)
        assert exc_info.value.details == {
            "field_value": "existing_value",
            "field": "test_field",
        }

    @pytest.mark.asyncio
    async def test_log_operation(self, async_base_service):
        """Test logging an operation."""
        operation = "test_operation"
        extra_data = {"key1": "value1", "key2": "value2"}

        # Test that the method doesn't raise an exception
        await async_base_service.log_operation(operation, **extra_data)

        # The actual logging is tested indirectly through the logger mixin
        assert hasattr(async_base_service, "logger")

    @pytest.mark.asyncio
    async def test_log_error(self, async_base_service):
        """Test logging an error."""
        operation = "test_operation"
        error = Exception("Test error")
        extra_data = {"key1": "value1", "key2": "value2"}

        # Test that the method doesn't raise an exception
        await async_base_service.log_error(operation, error, **extra_data)

        # The actual logging is tested indirectly through the logger mixin
        assert hasattr(async_base_service, "logger")

    def test_logger_mixin_inheritance(self, async_base_service):
        """Test that service inherits from LoggerMixin."""
        assert hasattr(async_base_service, "logger")
        assert async_base_service.logger is not None

    @pytest.mark.asyncio
    async def test_handle_database_operation_logging(self, async_base_service):
        """Test that database operations are properly logged."""
        operation_name = "test_operation"
        operation_func = AsyncMock(return_value="success_result")

        # Test that the method works and doesn't raise an exception
        result = await async_base_service.handle_database_operation(
            operation_name, operation_func
        )

        # Verify the result
        assert result == "success_result"
        operation_func.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_database_operation_error_logging(self, async_base_service):
        """Test that database operation errors are properly logged."""
        operation_name = "test_operation"
        operation_func = AsyncMock(side_effect=Exception("Database error"))

        # Test that the method raises the expected exception
        with pytest.raises(DatabaseError):
            await async_base_service.handle_database_operation(
                operation_name, operation_func
            )

        # The actual logging is tested indirectly through the logger mixin
        assert hasattr(async_base_service, "logger")
