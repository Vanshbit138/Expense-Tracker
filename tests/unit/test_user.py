"""
Unit tests for user service and repository.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.user.user import User
from src.schemas.user.user import UserCreate, UserUpdate
from src.schemas.user.user_queries import (
    AuthenticationQuery,
    PasswordChangeQuery,
    UserFilter,
    UserValidation,
)
from src.services.user.user_service import UserService


class TestUserService:
    """Test cases for UserService class."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return MagicMock(spec=Session)

    @pytest.fixture
    def user_service(self, mock_db_session):
        """Create a UserService instance with mocked dependencies."""
        with patch("src.services.user.user_service.UserRepository") as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo_class.return_value = mock_repo
            service = UserService(mock_db_session)
            service.user_repo = mock_repo
            return service

    def test_create_user_success(self, user_service, sample_user_create):
        """Test successful user creation."""
        # Arrange
        mock_user = User(
            id=1,
            email=sample_user_create.email,
            username=sample_user_create.username,
            full_name=sample_user_create.full_name,
            hashed_password="hashed_password",
            is_active=True,
            is_superuser=False,
        )
        user_service.user_repo.get_by_email.return_value = None
        user_service.user_repo.get_by_username.return_value = None
        user_service.user_repo.create.return_value = mock_user

        # Act
        result = user_service.create_user(sample_user_create)

        # Assert
        assert result == mock_user
        user_service.user_repo.get_by_email.assert_called_once_with(
            sample_user_create.email
        )
        user_service.user_repo.get_by_username.assert_called_once_with(
            sample_user_create.username
        )
        user_service.user_repo.create.assert_called_once()

    def test_create_user_email_already_exists(self, user_service, sample_user_create):
        """Test user creation with existing email."""
        # Arrange
        existing_user = User(id=1, email=sample_user_create.email)
        user_service.user_repo.get_by_email.return_value = existing_user

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            user_service.create_user(sample_user_create)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in exc_info.value.detail

    def test_create_user_username_already_exists(
        self, user_service, sample_user_create
    ):
        """Test user creation with existing username."""
        # Arrange
        user_service.user_repo.get_by_email.return_value = None
        existing_user = User(id=1, username=sample_user_create.username)
        user_service.user_repo.get_by_username.return_value = existing_user

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            user_service.create_user(sample_user_create)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already taken" in exc_info.value.detail

    def test_create_user_database_error(self, user_service, sample_user_create):
        """Test user creation with database error."""
        # Arrange
        user_service.user_repo.get_by_email.return_value = None
        user_service.user_repo.get_by_username.return_value = None
        user_service.user_repo.create.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            user_service.create_user(sample_user_create)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to create user" in exc_info.value.detail

    def test_get_user_by_id_success(self, user_service):
        """Test successful user retrieval by ID."""
        # Arrange
        mock_user = User(id=1, email="test@example.com")
        user_service.user_repo.get_by_id.return_value = mock_user

        # Act
        result = user_service.get_user_by_id(1)

        # Assert
        assert result == mock_user
        user_service.user_repo.get_by_id.assert_called_once_with(1)

    def test_get_user_by_id_not_found(self, user_service):
        """Test user retrieval by ID when user not found."""
        # Arrange
        user_service.user_repo.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            user_service.get_user_by_id(1)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in exc_info.value.detail

    def test_get_user_by_email_success(self, user_service):
        """Test successful user retrieval by email."""
        # Arrange
        mock_user = User(id=1, email="test@example.com")
        user_service.user_repo.get_by_email.return_value = mock_user

        # Act
        result = user_service.get_user_by_email("test@example.com")

        # Assert
        assert result == mock_user
        user_service.user_repo.get_by_email.assert_called_once_with("test@example.com")

    def test_get_user_by_email_not_found(self, user_service):
        """Test user retrieval by email when user not found."""
        # Arrange
        user_service.user_repo.get_by_email.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            user_service.get_user_by_email("test@example.com")

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in exc_info.value.detail

    def test_get_user_by_username_success(self, user_service):
        """Test successful user retrieval by username."""
        # Arrange
        mock_user = User(id=1, username="testuser")
        user_service.user_repo.get_by_username.return_value = mock_user

        # Act
        result = user_service.get_user_by_username("testuser")

        # Assert
        assert result == mock_user
        user_service.user_repo.get_by_username.assert_called_once_with("testuser")

    def test_get_user_by_username_not_found(self, user_service):
        """Test user retrieval by username when user not found."""
        # Arrange
        user_service.user_repo.get_by_username.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            user_service.get_user_by_username("testuser")

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in exc_info.value.detail

    def test_update_user_success(self, user_service):
        """Test successful user update."""
        # Arrange
        existing_user = User(
            id=1, email="old@example.com", username="olduser", full_name="Old Name"
        )
        user_service.user_repo.get_by_id.return_value = existing_user
        user_service.user_repo.get_by_email.return_value = None
        user_service.user_repo.get_by_username.return_value = None
        user_service.user_repo.update.return_value = existing_user

        update_data = UserUpdate(
            email="new@example.com", username="newuser", full_name="New Name"
        )

        # Act
        result = user_service.update_user(1, update_data)

        # Assert
        assert result == existing_user
        assert existing_user.email == "new@example.com"
        assert existing_user.username == "newuser"
        assert existing_user.full_name == "New Name"
        user_service.user_repo.update.assert_called_once_with(existing_user)

    def test_update_user_not_found(self, user_service):
        """Test user update when user not found."""
        # Arrange
        user_service.user_repo.get_by_id.return_value = None
        update_data = UserUpdate(email="new@example.com")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            user_service.update_user(1, update_data)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in exc_info.value.detail

    def test_update_user_email_already_exists(self, user_service):
        """Test user update with existing email."""
        # Arrange
        existing_user = User(id=1, email="old@example.com")
        other_user = User(id=2, email="new@example.com")
        user_service.user_repo.get_by_id.return_value = existing_user
        user_service.user_repo.get_by_email.return_value = other_user

        update_data = UserUpdate(email="new@example.com")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            user_service.update_user(1, update_data)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in exc_info.value.detail

    def test_update_user_username_already_exists(self, user_service):
        """Test user update with existing username."""
        # Arrange
        existing_user = User(id=1, username="olduser")
        other_user = User(id=2, username="newuser")
        user_service.user_repo.get_by_id.return_value = existing_user
        user_service.user_repo.get_by_email.return_value = None
        user_service.user_repo.get_by_username.return_value = other_user

        update_data = UserUpdate(username="newuser")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            user_service.update_user(1, update_data)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already taken" in exc_info.value.detail

    def test_update_user_same_email_and_username(self, user_service):
        """Test user update with same email and username (should succeed)."""
        # Arrange
        existing_user = User(id=1, email="test@example.com", username="testuser")
        user_service.user_repo.get_by_id.return_value = existing_user
        user_service.user_repo.update.return_value = existing_user

        update_data = UserUpdate(
            email="test@example.com", username="testuser"  # Same email  # Same username
        )

        # Act
        result = user_service.update_user(1, update_data)

        # Assert
        assert result == existing_user
        # Should not check for uniqueness since values are the same
        user_service.user_repo.get_by_email.assert_not_called()
        user_service.user_repo.get_by_username.assert_not_called()

    def test_delete_user_success(self, user_service):
        """Test successful user deletion."""
        # Arrange
        user_service.user_repo.delete.return_value = True

        # Act
        result = user_service.delete_user(1)

        # Assert
        assert result is True
        user_service.user_repo.delete.assert_called_once_with(1)

    def test_delete_user_not_found(self, user_service):
        """Test user deletion when user not found."""
        # Arrange
        user_service.user_repo.delete.return_value = False

        # Act
        result = user_service.delete_user(1)

        # Assert
        assert result is False

    def test_delete_user_database_error(self, user_service):
        """Test user deletion with database error."""
        # Arrange
        user_service.user_repo.delete.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            user_service.delete_user(1)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to delete user" in exc_info.value.detail

    def test_authenticate_user_success(self, user_service):
        """Test successful user authentication."""
        # Arrange
        mock_user = User(
            id=1, email="test@example.com", hashed_password="hashed_password"
        )
        user_service.user_repo.get_by_email.return_value = mock_user

        with patch("src.services.user.user_service.verify_password") as mock_verify:
            mock_verify.return_value = True

            auth_query = AuthenticationQuery(
                email="test@example.com", password="password"
            )

            # Act
            result = user_service.authenticate_user(auth_query)

            # Assert
            assert result == mock_user
            mock_verify.assert_called_once_with("password", "hashed_password")

    def test_authenticate_user_not_found(self, user_service):
        """Test user authentication when user not found."""
        # Arrange
        user_service.user_repo.get_by_email.return_value = None

        auth_query = AuthenticationQuery(email="test@example.com", password="password")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            user_service.authenticate_user(auth_query)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in exc_info.value.detail

    def test_authenticate_user_invalid_password(self, user_service):
        """Test user authentication with invalid password."""
        # Arrange
        mock_user = User(
            id=1, email="test@example.com", hashed_password="hashed_password"
        )
        user_service.user_repo.get_by_email.return_value = mock_user

        with patch("src.services.user.user_service.verify_password") as mock_verify:
            mock_verify.return_value = False

            auth_query = AuthenticationQuery(
                email="test@example.com", password="wrong_password"
            )

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                user_service.authenticate_user(auth_query)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid email or password" in exc_info.value.detail

    def test_change_password_success(self, user_service):
        """Test successful password change."""
        # Arrange
        mock_user = User(id=1, hashed_password="old_hashed_password")
        user_service.user_repo.get_by_id.return_value = mock_user
        user_service.user_repo.update.return_value = mock_user

        with patch("src.services.user.user_service.verify_password") as mock_verify:
            with patch("src.services.user.user_service.get_password_hash") as mock_hash:
                mock_verify.return_value = True
                mock_hash.return_value = "new_hashed_password"

                password_query = PasswordChangeQuery(
                    user_id=1,
                    current_password="old_password",
                    new_password="new_password",
                )

                # Act
                result = user_service.change_password(password_query)

                # Assert
                assert result is True
                assert mock_user.hashed_password == "new_hashed_password"
                mock_verify.assert_called_once_with(
                    "old_password", "old_hashed_password"
                )
                mock_hash.assert_called_once_with("new_password")
                user_service.user_repo.update.assert_called_once_with(mock_user)

    def test_change_password_user_not_found(self, user_service):
        """Test password change when user not found."""
        # Arrange
        user_service.user_repo.get_by_id.return_value = None

        password_query = PasswordChangeQuery(
            user_id=1, current_password="old_password", new_password="new_password"
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            user_service.change_password(password_query)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "User not found" in exc_info.value.detail

    def test_change_password_invalid_current_password(self, user_service):
        """Test password change with invalid current password."""
        # Arrange
        mock_user = User(id=1, hashed_password="old_hashed_password")
        user_service.user_repo.get_by_id.return_value = mock_user

        with patch("src.services.user.user_service.verify_password") as mock_verify:
            mock_verify.return_value = False

            password_query = PasswordChangeQuery(
                user_id=1,
                current_password="wrong_password",
                new_password="new_password",
            )

            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                user_service.change_password(password_query)

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Invalid current password" in exc_info.value.detail

    def test_get_users_success(self, user_service):
        """Test successful user retrieval with filtering."""
        # Arrange
        mock_users = [
            User(id=1, email="user1@example.com"),
            User(id=2, email="user2@example.com"),
        ]
        user_service.user_repo.get_all.return_value = mock_users

        user_filter = UserFilter(skip=0, limit=10)

        # Act
        result = user_service.get_users(user_filter)

        # Assert
        assert result == mock_users
        user_service.user_repo.get_all.assert_called_once_with(skip=0, limit=10)

    def test_get_users_database_error(self, user_service):
        """Test user retrieval with database error."""
        # Arrange
        user_service.user_repo.get_all.side_effect = Exception("Database error")

        user_filter = UserFilter(skip=0, limit=10)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            user_service.get_users(user_filter)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to retrieve users" in exc_info.value.detail

    def test_validate_email_unique_success(self, user_service):
        """Test email uniqueness validation when email is unique."""
        # Arrange
        user_service.user_repo.get_by_email.return_value = None

        validation = UserValidation(email="unique@example.com")

        # Act
        user_service._validate_email_unique(validation)

        # Assert - Should not raise an exception
        user_service.user_repo.get_by_email.assert_called_once_with(
            "unique@example.com"
        )

    def test_validate_email_unique_failure(self, user_service):
        """Test email uniqueness validation when email already exists."""
        # Arrange
        existing_user = User(id=1, email="existing@example.com")
        user_service.user_repo.get_by_email.return_value = existing_user

        validation = UserValidation(email="existing@example.com")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            user_service._validate_email_unique(validation)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in exc_info.value.detail

    def test_validate_username_unique_success(self, user_service):
        """Test username uniqueness validation when username is unique."""
        # Arrange
        user_service.user_repo.get_by_username.return_value = None

        validation = UserValidation(username="uniqueuser")

        # Act
        user_service._validate_username_unique(validation)

        # Assert - Should not raise an exception
        user_service.user_repo.get_by_username.assert_called_once_with("uniqueuser")

    def test_validate_username_unique_failure(self, user_service):
        """Test username uniqueness validation when username already exists."""
        # Arrange
        existing_user = User(id=1, username="existinguser")
        user_service.user_repo.get_by_username.return_value = existing_user

        validation = UserValidation(username="existinguser")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            user_service._validate_username_unique(validation)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already taken" in exc_info.value.detail


class TestUserServiceIntegration:
    """Integration tests for UserService."""

    def test_user_lifecycle(self, user_service):
        """Test complete user lifecycle: create, read, update, delete."""
        # Create user
        user_create = UserCreate(
            email="lifecycle@example.com",
            username="lifecycle",
            full_name="Lifecycle User",
            password="password123",
        )

        created_user = User(
            id=1,
            email=user_create.email,
            username=user_create.username,
            full_name=user_create.full_name,
            hashed_password="hashed_password",
        )

        user_service.user_repo.get_by_email.return_value = None
        user_service.user_repo.get_by_username.return_value = None
        user_service.user_repo.create.return_value = created_user

        result = user_service.create_user(user_create)
        assert result == created_user

        # Read user
        user_service.user_repo.get_by_id.return_value = created_user
        result = user_service.get_user_by_id(1)
        assert result == created_user

        # Update user
        update_data = UserUpdate(full_name="Updated Name")
        user_service.user_repo.update.return_value = created_user
        result = user_service.update_user(1, update_data)
        assert result == created_user

        # Delete user
        user_service.user_repo.delete.return_value = True
        result = user_service.delete_user(1)
        assert result is True

    def test_authentication_flow(self, user_service):
        """Test complete authentication flow."""
        # Create user
        user_create = UserCreate(
            email="auth@example.com", username="authuser", password="password123"
        )

        created_user = User(
            id=1,
            email=user_create.email,
            username=user_create.username,
            hashed_password="hashed_password",
        )

        user_service.user_repo.get_by_email.return_value = None
        user_service.user_repo.get_by_username.return_value = None
        user_service.user_repo.create.return_value = created_user

        user_service.create_user(user_create)

        # Authenticate user
        user_service.user_repo.get_by_email.return_value = created_user

        with patch("src.services.user.user_service.verify_password") as mock_verify:
            mock_verify.return_value = True

            auth_query = AuthenticationQuery(
                email="auth@example.com", password="password123"
            )

            result = user_service.authenticate_user(auth_query)
            assert result == created_user

        # Change password
        with patch("src.services.user.user_service.verify_password") as mock_verify:
            with patch("src.services.user.user_service.get_password_hash") as mock_hash:
                mock_verify.return_value = True
                mock_hash.return_value = "new_hashed_password"
                user_service.user_repo.update.return_value = created_user

                password_query = PasswordChangeQuery(
                    user_id=1,
                    current_password="password123",
                    new_password="newpassword123",
                )

                result = user_service.change_password(password_query)
                assert result is True
