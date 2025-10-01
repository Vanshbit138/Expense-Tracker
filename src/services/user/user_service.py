"""
User service for business logic operations.
"""

from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.core.logging_config import get_logger
from src.models.user.user import User
from src.repositories.user.user_repository import UserRepository
from src.schemas.user.user import UserCreate, UserUpdate
from src.schemas.user.user_queries import (
    AuthenticationQuery,
    PasswordChangeQuery,
    UserFilter,
    UserValidation,
)
from src.services.authentication.password_service import (
    get_password_hash,
    verify_password,
)

# Initialize logger
logger = get_logger(__name__)


class UserService:
    """User service for business logic operations following SOLID principles."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.logger = get_logger(self.__class__.__name__)

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        self.logger.info(
            "Creating new user", email=user_data.email, username=user_data.username
        )

        try:
            # Validate email uniqueness
            email_validation = UserValidation(email=user_data.email)
            self._validate_email_unique(email_validation)

            # Validate username uniqueness
            username_validation = UserValidation(username=user_data.username)
            self._validate_username_unique(username_validation)

            # Hash password
            hashed_password = get_password_hash(user_data.password)

            # Create user object
            user = User(
                email=user_data.email,
                username=user_data.username,
                full_name=user_data.full_name,
                hashed_password=hashed_password,
                is_active=True,
                is_superuser=False,
            )

            # Save to database
            created_user = self.user_repo.create(user)

            self.logger.info(
                "User created successfully",
                user_id=created_user.id,
                email=created_user.email,
            )
            return created_user

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to create user",
                email=user_data.email,
                error=str(e),
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user",
            )

    def get_user_by_id(self, user_id: int) -> User:
        """Get user by ID."""
        self.logger.debug("Getting user by ID", user_id=user_id)
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    def get_user_by_email(self, email: str) -> User:
        """Get user by email."""
        self.logger.debug("Getting user by email", email=email)
        user = self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    def get_user_by_username(self, username: str) -> User:
        """Get user by username."""
        self.logger.debug("Getting user by username", username=username)
        user = self.user_repo.get_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user information."""
        self.logger.info("Updating user", user_id=user_id)

        try:
            # Get the user first
            user = self.user_repo.get_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            # Update fields if provided
            if user_data.email is not None:
                if user_data.email != user.email:
                    email_validation = UserValidation(email=user_data.email)
                    self._validate_email_unique(email_validation)
                user.email = user_data.email

            if user_data.username is not None:
                if user_data.username != user.username:
                    username_validation = UserValidation(username=user_data.username)
                    self._validate_username_unique(username_validation)
                user.username = user_data.username

            if user_data.full_name is not None:
                user.full_name = user_data.full_name

            if user_data.is_active is not None:
                user.is_active = user_data.is_active

            # Save changes
            updated_user = self.user_repo.update(user)

            self.logger.info("User updated successfully", user_id=updated_user.id)
            return updated_user

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to update user", user_id=user_id, error=str(e), exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user",
            )

    def delete_user(self, user_id: int) -> bool:
        """Delete user."""
        self.logger.info("Deleting user", user_id=user_id)

        try:
            success = self.user_repo.delete(user_id)

            if success:
                self.logger.info("User deleted successfully", user_id=user_id)
            else:
                self.logger.warning("Failed to delete user", user_id=user_id)

            return success

        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to delete user", user_id=user_id, error=str(e), exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user",
            )

    def authenticate_user(self, auth_query: AuthenticationQuery) -> User:
        """Authenticate user with email and password."""
        self.logger.debug("Authenticating user", email=auth_query.email)
        user = self.user_repo.get_by_email(auth_query.email)
        if not user:
            self.logger.warning(
                "Authentication failed - user not found", email=auth_query.email
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        if not verify_password(auth_query.password, user.hashed_password):
            self.logger.warning(
                "Authentication failed - invalid password", email=auth_query.email
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        self.logger.info(
            "User authenticated successfully", user_id=user.id, email=user.email
        )
        return user

    def change_password(self, password_query: PasswordChangeQuery) -> bool:
        """Change user password."""
        self.logger.info("Changing password for user", user_id=password_query.user_id)
        user = self.user_repo.get_by_id(password_query.user_id)
        if not user:
            self.logger.error(
                "Password change failed - user not found",
                user_id=password_query.user_id,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if not verify_password(password_query.current_password, user.hashed_password):
            self.logger.warning(
                "Password change failed - invalid current password", user_id=user.id
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid current password",
            )

        new_hashed_password = get_password_hash(password_query.new_password)
        user.hashed_password = new_hashed_password
        self.user_repo.update(user)

        self.logger.info("Password successfully changed", user_id=user.id)
        return True

    def _validate_email_unique(self, validation: UserValidation) -> None:
        """Validate email uniqueness."""
        existing_user = self.user_repo.get_by_email(validation.email)
        if existing_user:
            self.logger.warning(
                "Email validation failed - email already exists", email=validation.email
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    def _validate_username_unique(self, validation: UserValidation) -> None:
        """Validate username uniqueness."""
        existing_user = self.user_repo.get_by_username(validation.username)
        if existing_user:
            self.logger.warning(
                "Username validation failed - username already exists",
                username=validation.username,
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    def get_users(self, query: UserFilter) -> List[User]:
        """Get users with filtering and pagination."""
        self.logger.debug("Getting users", filters=query.model_dump())

        try:
            users = self.user_repo.get_all(skip=query.skip, limit=query.limit)

            self.logger.debug("Users retrieved successfully", count=len(users))
            return users

        except Exception as e:
            self.logger.error("Failed to get users", error=str(e), exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve users",
            )
