"""
User service for business logic operations.
"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.schemas.user import UserCreate, UserUpdate
from src.services.authentication.password_service import (
    get_password_hash,
    verify_password,
)


class UserService:
    """User service for business logic operations."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if email is already taken
        if self.user_repo.is_email_taken(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Check if username is already taken
        if self.user_repo.is_username_taken(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )

        # Create user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
        )

        return self.user_repo.create(user)

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.user_repo.get_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.user_repo.get_by_email(email)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.user_repo.get_by_username(username)

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        return self.user_repo.get_all(skip, limit)

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None

        # Check email uniqueness if email is being updated
        if user_data.email and user_data.email != user.email:
            if self.user_repo.is_email_taken(user_data.email, exclude_user_id=user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

        # Check username uniqueness if username is being updated
        if user_data.username and user_data.username != user.username:
            if self.user_repo.is_username_taken(
                user_data.username, exclude_user_id=user_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken",
                )

        # Update user fields
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        return self.user_repo.update(user)

    def delete_user(self, user_id: int) -> bool:
        """Delete user."""
        return self.user_repo.delete(user_id)

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.user_repo.get_by_email(email)
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    def change_password(
        self, user_id: int, current_password: str, new_password: str
    ) -> bool:
        """Change user password."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False

        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        user.hashed_password = get_password_hash(new_password)
        self.user_repo.update(user)
        return True
