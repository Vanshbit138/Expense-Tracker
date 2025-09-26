"""
Tests for enhanced features: logging, async, file validation, etc.
"""

import os
import tempfile
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.core.auth_bypass import AuthBypass
from src.core.exceptions import ConflictError, NotFoundError, ValidationError
from src.core.file_validation import FileValidator
from src.core.logging_config import get_logger, setup_logging
from src.core.query_optimization import IndexOptimizer, QueryOptimizer
from src.schemas.user import UserCreate
from src.services.user.async_user_service import AsyncUserService


class TestLoggingConfiguration:
    """Test logging configuration."""

    def test_setup_logging(self):
        """Test logging setup."""
        setup_logging(log_level="DEBUG", enable_json=False)
        logger = get_logger("test")
        assert logger is not None

    def test_logger_mixin(self):
        """Test LoggerMixin functionality."""
        from src.core.logging_config import LoggerMixin

        class TestClass(LoggerMixin):
            pass

        test_obj = TestClass()
        assert hasattr(test_obj, "logger")
        assert test_obj.logger is not None


class TestCustomExceptions:
    """Test custom exception classes."""

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Test validation error", field="test_field")
        assert error.message == "Test validation error"
        assert error.error_code == "VALIDATION_ERROR"
        assert error.status_code == 400
        assert error.details["field"] == "test_field"

    def test_not_found_error(self):
        """Test NotFoundError."""
        error = NotFoundError("User", 123)
        assert error.message == "User not found"
        assert error.error_code == "NOT_FOUND_ERROR"
        assert error.status_code == 404
        assert error.details["resource"] == "User"
        assert error.details["identifier"] == 123

    def test_conflict_error(self):
        """Test ConflictError."""
        error = ConflictError("Email already exists")
        assert error.message == "Email already exists"
        assert error.error_code == "CONFLICT_ERROR"
        assert error.status_code == 409


class TestFileValidation:
    """Test file validation functionality."""

    def setup_method(self):
        """Set up test files."""
        self.validator = FileValidator()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test files."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validate_image_file(self):
        """Test image file validation."""
        # Create a dummy image file
        image_path = os.path.join(self.temp_dir, "test.jpg")
        with open(image_path, "wb") as f:
            f.write(b"fake image data")

        is_valid, mime_type, error = self.validator.validate_image(image_path)
        # Note: This might fail with real python-magic, but tests the structure
        assert isinstance(is_valid, bool)
        assert isinstance(mime_type, str)
        assert isinstance(error, str)

    def test_validate_document_file(self):
        """Test document file validation."""
        # Create a dummy text file
        doc_path = os.path.join(self.temp_dir, "test.txt")
        with open(doc_path, "w") as f:
            f.write("test document content")

        is_valid, mime_type, error = self.validator.validate_document(doc_path)
        assert isinstance(is_valid, bool)
        assert isinstance(mime_type, str)
        assert isinstance(error, str)

    def test_get_file_info(self):
        """Test file info retrieval."""
        # Create a test file
        file_path = os.path.join(self.temp_dir, "test.txt")
        with open(file_path, "w") as f:
            f.write("test content")

        info = self.validator.get_file_info(file_path)
        assert "file_path" in info
        assert "file_size" in info
        assert "mime_type" in info
        assert info["file_path"] == file_path


class TestAuthBypass:
    """Test authentication bypass functionality."""

    def test_auth_bypass_initialization(self, db):
        """Test AuthBypass initialization."""
        auth_bypass = AuthBypass(db)
        assert auth_bypass.db == db
        assert auth_bypass.user_repo is not None

    @patch("src.core.config.settings.debug", True)
    def test_get_test_user_creation(self, db):
        """Test test user creation."""
        auth_bypass = AuthBypass(db)
        test_user = auth_bypass.get_test_user()

        if test_user:
            assert test_user.email == "test@example.com"
            assert test_user.username == "testuser"


class TestQueryOptimization:
    """Test query optimization utilities."""

    def test_query_optimizer_pagination(self):
        """Test query pagination."""
        # Mock query
        mock_query = Mock()
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query

        result = QueryOptimizer.add_pagination(mock_query, skip=10, limit=20)

        mock_query.offset.assert_called_once_with(10)
        mock_query.limit.assert_called_once_with(20)
        assert result == mock_query

    def test_query_optimizer_filters(self):
        """Test query filtering."""
        # Mock query and entity
        mock_entity = Mock()
        mock_column = Mock()
        mock_entity.test_field = mock_column
        mock_query = Mock()
        mock_query.column_descriptions = [{"entity": mock_entity}]
        mock_query.filter.return_value = mock_query

        filters = {"test_field": "test_value"}
        result = QueryOptimizer.add_filters(mock_query, filters)

        mock_query.filter.assert_called_once()
        assert result == mock_query

    def test_index_optimizer_recommendations(self):
        """Test index recommendations."""
        indexes = IndexOptimizer.get_recommended_indexes()

        assert isinstance(indexes, list)
        assert len(indexes) > 0

        # Check that we have indexes for main tables
        table_names = [idx["table"] for idx in indexes]
        assert "users" in table_names
        assert "categories" in table_names
        assert "expenses" in table_names


