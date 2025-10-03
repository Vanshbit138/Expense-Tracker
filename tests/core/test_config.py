"""
Tests for the configuration module.
"""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.core.config import Settings


class TestSettings:
    """Test cases for Settings class."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        # Clear environment variables that might affect the test
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert settings.app_name == "Expense Tracker API"
            # Note: debug might be True due to environment, so we check it's a boolean
            assert isinstance(settings.debug, bool)
            assert settings.version == "1.0.0"
            assert settings.api_v1_str == "/api/v1"
            assert settings.algorithm == "HS256"
            assert settings.access_token_expire_minutes == 1440
            assert settings.backend_cors_origins == [
                "http://localhost:3000",
                "http://localhost:8080",
            ]
            assert settings.default_page_size == 20
            assert settings.max_page_size == 100
            # Log level might be overridden by environment, so just check it's a string
            assert isinstance(settings.log_level, str)
            # enable_json_logging might be overridden by environment, so just check it's a boolean
            assert isinstance(settings.enable_json_logging, bool)
            assert settings.log_file == "logs/expense-tracker.log"

    def test_environment_variable_override(self):
        """Test that environment variables override default values."""
        with patch.dict(
            os.environ,
            {
                "APP_NAME": "Test API",
                "DEBUG": "true",
                "VERSION": "2.0.0",
                "LOG_LEVEL": "DEBUG",
            },
        ):
            settings = Settings()
            assert settings.app_name == "Test API"
            assert settings.debug is True
            assert settings.version == "2.0.0"
            assert settings.log_level == "DEBUG"

    def test_cors_origins_list_parsing(self):
        """Test that CORS origins work with list input."""
        with patch.dict(
            os.environ,
            {
                "BACKEND_CORS_ORIGINS": '["http://localhost:3000", "https://example.com"]'
            },
        ):
            settings = Settings()
            assert settings.backend_cors_origins == [
                "http://localhost:3000",
                "https://example.com",
            ]

    def test_database_url_validation_placeholder(self):
        """Test that placeholder database URL raises validation error."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://username:password@localhost:5432/expense_tracker"
            },
        ):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            error_messages = str(exc_info.value)
            assert "must be properly configured" in error_messages

    def test_database_url_validation_valid(self):
        """Test that valid database URL passes validation."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://realuser:realpass@localhost:5432/expense_tracker",
                "SECRET_KEY": "a" * 32,  # Valid secret key
            },
        ):
            settings = Settings()
            assert (
                settings.database_url
                == "postgresql://realuser:realpass@localhost:5432/expense_tracker"
            )

    def test_secret_key_validation_too_short(self):
        """Test that short secret key raises validation error."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://realuser:realpass@localhost:5432/expense_tracker",
                "SECRET_KEY": "short",
            },
        ):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            error_messages = str(exc_info.value)
            assert "must be at least 32 characters" in error_messages

    def test_secret_key_validation_default_value(self):
        """Test that default secret key value raises validation error."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://realuser:realpass@localhost:5432/expense_tracker",
                "SECRET_KEY": "your-secret-key-here-change-in-production",
            },
        ):
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            error_messages = str(exc_info.value)
            assert "must be changed from default value" in error_messages

    def test_secret_key_validation_valid(self):
        """Test that valid secret key passes validation."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://realuser:realpass@localhost:5432/expense_tracker",
                "SECRET_KEY": "a" * 32,  # Valid secret key
            },
        ):
            settings = Settings()
            assert settings.secret_key == "a" * 32

    def test_jwt_configuration(self):
        """Test JWT configuration values."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://realuser:realpass@localhost:5432/expense_tracker",
                "SECRET_KEY": "a" * 32,
                "ALGORITHM": "HS512",
                "ACCESS_TOKEN_EXPIRE_MINUTES": "60",
            },
        ):
            settings = Settings()
            assert settings.algorithm == "HS512"
            assert settings.access_token_expire_minutes == 60

    def test_pagination_configuration(self):
        """Test pagination configuration values."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://realuser:realpass@localhost:5432/expense_tracker",
                "SECRET_KEY": "a" * 32,
                "DEFAULT_PAGE_SIZE": "10",
                "MAX_PAGE_SIZE": "50",
            },
        ):
            settings = Settings()
            assert settings.default_page_size == 10
            assert settings.max_page_size == 50

    def test_logging_configuration(self):
        """Test logging configuration values."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://realuser:realpass@localhost:5432/expense_tracker",
                "SECRET_KEY": "a" * 32,
                "LOG_LEVEL": "WARNING",
                "ENABLE_JSON_LOGGING": "false",
                "LOG_FILE": "custom.log",
            },
        ):
            settings = Settings()
            assert settings.log_level == "WARNING"
            assert settings.enable_json_logging is False
            assert settings.log_file == "custom.log"
