"""
Tests for UserService.
"""

from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException, status

from src.models.user.user import User
from src.schemas.authentication.auth import UserLogin, UserRegister
from src.schemas.user.user_queries import PasswordChangeQuery
from src.services.user.user_service import UserService


class TestUserService:
    """Test cases for UserService."""

    def test_create_user_success(self, mock_db_session):
        """Test successful user creation."""
        # Mock repository
        mock_repo = Mock()
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.full_name = "Test User"
        mock_user.is_active = True
        mock_user.is_superuser = False
        mock_repo.create.return_value = mock_user
        mock_repo.get_by_email.return_value = None  # Email not taken
        mock_repo.get_by_username.return_value = None  # Username not taken

        user_data = UserRegister(
            email="test@example.com",
            username="testuser",
            password="TestPassword123!",
            full_name="Test User",
        )

        with patch(
            "src.services.user.user_service.UserRepository", return_value=mock_repo
        ):
            user_service = UserService(mock_db_session)
            result = user_service.create_user(user_data)

        assert result.id == 1
        assert result.email == "test@example.com"
        assert result.username == "testuser"
        assert result.full_name == "Test User"
        assert result.is_active is True
        assert result.is_superuser is False

    def test_create_user_duplicate_email(self, mock_db_session):
        """Test user creation with duplicate email."""
        # Mock repository
        mock_repo = Mock()
        mock_existing_user = Mock(spec=User)
        mock_repo.get_by_email.return_value = mock_existing_user  # Email already taken

        user_data = UserRegister(
            email="test@example.com",
            username="testuser",
            password="TestPassword123!",
            full_name="Test User",
        )

        with patch(
            "src.services.user.user_service.UserRepository", return_value=mock_repo
        ):
            user_service = UserService(mock_db_session)

            with pytest.raises(HTTPException) as exc_info:
                user_service.create_user(user_data)

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Email already registered" in exc_info.value.detail

    def test_create_user_duplicate_username(self, mock_db_session):
        """Test user creation with duplicate username."""
        # Mock repository
        mock_repo = Mock()
        mock_repo.get_by_email.return_value = None  # Email not taken
        mock_existing_user = Mock(spec=User)
        mock_repo.get_by_username.return_value = (
            mock_existing_user  # Username already taken
        )

        user_data = UserRegister(
            email="test@example.com",
            username="testuser",
            password="TestPassword123!",
            full_name="Test User",
        )

        with patch(
            "src.services.user.user_service.UserRepository", return_value=mock_repo
        ):
            user_service = UserService(mock_db_session)

            with pytest.raises(HTTPException) as exc_info:
                user_service.create_user(user_data)

            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
            assert "Username already taken" in exc_info.value.detail

    def test_get_user_by_id_success(self, mock_db_session):
        """Test getting user by ID successfully."""
        # Mock repository
        mock_repo = Mock()
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_repo.get_by_id.return_value = mock_user

        with patch(
            "src.services.user.user_service.UserRepository", return_value=mock_repo
        ):
            user_service = UserService(mock_db_session)
            result = user_service.get_user_by_id(1)

        assert result.id == 1
        assert result.email == "test@example.com"

    def test_get_user_by_id_not_found(self, mock_db_session):
        """Test getting user by ID when user doesn't exist."""
        # Mock repository
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = None

        with patch(
            "src.services.user.user_service.UserRepository", return_value=mock_repo
        ):
            user_service = UserService(mock_db_session)

            with pytest.raises(HTTPException) as exc_info:
                user_service.get_user_by_id(999)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "User not found" in exc_info.value.detail

    def test_get_user_by_email_success(self, mock_db_session):
        """Test getting user by email successfully."""
        # Mock repository
        mock_repo = Mock()
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_repo.get_by_email.return_value = mock_user

        with patch(
            "src.services.user.user_service.UserRepository", return_value=mock_repo
        ):
            user_service = UserService(mock_db_session)
            result = user_service.get_user_by_email("test@example.com")

        assert result.id == 1
        assert result.email == "test@example.com"

    def test_get_user_by_email_not_found(self, mock_db_session):
        """Test getting user by email when user doesn't exist."""
        # Mock repository
        mock_repo = Mock()
        mock_repo.get_by_email.return_value = None

        with patch(
            "src.services.user.user_service.UserRepository", return_value=mock_repo
        ):
            user_service = UserService(mock_db_session)

            with pytest.raises(HTTPException) as exc_info:
                user_service.get_user_by_email("nonexistent@example.com")

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "User not found" in exc_info.value.detail

    def test_get_user_by_username_success(self, mock_db_session):
        """Test getting user by username successfully."""
        # Mock repository
        mock_repo = Mock()
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.username = "testuser"
        mock_repo.get_by_username.return_value = mock_user

        with patch(
            "src.services.user.user_service.UserRepository", return_value=mock_repo
        ):
            user_service = UserService(mock_db_session)
            result = user_service.get_user_by_username("testuser")

        assert result.id == 1
        assert result.username == "testuser"

    def test_get_user_by_username_not_found(self, mock_db_session):
        """Test getting user by username when user doesn't exist."""
        # Mock repository
        mock_repo = Mock()
        mock_repo.get_by_username.return_value = None

        with patch(
            "src.services.user.user_service.UserRepository", return_value=mock_repo
        ):
            user_service = UserService(mock_db_session)

            with pytest.raises(HTTPException) as exc_info:
                user_service.get_user_by_username("nonexistentuser")

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "User not found" in exc_info.value.detail

    def test_authenticate_user_success(self, mock_db_session):
        """Test successful user authentication."""
        # Mock repository
        mock_repo = Mock()
        mock_user = Mock(spec=User)
        mock_user.email = "test@example.com"
        mock_user.hashed_password = "hashed_password"
        mock_user.is_active = True
        mock_repo.get_by_email.return_value = mock_user

        auth_query = UserLogin(email="test@example.com", password="password")

        with patch(
            "src.services.user.user_service.UserRepository", return_value=mock_repo
        ):
            with patch(
                "src.services.user.user_service.verify_password", return_value=True
            ):
                user_service = UserService(mock_db_session)
                result = user_service.authenticate_user(auth_query)

        assert result == mock_user

    def test_authenticate_user_wrong_password(self, mock_db_session):
        """Test user authentication with wrong password."""
        # Mock user
        mock_repo = Mock()
        mock_user = Mock(spec=User)
        mock_user.email = "test@example.com"
        mock_user.hashed_password = "hashed_password"
        mock_user.is_active = True
        mock_repo.get_by_email.return_value = mock_user

        auth_query = UserLogin(email="test@example.com", password="wrong_password")

        with patch(
            "src.services.user.user_service.UserRepository", return_value=mock_repo
        ):
            with patch(
                "src.services.user.user_service.verify_password", return_value=False
            ):
                user_service = UserService(mock_db_session)

                with pytest.raises(HTTPException) as exc_info:
                    user_service.authenticate_user(auth_query)

                assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticate_user_inactive(self, mock_db_session):
        """Test user authentication with inactive user."""
        # Mock inactive user
        mock_repo = Mock()
        mock_user = Mock(spec=User)
        mock_user.email = "test@example.com"
        mock_user.hashed_password = "hashed_password"
        mock_user.is_active = False
        mock_repo.get_by_email.return_value = mock_user

        auth_query = UserLogin(email="test@example.com", password="password")

        with patch(
            "src.services.user.user_service.UserRepository", return_value=mock_repo
        ):
            user_service = UserService(mock_db_session)

            with pytest.raises(HTTPException) as exc_info:
                user_service.authenticate_user(auth_query)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticate_user_not_found(self, mock_db_session):
        """Test user authentication when user doesn't exist."""
        # Mock repository
        mock_repo = Mock()
        mock_repo.get_by_email.return_value = None

        auth_query = UserLogin(email="nonexistent@example.com", password="password")

        with patch(
            "src.services.user.user_service.UserRepository", return_value=mock_repo
        ):
            user_service = UserService(mock_db_session)

            with pytest.raises(HTTPException) as exc_info:
                user_service.authenticate_user(auth_query)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password_success(self, mock_db_session):
        """Test successful password change."""
        # Mock repository
        mock_repo = Mock()
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.hashed_password = "old_hashed_password"
        mock_repo.get_by_id.return_value = mock_user
        mock_repo.update.return_value = mock_user

        password_query = PasswordChangeQuery(
            user_id=1, current_password="old_password", new_password="NewPassword123!"
        )

        with patch(
            "src.services.user.user_service.UserRepository", return_value=mock_repo
        ):
            with patch(
                "src.services.user.user_service.verify_password", return_value=True
            ):
                with patch(
                    "src.services.user.user_service.get_password_hash",
                    return_value="new_hashed_password",
                ):
                    user_service = UserService(mock_db_session)
                    result = user_service.change_password(password_query)

        assert result is True
        assert mock_user.hashed_password == "new_hashed_password"
        mock_repo.update.assert_called_once_with(mock_user)

    def test_change_password_wrong_current_password(self, mock_db_session):
        """Test password change with wrong current password."""
        # Mock repository
        mock_repo = Mock()
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.hashed_password = "old_hashed_password"
        mock_repo.get_by_id.return_value = mock_user

        password_query = PasswordChangeQuery(
            user_id=1, current_password="wrong_password", new_password="NewPassword123!"
        )

        with patch(
            "src.services.user.user_service.UserRepository", return_value=mock_repo
        ):
            with patch(
                "src.services.user.user_service.verify_password", return_value=False
            ):
                user_service = UserService(mock_db_session)

                with pytest.raises(HTTPException) as exc_info:
                    user_service.change_password(password_query)

                assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
                assert "Invalid current password" in exc_info.value.detail

    def test_change_password_user_not_found(self, mock_db_session):
        """Test password change when user doesn't exist."""
        # Mock repository
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = None

        password_query = PasswordChangeQuery(
            user_id=999, current_password="old_password", new_password="NewPassword123!"
        )

        with patch(
            "src.services.user.user_service.UserRepository", return_value=mock_repo
        ):
            user_service = UserService(mock_db_session)

            with pytest.raises(HTTPException) as exc_info:
                user_service.change_password(password_query)

            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "User not found" in exc_info.value.detail

    def test_update_user_success(self, mock_db_session):
        """Test successful user update."""
        # Mock repository
        mock_repo = Mock()
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"
        mock_user.full_name = "Test User"
        mock_repo.get_by_id.return_value = mock_user
        mock_repo.update.return_value = mock_user
        mock_repo.get_by_email.return_value = None  # Email not taken

        # Create a mock object that behaves like a Pydantic model
        from types import SimpleNamespace

        update_data = SimpleNamespace()
        update_data.full_name = "Updated Name"
        update_data.email = "updated@example.com"
        update_data.username = None  # Add username attribute
        update_data.is_active = None  # Add is_active attribute
        update_data.is_superuser = None  # Add is_superuser attribute

        with patch(
            "src.services.user.user_service.UserRepository", return_value=mock_repo
        ):
            user_service = UserService(mock_db_session)
            result = user_service.update_user(1, update_data)

        assert result == mock_user
        assert mock_user.full_name == "Updated Name"
        assert mock_user.email == "updated@example.com"
        mock_repo.update.assert_called_once_with(mock_user)

    def test_delete_user_success(self, mock_db_session):
        """Test successful user deletion."""
        # Mock repository
        mock_repo = Mock()
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_repo.get_by_id.return_value = mock_user
        mock_repo.delete.return_value = True

        with patch(
            "src.services.user.user_service.UserRepository", return_value=mock_repo
        ):
            user_service = UserService(mock_db_session)
            result = user_service.delete_user(1)

        assert result is True
        mock_repo.delete.assert_called_once_with(1)

    def test_delete_user_not_found(self, mock_db_session):
        """Test user deletion when user doesn't exist."""
        # Mock repository
        mock_repo = Mock()
        mock_repo.delete.return_value = (
            False  # Repository returns False for non-existent user
        )

        with patch(
            "src.services.user.user_service.UserRepository", return_value=mock_repo
        ):
            user_service = UserService(mock_db_session)
            result = user_service.delete_user(999)

        assert result is False