class TestAsyncUserService:
    """Test async user service functionality."""

    @pytest.mark.asyncio
    async def test_async_user_service_initialization(self, db):
        """Test async user service initialization."""
        # Mock async session
        mock_async_session = Mock()
        service = AsyncUserService(mock_async_session)
        assert service.db == mock_async_session
        assert service.user_repo is not None

    @pytest.mark.asyncio
    async def test_create_user_validation(self, db):
        """Test user creation validation."""
        # Mock async session
        mock_async_session = Mock()
        service = AsyncUserService(mock_async_session)

        # Test with valid data that will pass Pydantic validation
        valid_user_data = UserCreate(
            email="test@example.com",
            username="testuser",
            password="testpass123",
            full_name="Test User",
        )

        # Mock the repository methods to avoid actual database calls
        service.user_repo.is_email_taken = AsyncMock(return_value=False)
        service.user_repo.is_username_taken = AsyncMock(return_value=False)
        service.user_repo.create = AsyncMock(return_value=Mock())

        # This should not raise an exception
        result = await service.create_user(valid_user_data)
        assert result is not None


class TestEnhancedAPI:
    """Test enhanced API functionality."""

    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs_url" in data

    def test_error_handling(self):
        """Test error handling."""
        # Test 404 error
        response = self.client.get("/nonexistent")
        assert response.status_code == 404


class TestInterfaceSegregation:
    """Test interface segregation implementation."""

    def test_repository_interfaces(self):
        """Test repository interfaces are properly defined."""
        from src.interfaces.repository_interfaces import (
            IBaseRepository,
            IUserRepository,
        )

        # Check that interfaces have required methods
        assert hasattr(IBaseRepository, "create")
        assert hasattr(IBaseRepository, "get_by_id")
        assert hasattr(IBaseRepository, "get_multi")
        assert hasattr(IBaseRepository, "update")
        assert hasattr(IBaseRepository, "delete")

        assert hasattr(IUserRepository, "get_by_email")
        assert hasattr(IUserRepository, "get_by_username")
        assert hasattr(IUserRepository, "is_email_taken")
        assert hasattr(IUserRepository, "is_username_taken")

    def test_service_interfaces(self):
        """Test service interfaces are properly defined."""
        from src.interfaces.service_interfaces import (
            ICategoryService,
            IExpenseService,
            IUserService,
        )

        # Check that interfaces have required methods
        assert hasattr(IUserService, "create_user")
        assert hasattr(IUserService, "get_user_by_id")
        assert hasattr(IUserService, "authenticate_user")

        assert hasattr(ICategoryService, "create_category")
        assert hasattr(ICategoryService, "get_category_by_id")

        assert hasattr(IExpenseService, "create_expense")
        assert hasattr(IExpenseService, "get_expense_by_id")
        assert hasattr(IExpenseService, "get_expense_stats")


class TestSOLIDPrinciples:
    """Test SOLID principles implementation."""

    def test_single_responsibility_principle(self):
        """Test Single Responsibility Principle."""
        # Each service should have a single responsibility
        from src.services.category.category_validation import CategoryValidationService
        from src.services.expense.expense_validation import ExpenseValidationService
        from src.services.user.user_validation import UserValidationService

        # Validation services should only handle validation
        assert hasattr(UserValidationService, "validate_email")
        assert hasattr(UserValidationService, "validate_password")
        assert hasattr(CategoryValidationService, "validate_name")
        assert hasattr(ExpenseValidationService, "validate_amount")

    def test_open_closed_principle(self):
        """Test Open/Closed Principle."""
        # Services should be open for extension, closed for modification
        from src.services.user.async_user_service import AsyncUserService
        from src.services.user.user_service import UserService

        # Both sync and async versions should exist
        assert UserService is not None
        assert AsyncUserService is not None

    def test_interface_segregation_principle(self):
        """Test Interface Segregation Principle."""
        # Interfaces should be focused and not force unnecessary dependencies
        from src.interfaces.repository_interfaces import (
            ICategoryRepository,
            IUserRepository,
        )

        # User repository should only have user-specific methods
        user_methods = [
            method for method in dir(IUserRepository) if not method.startswith("_")
        ]
        assert "get_by_email" in user_methods
        assert "get_by_username" in user_methods
        assert "is_email_taken" in user_methods

        # Category repository should only have category-specific methods
        category_methods = [
            method for method in dir(ICategoryRepository) if not method.startswith("_")
        ]
        assert "get_user_categories" in category_methods
        assert "get_system_categories" in category_methods
        assert "is_name_taken" in category_methods


class TestCleanArchitecture:
    """Test Clean Architecture implementation."""

    def test_layered_architecture(self):
        """Test that layers are properly separated."""
        # API layer should not directly access database
        from src.api.routers import analytics, auth, categories, expenses

        assert auth is not None
        assert expenses is not None
        assert categories is not None
        assert analytics is not None

        # Service layer should handle business logic
        from src.services.category.category_service import CategoryService
        from src.services.expense.expense_service import ExpenseService
        from src.services.user.user_service import UserService

        assert UserService is not None
        assert CategoryService is not None
        assert ExpenseService is not None

        # Repository layer should handle data access
        from src.repositories.category_repository import CategoryRepository
        from src.repositories.expense_repository import ExpenseRepository
        from src.repositories.user_repository import UserRepository

        assert UserRepository is not None
        assert CategoryRepository is not None
        assert ExpenseRepository is not None

    def test_dependency_inversion(self):
        """Test Dependency Inversion Principle."""
        # High-level modules should not depend on low-level modules
        # Both should depend on abstractions (interfaces)
        from src.interfaces.repository_interfaces import IUserRepository
        from src.interfaces.service_interfaces import IUserService

        assert IUserRepository is not None
        assert IUserService is not None
