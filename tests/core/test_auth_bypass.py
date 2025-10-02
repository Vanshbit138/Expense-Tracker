"""
Tests for auth bypass module.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from src.core.auth_bypass import (
    AuthBypass,
    get_auth_bypass_user,
    get_current_active_user_with_bypass,
    get_current_user_with_bypass,
)


class TestAuthBypass:
    """Test cases for AuthBypass class."""

    @patch("src.core.auth_bypass.UserRepository")
    def test_get_test_user_existing(self, mock_user_repo_class):
        """Test getting existing test user."""
        mock_db = MagicMock()
        mock_user_repo = MagicMock()
        mock_user_repo_class.return_value = mock_user_repo

        # Mock existing user
        existing_user = MagicMock()
        existing_user.id = 1
        existing_user.email = "test@example.com"
        existing_user.username = "testuser"
        existing_user.hashed_password = "hashed"
        existing_user.full_name = "Test User"
        existing_user.is_active = True

        mock_user_repo.get_by_email.return_value = existing_user

        auth_bypass = AuthBypass(mock_db)
        user = auth_bypass.get_test_user()

        assert user == existing_user
        mock_user_repo.get_by_email.assert_called_once_with("test@example.com")

    @patch("src.core.auth_bypass.UserRepository")
    @patch("src.services.authentication.password_service.get_password_hash")
    def test_get_test_user_create_new(self, mock_hash, mock_user_repo_class):
        """Test creating new test user."""
        mock_db = MagicMock()
        mock_user_repo = MagicMock()
        mock_user_repo_class.return_value = mock_user_repo

        # Mock no existing user
        mock_user_repo.get_by_email.return_value = None
        mock_hash.return_value = "hashed_password"

        new_user = MagicMock()
        new_user.id = 1
        new_user.email = "test@example.com"
        new_user.username = "testuser"
        new_user.hashed_password = "hashed_password"
        new_user.full_name = "Test User"
        new_user.is_active = True

        mock_user_repo.create.return_value = new_user

        auth_bypass = AuthBypass(mock_db)
        user = auth_bypass.get_test_user()

        assert user == new_user
        mock_user_repo.create.assert_called_once()

    @patch("src.core.auth_bypass.UserRepository")
    def test_get_test_user_exception(self, mock_user_repo_class):
        """Test exception handling in get_test_user."""
        mock_db = MagicMock()
        mock_user_repo = MagicMock()
        mock_user_repo_class.return_value = mock_user_repo

        # Mock exception
        mock_user_repo.get_by_email.side_effect = Exception("Database error")

        auth_bypass = AuthBypass(mock_db)
        user = auth_bypass.get_test_user()

        assert user is None


class TestAuthBypassFunctions:
    """Test cases for auth bypass functions."""

    @patch("src.core.auth_bypass.settings")
    @patch("src.core.auth_bypass.AuthBypass")
    def test_get_auth_bypass_user_enabled(self, mock_auth_bypass_class, mock_settings):
        """Test get_auth_bypass_user when bypass is enabled."""
        mock_settings.debug = True
        mock_db = MagicMock()

        test_user = MagicMock()
        test_user.id = 1
        test_user.email = "test@example.com"
        test_user.username = "testuser"
        test_user.hashed_password = "hashed"
        test_user.is_active = True

        mock_auth_bypass = MagicMock()
        mock_auth_bypass.get_test_user.return_value = test_user
        mock_auth_bypass_class.return_value = mock_auth_bypass

        result = get_auth_bypass_user(mock_db, bypass_enabled=True)

        assert result == test_user

    def test_get_auth_bypass_user_disabled(self):
        """Test get_auth_bypass_user when bypass is disabled."""
        mock_db = MagicMock()
        result = get_auth_bypass_user(mock_db, bypass_enabled=False)
        assert result is None

    @patch("src.core.auth_bypass.settings")
    def test_get_current_user_with_bypass_uses_bypass(self, mock_settings):
        """Test get_current_user_with_bypass uses bypass when available."""
        mock_settings.debug = True
        mock_db = MagicMock()

        bypass_user = MagicMock()
        bypass_user.id = 1
        bypass_user.email = "test@example.com"
        bypass_user.username = "testuser"
        bypass_user.hashed_password = "hashed"
        bypass_user.is_active = True

        result = get_current_user_with_bypass(
            credentials=None, db=mock_db, bypass_user=bypass_user
        )

        assert result == bypass_user

    @patch("src.core.auth_bypass.settings")
    @patch("src.core.dependencies.get_current_user")
    def test_get_current_user_with_bypass_normal_auth(
        self, mock_get_current_user, mock_settings
    ):
        """Test get_current_user_with_bypass falls back to normal auth."""
        mock_settings.debug = False
        mock_db = MagicMock()

        normal_user = MagicMock()
        normal_user.id = 2
        normal_user.email = "user@example.com"
        normal_user.username = "normaluser"
        normal_user.hashed_password = "hashed"
        normal_user.is_active = True
        mock_get_current_user.return_value = normal_user

        result = get_current_user_with_bypass(
            credentials="token", db=mock_db, bypass_user=None
        )

        assert result == normal_user

    def test_get_current_active_user_with_bypass_active(self):
        """Test get_current_active_user_with_bypass with active user."""
        active_user = MagicMock()
        active_user.is_active = True

        result = get_current_active_user_with_bypass(active_user)
        assert result == active_user

    def test_get_current_active_user_with_bypass_inactive(self):
        """Test get_current_active_user_with_bypass with inactive user."""
        inactive_user = MagicMock()
        inactive_user.is_active = False

        with pytest.raises(HTTPException) as exc_info:
            get_current_active_user_with_bypass(inactive_user)

        assert exc_info.value.status_code == 400
        assert "Inactive user" in str(exc_info.value.detail)
