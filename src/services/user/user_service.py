"""
User service for business logic operations.
"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.schemas.user import UserCreate, UserUpdate
from src.schemas.user_queries import (
    AuthenticationQuery,
    PasswordChangeQuery,
    UserFilter,
    UserQuery,
    UserValidation,
)
from src.services.authentication.password_service import (
    get_password_hash,
    verify_password,
)


class UserService:
    """User service for business logic operations following SOLID principles."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Validate email uniqueness
        email_validation = UserValidation(email=user_data.email)
        self._validate_email_unique(email_validation)

        # Validate username uniqueness
        username_validation = UserValidation(username=user_data.username)
        self._validate_username_unique(username_validation)

        # Create user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
        )

        return self.user_repo.create(user)

    def get_user_by_id(self, data: UserQuery) -> Optional[User]:
        """Get user by ID."""
        return self.user_repo.get_by_id(data.user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.user_repo.get_by_email(email)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.user_repo.get_by_username(username)

    def get_users(self, data: UserFilter) -> List[User]:
        """Get all users with pagination."""
        return self.user_repo.get_all(data.skip, data.limit)

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None

        # Check email uniqueness if email is being updated
        if user_data.email and user_data.email != user.email:
            email_validation = UserValidation(
                email=user_data.email, exclude_user_id=user_id
            )
            self._validate_email_unique(email_validation)

        # Check username uniqueness if username is being updated
        if user_data.username and user_data.username != user.username:
            username_validation = UserValidation(
                username=user_data.username, exclude_user_id=user_id
            )
            self._validate_username_unique(username_validation)

        # Update user fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        return self.user_repo.update(user)

    def delete_user(self, data: UserQuery) -> bool:
        """Delete user."""
        return self.user_repo.delete(data.user_id)

    def authenticate_user(self, data: AuthenticationQuery) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.user_repo.get_by_email(data.email)
        if not user:
            return None

        if not verify_password(data.password, user.hashed_password):
            return None

        return user

    def change_password(self, data: PasswordChangeQuery) -> bool:
        """Change user password."""
        user = self.user_repo.get_by_id(data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Verify current password
        if not verify_password(data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        # Update password
        user.hashed_password = get_password_hash(data.new_password)
        self.user_repo.update(user)
        return True
        return True

    def _validate_email_unique(self, data: UserValidation) -> None:
        """Validate email uniqueness."""
        if data.email and self.user_repo.is_email_taken(
            data.email, exclude_user_id=data.exclude_user_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    def _validate_username_unique(self, data: UserValidation) -> None:
        """Validate username uniqueness."""
        if data.username and self.user_repo.is_username_taken(
            data.username, exclude_user_id=data.exclude_user_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )

    # Backward compatibility methods for existing tests
    def get_user_by_id_legacy(self, user_id: int) -> Optional[User]:
        """Legacy method for backward compatibility."""
        data = UserQuery(user_id=user_id)
        return self.get_user_by_id(data)

    def delete_user_legacy(self, user_id: int) -> bool:
        """Legacy method for backward compatibility."""
        data = UserQuery(user_id=user_id)
        return self.delete_user(data)

    def authenticate_user_legacy(self, email: str, password: str) -> Optional[User]:
        """Legacy method for backward compatibility."""
        data = AuthenticationQuery(email=email, password=password)
        return self.authenticate_user(data)

    def change_password_legacy(
        self, user_id: int, current_password: str, new_password: str
    ) -> bool:
        """Legacy method for backward compatibility."""
        data = PasswordChangeQuery(
            user_id=user_id,
            current_password=current_password,
            new_password=new_password,
        )
        return self.change_password(data)
