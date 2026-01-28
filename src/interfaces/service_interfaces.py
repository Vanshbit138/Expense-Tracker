"""
Service interfaces following Interface Segregation Principle.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class IUserService(ABC):
    """User service interface."""

    @abstractmethod
    def create_user(self, user_data: Any) -> Any:
        """Create a new user."""
        pass

    @abstractmethod
    def get_user_by_id(self, data: Any) -> Optional[Any]:
        """Get user by ID."""
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[Any]:
        """Get user by email."""
        pass

    @abstractmethod
    def authenticate_user(self, data: Any) -> Optional[Any]:
        """Authenticate user."""
        pass

    @abstractmethod
    def change_password(self, data: Any) -> bool:
        """Change user password."""
        pass


class ICategoryService(ABC):
    """Category service interface."""

    @abstractmethod
    def create_category(self, user_id: int, category_data: Any) -> Any:
        """Create a new category."""
        pass

    @abstractmethod
    def get_category_by_id(self, data: Any) -> Optional[Any]:
        """Get category by ID."""
        pass

    @abstractmethod
    def get_user_categories(self, data: Any) -> List[Any]:
        """Get user categories."""
        pass

    @abstractmethod
    def update_category(
        self, category_id: int, user_id: int, category_data: Any
    ) -> Optional[Any]:
        """Update category."""
        pass

    @abstractmethod
    def delete_category(self, data: Any) -> bool:
        """Delete category."""
        pass


class IExpenseService(ABC):
    """Expense service interface."""

    @abstractmethod
    def create_expense(self, user_id: int, expense_data: Any) -> Any:
        """Create a new expense."""
        pass

    @abstractmethod
    def get_expense_by_id(self, data: Any) -> Optional[Any]:
        """Get expense by ID."""
        pass

    @abstractmethod
    def get_user_expenses(self, data: Any) -> List[Any]:
        """Get user expenses."""
        pass

    @abstractmethod
    def update_expense(
        self, expense_id: int, user_id: int, expense_data: Any
    ) -> Optional[Any]:
        """Update expense."""
        pass

    @abstractmethod
    def delete_expense(self, data: Any) -> bool:
        """Delete expense."""
        pass

    @abstractmethod
    def get_expense_stats(self, data: Any) -> Dict[str, Any]:
        """Get expense statistics."""
        pass

    @abstractmethod
    def get_category_stats(self, data: Any) -> List[Dict[str, Any]]:
        """Get category statistics."""
        pass

    @abstractmethod
    def get_monthly_analytics(self, data: Any) -> Dict[str, Any]:
        """Get monthly analytics."""
        pass


class IAsyncUserService(ABC):
    """Async user service interface."""

    @abstractmethod
    async def create_user(self, user_data: Any) -> Any:
        """Create a new user asynchronously."""
        pass

    @abstractmethod
    async def get_user_by_id(self, data: Any) -> Optional[Any]:
        """Get user by ID asynchronously."""
        pass

    @abstractmethod
    async def authenticate_user(self, data: Any) -> Optional[Any]:
        """Authenticate user asynchronously."""
        pass


class IAsyncCategoryService(ABC):
    """Async category service interface."""

    @abstractmethod
    async def create_category(self, user_id: int, category_data: Any) -> Any:
        """Create a new category asynchronously."""
        pass

    @abstractmethod
    async def get_category_by_id(self, data: Any) -> Optional[Any]:
        """Get category by ID asynchronously."""
        pass

    @abstractmethod
    async def get_user_categories(self, data: Any) -> List[Any]:
        """Get user categories asynchronously."""
        pass


class IAsyncExpenseService(ABC):
    """Async expense service interface."""

    @abstractmethod
    async def create_expense(self, user_id: int, expense_data: Any) -> Any:
        """Create a new expense asynchronously."""
        pass

    @abstractmethod
    async def get_expense_by_id(self, data: Any) -> Optional[Any]:
        """Get expense by ID asynchronously."""
        pass

    @abstractmethod
    async def get_user_expenses(self, data: Any) -> List[Any]:
        """Get user expenses asynchronously."""
        pass

    @abstractmethod
    async def get_expense_stats(self, data: Any) -> Dict[str, Any]:
        """Get expense statistics asynchronously."""
        pass


class IValidationService(ABC):
    """Validation service interface."""

    @abstractmethod
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        pass

    @abstractmethod
    def validate_password(self, password: str) -> bool:
        """Validate password strength."""
        pass

    @abstractmethod
    def validate_username(self, username: str) -> bool:
        """Validate username format."""
        pass


class IFileValidationService(ABC):
    """File validation service interface."""

    @abstractmethod
    def validate_file(
        self, file_path: str, allowed_types: List[str], max_size: Optional[int] = None
    ) -> bool:
        """Validate file type and size."""
        pass

    @abstractmethod
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information."""
        pass
