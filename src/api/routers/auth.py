"""
Authentication router for user registration, login, and profile management.
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.dependencies import get_current_active_user
from src.core.security import create_access_token
from src.models.user import User
from src.schemas.auth import (
    PasswordChange,
    Token,
    UserLogin,
    UserRegister,
    UserResponse,
)
from src.schemas.user_queries import AuthenticationQuery, PasswordChangeQuery
from src.services.user.user_service import UserService

router = APIRouter()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    user_service = UserService(db)
    user = user_service.create_user(user_data)
    return user


@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token."""
    user_service = UserService(db)

    # Use Pydantic model for parameter validation
    auth_query = AuthenticationQuery(
        email=user_credentials.email, password=user_credentials.password
    )
    user = user_service.authenticate_user(auth_query)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=1440)  # 24 hours
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/change-password")
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Change user password."""
    user_service = UserService(db)

    # Use Pydantic model for parameter validation
    password_query = PasswordChangeQuery(
        user_id=current_user.id,
        current_password=password_data.current_password,
        new_password=password_data.new_password,
    )
    user_service.change_password(password_query)

    return {"message": "Password changed successfully"}


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    user_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update current user profile."""
    user_service = UserService(db)
    updated_user = user_service.update_user(current_user.id, user_data)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return updated_user
