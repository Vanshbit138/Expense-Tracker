"""
Repository interfaces following Interface Segregation Principle.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

ModelType = TypeVar("ModelType")


class IBaseRepository(ABC, Generic[ModelType]):
    """Base repository interface with common CRUD operations."""

    @abstractmethod
    def create(self, obj_in: ModelType) -> ModelType:
        """Create a new record."""
        pass

    @abstractmethod
    def get_by_id(self, id: Any) -> Optional[ModelType]:
        """Get record by ID."""
        pass

    @abstractmethod
    def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get multiple records with pagination."""
        pass

    @abstractmethod
    def update(self, id: Any, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """Update a record."""
        pass

    @abstractmethod
    def delete(self, id: Any) -> bool:
        """Delete a record."""
        pass


class IUserRepository(ABC):
    """User-specific repository interface."""

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Any]:
        """Get user by email."""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[Any]:
        """Get user by username."""
        pass

    @abstractmethod
    def is_email_taken(self, email: str, exclude_user_id: Optional[int] = None) -> bool:
        """Check if email is already taken."""
        pass

    @abstractmethod
    def is_username_taken(
        self, username: str, exclude_user_id: Optional[int] = None
    ) -> bool:
        """Check if username is already taken."""
        pass


class ICategoryRepository(ABC):
    """Category-specific repository interface."""

    @abstractmethod
    def get_user_categories(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Any]:
        """Get categories for a specific user."""
        pass

    @abstractmethod
    def get_system_categories(self) -> List[Any]:
        """Get system categories."""
        pass

    @abstractmethod
    def is_name_taken(
        self, name: str, user_id: int, exclude_category_id: Optional[int] = None
    ) -> bool:
        """Check if category name is taken by user."""
        pass

    @abstractmethod
    def get_by_id_with_user_check(
        self, category_id: int, user_id: int
    ) -> Optional[Any]:
        """Get category by ID with user access check."""
        pass


class IExpenseRepository(ABC):
    """Expense-specific repository interface."""

    @abstractmethod
    def get_user_expenses(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Any]:
        """Get expenses for a specific user."""
        pass

    @abstractmethod
    def get_by_id_with_user_check(self, expense_id: int, user_id: int) -> Optional[Any]:
        """Get expense by ID with user access check."""
        pass

    @abstractmethod
    def get_monthly_expenses(self, user_id: int, year: int, month: int) -> List[Any]:
        """Get monthly expenses for a user."""
        pass

    @abstractmethod
    def get_expense_stats(
        self,
        user_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get expense statistics for a user."""
        pass

    @abstractmethod
    def get_category_stats(
        self,
        user_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get category statistics for a user."""
        pass


class IAsyncRepository(ABC, Generic[ModelType]):
    """Async repository interface."""

    @abstractmethod
    async def create(self, obj_in: ModelType) -> ModelType:
        """Create a new record asynchronously."""
        pass

    @abstractmethod
    async def get_by_id(self, id: Any) -> Optional[ModelType]:
        """Get record by ID asynchronously."""
        pass

    @abstractmethod
    async def get_multi(
        self, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination asynchronously."""
        pass

    @abstractmethod
    async def update(self, id: Any, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """Update a record asynchronously."""
        pass

    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Delete a record asynchronously."""
        pass

    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records asynchronously."""
        pass

    @abstractmethod
    async def exists(self, filters: Dict[str, Any]) -> bool:
        """Check if record exists asynchronously."""
        pass
