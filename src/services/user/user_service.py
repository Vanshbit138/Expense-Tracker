"""
User service for business logic operations.
"""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.core.logging_config import get_logger
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
            user_data.password = hashed_password

            # Create user object
            user = User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                is_active=True,
                is_superuser=False,
            )

            user = self.user_repo.create(user)
            self.logger.info(
                "User created successfully", user_id=user.id, email=user.email
            )
            return user
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Failed to create user",
                email=user_data.email,
                error=str(e),
                exc_info=True,
            )
            raise

    def get_user_by_id(self, user_query: UserQuery) -> Optional[User]:
        """Get user by ID."""
        self.logger.debug("Fetching user by ID", user_id=user_query.user_id)
        user = self.user_repo.get_by_id(user_query.user_id)
        if user:
            self.logger.debug("User found by ID", user_id=user.id, email=user.email)
        else:
            self.logger.debug("User not found by ID", user_id=user_query.user_id)
        return user

    def get_user_by_email(self, user_query: UserQuery) -> Optional[User]:
        """Get user by email."""
        self.logger.debug("Fetching user by email", email=user_query.email)
        user = self.user_repo.get_by_email(user_query.email)
        if user:
            self.logger.debug("User found by email", user_id=user.id, email=user.email)
        else:
            self.logger.debug("User not found by email", email=user_query.email)
        return user

    def get_users(self, user_filter: UserFilter) -> List[User]:
        """Get all users with pagination and filters."""
        self.logger.debug(
            "Fetching users with filters",
            skip=user_filter.skip,
            limit=user_filter.limit,
        )
        users = self.user_repo.get_all(skip=user_filter.skip, limit=user_filter.limit)
        self.logger.debug("Users fetched successfully", count=len(users))
        return users

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update an existing user."""
        self.logger.info("Updating user", user_id=user_id)
        user = self.user_repo.get_by_id(user_id)
        if not user:
            self.logger.warning("User not found for update", user_id=user_id)
            return None

        # Update user fields
        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        user = self.user_repo.update(user)
        self.logger.info("User updated successfully", user_id=user.id, email=user.email)
        return user

    def delete_user(self, user_query: UserQuery) -> bool:
        """Delete a user."""
        self.logger.info("Deleting user", user_id=user_query.user_id)
        success = self.user_repo.delete(user_query.user_id)
        if success:
            self.logger.info("User deleted successfully", user_id=user_query.user_id)
        else:
            self.logger.warning(
                "User not found for deletion", user_id=user_query.user_id
            )
        return success

    def authenticate_user(self, auth_query: AuthenticationQuery) -> Optional[User]:
        """Authenticate user with email and password."""
        self.logger.debug("Authenticating user", email=auth_query.email)
        user = self.user_repo.get_by_email(auth_query.email)
        if not user:
            self.logger.warning(
                "Authentication failed - user not found", email=auth_query.email
            )
            return None
        if not verify_password(auth_query.password, user.hashed_password):
            self.logger.warning(
                "Authentication failed - invalid password", email=auth_query.email
            )
            return None
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
        """Validate if email is unique."""
        self.logger.debug("Validating email uniqueness", email=validation.email)
        if self.user_repo.get_by_email(validation.email):
            self.logger.warning("Email already registered", email=validation.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        self.logger.debug("Email is unique", email=validation.email)

    def _validate_username_unique(self, validation: UserValidation) -> None:
        """Validate if username is unique."""
        self.logger.debug(
            "Validating username uniqueness", username=validation.username
        )
        if self.user_repo.get_by_username(validation.username):
            self.logger.warning("Username already taken", username=validation.username)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
        self.logger.debug("Username is unique", username=validation.username)
