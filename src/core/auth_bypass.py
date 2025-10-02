"""
Authentication bypass for testing and local development.
"""

from typing import Optional

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.database import get_db
from src.core.logging_config import get_logger
from src.models.user.user import User
from src.repositories.user.user_repository import UserRepository

logger = get_logger(__name__)


class AuthBypass:
    """Authentication bypass for testing and development."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def get_test_user(self) -> Optional[User]:
        """Get or create a test user for bypass authentication."""
        try:
            # Try to get existing test user
            test_user = self.user_repo.get_by_email("test@example.com")
            if test_user:
                logger.info(
                    "Using existing test user for bypass auth", user_id=test_user.id
                )
                return test_user

            # Create test user if it doesn't exist
            from src.schemas.user.user import UserCreate
            from src.services.authentication.password_service import get_password_hash

            test_user_data = UserCreate(
                email="test@example.com",
                username="testuser",
                password="TestPass123!",
                full_name="Test User",
            )

            test_user = User(
                email=test_user_data.email,
                username=test_user_data.username,
                hashed_password=get_password_hash(test_user_data.password),
                full_name=test_user_data.full_name,
                is_active=True,
            )

            test_user = self.user_repo.create(test_user)
            logger.info("Created test user for bypass auth", user_id=test_user.id)
            return test_user

        except Exception as e:
            logger.error(
                "Failed to get/create test user for bypass auth",
                error=str(e),
                exc_info=True,
            )
            return None


def get_auth_bypass_user(
    db: Session = Depends(get_db), bypass_enabled: bool = settings.debug
) -> Optional[User]:
    """
    Get bypass authentication user for testing/development.

    This should only be used in development/testing environments.
    """
    if not bypass_enabled:
        return None

    try:
        auth_bypass = AuthBypass(db)
        return auth_bypass.get_test_user()
    except Exception as e:
        logger.error("Auth bypass failed", error=str(e), exc_info=True)
        return None


def get_current_user_with_bypass(
    credentials: Optional[str] = None,
    db: Session = Depends(get_db),
    bypass_user: Optional[User] = Depends(get_auth_bypass_user),
) -> User:
    """
    Get current user with bypass authentication support.

    This function tries normal authentication first, then falls back to bypass
    if enabled and no valid credentials are provided.
    """
    # If bypass is enabled and we have a bypass user, use it
    if bypass_user and settings.debug:
        logger.info("Using bypass authentication", user_id=bypass_user.id)
        return bypass_user

    # Otherwise, use normal authentication
    from src.core.dependencies import get_current_user

    return get_current_user(credentials, db)


def get_current_active_user_with_bypass(
    current_user: User = Depends(get_current_user_with_bypass),
) -> User:
    """
    Get current active user with bypass authentication support.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
