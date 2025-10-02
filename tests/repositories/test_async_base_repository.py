"""
Tests for async base repository module.
"""

from src.repositories.async_base_repository import AsyncBaseRepository


class TestAsyncBaseRepository:
    """Test cases for AsyncBaseRepository."""

    def test_async_base_repository_class_exists(self):
        """Test that AsyncBaseRepository class exists."""
        assert AsyncBaseRepository is not None

    def test_async_base_repository_methods_exist(self):
        """Test that key methods exist in AsyncBaseRepository."""
        methods = [
            "create",
            "get_by_id",
            "get_by_id_with_relations",
            "get_multi",
            "update",
            "delete",
            "count",
            "exists",
        ]

        for method in methods:
            assert hasattr(AsyncBaseRepository, method)
            assert callable(getattr(AsyncBaseRepository, method))

    def test_async_base_repository_init_method(self):
        """Test that __init__ method exists."""
        assert hasattr(AsyncBaseRepository, "__init__")
        assert callable(AsyncBaseRepository.__init__)
