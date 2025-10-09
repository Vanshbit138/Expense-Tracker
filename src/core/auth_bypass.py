"""
Authentication bypass for testing and local development.
"""

from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.core.config import get_settings
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
    db: Session = Depends(get_db), bypass_enabled: bool = None
) -> Optional[User]:
    """
    Get bypass authentication user for testing/development.

    This should only be used in development/testing environments.
    """
    if bypass_enabled is None:
        bypass_enabled = get_settings().debug

    if not bypass_enabled:
        return None

    try:
        # Handle the case where db might be a Depends object
        if hasattr(db, "__call__") and not hasattr(db, "query"):
            # This is a Depends object, we need to resolve it
            from src.core.database import get_db

            db = next(get_db())

        # Create a simple test user without database operations
        from src.models.user.user import User
        from src.services.authentication.password_service import get_password_hash

        test_user = User(
            id=999999,  # Use a high ID to avoid conflicts
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("TestPass123!"),
            full_name="Test User",
            is_active=True,
            is_superuser=False,
        )

        logger.info("Using bypass authentication", user_id=test_user.id)
        return test_user

    except Exception as e:
        logger.critical(
            "Authentication system failure - bypass mechanism failed",
            error=str(e),
            exc_info=True,
        )
        return None


def get_current_user_with_bypass(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db),
    bypass_user: Optional[User] = Depends(get_auth_bypass_user),
) -> User:
    """
    Get current user with bypass authentication support.

    This function tries normal authentication first, then falls back to bypass
    if enabled and no valid credentials are provided.
    """
    # Try normal authentication first if credentials are provided
    if credentials:
        from src.core.dependencies import get_current_user

        return get_current_user(credentials, db)

    # If no credentials, try bypass (only if enabled)
    if bypass_user:
        logger.info("Using bypass authentication", user_id=bypass_user.id)
        return bypass_user

    # If no credentials and no bypass, raise authentication error
    from fastapi import HTTPException, status

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_active_user_with_bypass(
    current_user: User = Depends(get_current_user_with_bypass),
) -> User:
    """
    Get current active user with bypass authentication support.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
