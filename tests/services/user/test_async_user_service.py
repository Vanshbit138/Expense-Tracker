"""
Tests for async user service module.
"""

from src.services.user.async_user_service import AsyncUserRepository, AsyncUserService


class TestAsyncUserRepository:
    """Test cases for AsyncUserRepository."""

    def test_async_user_repository_class_exists(self):
        """Test that AsyncUserRepository class exists."""
        assert AsyncUserRepository is not None

    def test_async_user_repository_methods_exist(self):
        """Test that key methods exist in AsyncUserRepository."""
        methods = [
            "get_by_email",
            "get_by_username",
            "is_email_taken",
            "is_username_taken",
        ]

        for method in methods:
            assert hasattr(AsyncUserRepository, method)
            assert callable(getattr(AsyncUserRepository, method))


class TestAsyncUserService:
    """Test cases for AsyncUserService."""

    def test_async_user_service_class_exists(self):
        """Test that AsyncUserService class exists."""
        assert AsyncUserService is not None

    def test_async_user_service_methods_exist(self):
        """Test that key methods exist in AsyncUserService."""
        methods = [
            "create_user",
            "get_user_by_id",
            "get_user_by_email",
            "get_user_by_username",
            "get_users",
            "update_user",
            "delete_user",
            "authenticate_user",
            "change_password",
        ]

        for method in methods:
            assert hasattr(AsyncUserService, method)
            assert callable(getattr(AsyncUserService, method))

    def test_async_user_service_init_method(self):
        """Test that __init__ method exists."""
        assert hasattr(AsyncUserService, "__init__")
        assert callable(AsyncUserService.__init__)
