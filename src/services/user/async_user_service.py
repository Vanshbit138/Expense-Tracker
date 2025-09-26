"""
Async user service for business logic operations.
"""

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictError, ValidationError
from src.core.logging_config import LoggerMixin
from src.models.user import User
from src.repositories.async_base_repository import AsyncBaseRepository
from src.schemas.user import UserCreate, UserUpdate
from src.schemas.user_queries import (
    AuthenticationQuery,
    PasswordChangeQuery,
    UserFilter,
    UserQuery,
    UserValidation,
)
from src.services.async_base_service import AsyncBaseService
from src.services.authentication.password_service import (
    get_password_hash,
    verify_password,
)


class AsyncUserRepository(AsyncBaseRepository[User], LoggerMixin):
    """Async user repository with user-specific operations."""

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            result = await self.db.execute(
                self.db.query(User).filter(User.email == email)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(
                "Failed to get user by email", email=email, error=str(e), exc_info=True
            )
            raise

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        try:
            result = await self.db.execute(
                self.db.query(User).filter(User.username == username)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(
                "Failed to get user by username",
                username=username,
                error=str(e),
                exc_info=True,
            )
            raise

    async def is_email_taken(
        self, email: str, exclude_user_id: Optional[int] = None
    ) -> bool:
        """Check if email is already taken."""
        try:
            query = self.db.query(User).filter(User.email == email)
            if exclude_user_id:
                query = query.filter(User.id != exclude_user_id)

            result = await self.db.execute(query)
            return result.scalar_one_or_none() is not None
        except Exception as e:
            self.logger.error(
                "Failed to check email availability",
                email=email,
                error=str(e),
                exc_info=True,
            )
            raise

    async def is_username_taken(
        self, username: str, exclude_user_id: Optional[int] = None
    ) -> bool:
        """Check if username is already taken."""
        try:
            query = self.db.query(User).filter(User.username == username)
            if exclude_user_id:
                query = query.filter(User.id != exclude_user_id)

            result = await self.db.execute(query)
            return result.scalar_one_or_none() is not None
        except Exception as e:
            self.logger.error(
                "Failed to check username availability",
                username=username,
                error=str(e),
                exc_info=True,
            )
            raise


class AsyncUserService(AsyncBaseService, LoggerMixin):
    """Async user service for business logic operations following SOLID principles."""

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.user_repo = AsyncUserRepository(User, db)

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user asynchronously."""
        await self.log_operation(
            "create_user", email=user_data.email, username=user_data.username
        )

        try:
            # Validate email uniqueness
            email_validation = UserValidation(email=user_data.email)
            await self._validate_email_unique(email_validation)

            # Validate username uniqueness
            username_validation = UserValidation(username=user_data.username)
            await self._validate_username_unique(username_validation)

            # Create user
            hashed_password = get_password_hash(user_data.password)
            user = User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
            )

            return await self.user_repo.create(user)

        except Exception as e:
            await self.log_error(
                "create_user", e, email=user_data.email, username=user_data.username
            )
            raise

    async def get_user_by_id(self, data: UserQuery) -> Optional[User]:
        """Get user by ID asynchronously."""
        await self.log_operation("get_user_by_id", user_id=data.user_id)

        try:
            return await self.user_repo.get_by_id(data.user_id)
        except Exception as e:
            await self.log_error("get_user_by_id", e, user_id=data.user_id)
            raise

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email asynchronously."""
        await self.log_operation("get_user_by_email", email=email)

        try:
            return await self.user_repo.get_by_email(email)
        except Exception as e:
            await self.log_error("get_user_by_email", e, email=email)
            raise

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username asynchronously."""
        await self.log_operation("get_user_by_username", username=username)

        try:
            return await self.user_repo.get_by_username(username)
        except Exception as e:
            await self.log_error("get_user_by_username", e, username=username)
            raise

    async def get_users(self, data: UserFilter) -> List[User]:
        """Get all users with pagination asynchronously."""
        await self.log_operation("get_users", skip=data.skip, limit=data.limit)

        try:
            return await self.user_repo.get_multi(skip=data.skip, limit=data.limit)
        except Exception as e:
            await self.log_error("get_users", e, skip=data.skip, limit=data.limit)
            raise

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user asynchronously."""
        await self.log_operation("update_user", user_id=user_id)

        try:
            # Check if user exists
            user = await self.ensure_record_exists(
                user_id, lambda uid: self.user_repo.get_by_id(uid), "User"
            )

            # Validate email uniqueness if email is being updated
            if user_data.email and user_data.email != user.email:
                email_validation = UserValidation(email=user_data.email)
                await self._validate_email_unique(
                    email_validation, exclude_user_id=user_id
                )

            # Validate username uniqueness if username is being updated
            if user_data.username and user_data.username != user.username:
                username_validation = UserValidation(username=user_data.username)
                await self._validate_username_unique(
                    username_validation, exclude_user_id=user_id
                )

            # Update user
            update_data = user_data.model_dump(exclude_unset=True)
            return await self.user_repo.update(user_id, update_data)

        except Exception as e:
            await self.log_error("update_user", e, user_id=user_id)
            raise

    async def delete_user(self, data: UserQuery) -> bool:
        """Delete user asynchronously."""
        await self.log_operation("delete_user", user_id=data.user_id)

        try:
            return await self.user_repo.delete(data.user_id)
        except Exception as e:
            await self.log_error("delete_user", e, user_id=data.user_id)
            raise

    async def authenticate_user(self, data: AuthenticationQuery) -> Optional[User]:
        """Authenticate user asynchronously."""
        await self.log_operation("authenticate_user", email=data.email)

        try:
            user = await self.user_repo.get_by_email(data.email)
            if not user:
                return None

            if not verify_password(data.password, user.hashed_password):
                return None

            return user

        except Exception as e:
            await self.log_error("authenticate_user", e, email=data.email)
            raise

    async def change_password(self, data: PasswordChangeQuery) -> bool:
        """Change user password asynchronously."""
        await self.log_operation("change_password", user_id=data.user_id)

        try:
            # Check if user exists
            user = await self.ensure_record_exists(
                data.user_id, lambda uid: self.user_repo.get_by_id(uid), "User"
            )

            # Verify current password
            if not verify_password(data.current_password, user.hashed_password):
                raise ValidationError("Current password is incorrect")

            # Update password
            hashed_password = get_password_hash(data.new_password)
            await self.user_repo.update(
                data.user_id, {"hashed_password": hashed_password}
            )

            return True

        except Exception as e:
            await self.log_error("change_password", e, user_id=data.user_id)
            raise

    async def _validate_email_unique(
        self, validation_data: UserValidation, exclude_user_id: Optional[int] = None
    ) -> None:
        """Validate email uniqueness asynchronously."""
        is_taken = await self.user_repo.is_email_taken(
            validation_data.email, exclude_user_id
        )
        if is_taken:
            raise ConflictError("Email already registered")

    async def _validate_username_unique(
        self, validation_data: UserValidation, exclude_user_id: Optional[int] = None
    ) -> None:
        """Validate username uniqueness asynchronously."""
        is_taken = await self.user_repo.is_username_taken(
            validation_data.username, exclude_user_id
        )
        if is_taken:
            raise ConflictError("Username already taken")
