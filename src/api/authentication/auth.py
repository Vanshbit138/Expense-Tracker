"""
Authentication router for user registration, login, and password management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.dependencies import get_current_active_user
from src.core.logging_config import get_logger
from src.models.user.user import User
from src.schemas.authentication.auth import PasswordChange, UserLogin, UserRegister
from src.schemas.user.user_queries import AuthenticationQuery, PasswordChangeQuery
from src.services.authentication.jwt_service import create_access_token
from src.services.user.user_service import UserService

# Initialize router and logger
router = APIRouter()
logger = get_logger(__name__)


@router.post("/register", response_model=dict, status_code=201)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    logger.info(
        "User registration request", email=user_data.email, username=user_data.username
    )

    try:
        user_service = UserService(db)
        user = user_service.create_user(user_data)

        logger.info("User registered successfully", user_id=user.id, email=user.email)
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }
    except HTTPException as e:
        logger.warning(
            "User registration failed", email=user_data.email, error=e.detail
        )
        raise
    except Exception as e:
        logger.error(
            "User registration failed with unexpected error",
            email=user_data.email,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration",
        )


@router.post("/login", response_model=dict)
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token."""
    logger.info("User login request", email=login_data.email)

    try:
        user_service = UserService(db)
        auth_query = AuthenticationQuery(
            email=login_data.email, password=login_data.password
        )
        user = user_service.authenticate_user(auth_query)

        if not user:
            logger.warning("Login failed - invalid credentials", email=login_data.email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        access_token = create_access_token(subject=str(user.id))
        logger.info("User logged in successfully", user_id=user.id, email=user.email)

        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Login failed with unexpected error",
            email=login_data.email,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login",
        )


@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    logger.info("User info request", user_id=current_user.id, email=current_user.email)

    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_superuser": current_user.is_superuser,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
    }


@router.post("/change-password", response_model=dict)
async def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Change user password."""
    logger.info("Password change request", user_id=current_user.id)

    try:
        user_service = UserService(db)
        password_query = PasswordChangeQuery(
            user_id=current_user.id,
            current_password=password_data.current_password,
            new_password=password_data.new_password,
        )

        success = user_service.change_password(password_query)
        if success:
            logger.info("Password changed successfully", user_id=current_user.id)
            return {"message": "Password changed successfully"}
        else:
            logger.error("Password change failed", user_id=current_user.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to change password",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Password change failed with unexpected error",
            user_id=current_user.id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during password change",
        )
