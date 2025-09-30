"""
Unit tests for configuration module.
"""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.core.config import Settings


class TestSettings:
    """Test cases for Settings class."""

    def test_default_values(self):
        """Test default configuration values."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://user:pass@localhost:5432/test",
                "SECRET_KEY": "test-secret-key-32-characters-long",
            },
        ):
            settings = Settings()

            assert settings.app_name == "Expense Tracker API"
            assert settings.debug is False
            assert settings.version == "1.0.0"
            assert settings.api_v1_str == "/api/v1"
            assert settings.algorithm == "HS256"
            assert settings.access_token_expire_minutes == 1440
            assert settings.default_page_size == 20
            assert settings.max_page_size == 100
            assert settings.log_level == "INFO"
            assert settings.enable_json_logging is True

    def test_database_url_validation_empty(self):
        """Test database URL validation with empty value."""
        with patch.dict(
            os.environ, {"SECRET_KEY": "test-secret-key-32-characters-long"}, clear=True
        ):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            assert "database_url must be set in .env file" in str(exc_info.value)

    def test_database_url_validation_placeholder(self):
        """Test database URL validation with placeholder value."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://username:password@localhost:5432/test",
                "SECRET_KEY": "test-secret-key-32-characters-long",
            },
        ):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            assert "DATABASE_URL must be properly configured" in str(exc_info.value)

    def test_secret_key_validation_empty(self):
        """Test secret key validation with empty value."""
        with patch.dict(
            os.environ,
            {"DATABASE_URL": "postgresql://user:pass@localhost:5432/test"},
            clear=True,
        ):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            assert "secret_key must be set in .env file" in str(exc_info.value)

    def test_secret_key_validation_placeholder(self):
        """Test secret key validation with placeholder value."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://user:pass@localhost:5432/test",
                "SECRET_KEY": "your-secret-key-here-change-in-production",
            },
        ):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            assert "SECRET_KEY must be changed from default value" in str(
                exc_info.value
            )

    def test_secret_key_validation_too_short(self):
        """Test secret key validation with too short key."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://user:pass@localhost:5432/test",
                "SECRET_KEY": "short",
            },
        ):
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            assert "SECRET_KEY must be at least 32 characters long" in str(
                exc_info.value
            )

    def test_cors_origins_string_parsing(self):
        """Test CORS origins parsing from string."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://user:pass@localhost:5432/test",
                "SECRET_KEY": "test-secret-key-32-characters-long",
                "BACKEND_CORS_ORIGINS": "http://localhost:3000,http://localhost:8080",
            },
        ):
            settings = Settings()
            assert settings.backend_cors_origins == [
                "http://localhost:3000",
                "http://localhost:8080",
            ]

    def test_cors_origins_list_parsing(self):
        """Test CORS origins parsing from list."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://user:pass@localhost:5432/test",
                "SECRET_KEY": "test-secret-key-32-characters-long",
                "BACKEND_CORS_ORIGINS": '["http://localhost:3000", "http://localhost:8080"]',
            },
        ):
            settings = Settings()
            assert settings.backend_cors_origins == [
                "http://localhost:3000",
                "http://localhost:8080",
            ]

    def test_cors_origins_invalid_format(self):
        """Test CORS origins validation with invalid format."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://user:pass@localhost:5432/test",
                "SECRET_KEY": "test-secret-key-32-characters-long",
                "BACKEND_CORS_ORIGINS": "invalid_format",
            },
        ):
            with pytest.raises(ValidationError):
                Settings()

    def test_valid_configuration(self):
        """Test valid configuration setup."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://user:pass@localhost:5432/test",
                "SECRET_KEY": "test-secret-key-32-characters-long",
                "DEBUG": "true",
                "LOG_LEVEL": "DEBUG",
                "ENABLE_JSON_LOGGING": "false",
            },
        ):
            settings = Settings()

            assert settings.database_url == "postgresql://user:pass@localhost:5432/test"
            assert settings.secret_key == "test-secret-key-32-characters-long"
            assert settings.debug is True
            assert settings.log_level == "DEBUG"
            assert settings.enable_json_logging is False

    def test_model_config(self):
        """Test Pydantic model configuration."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://user:pass@localhost:5432/test",
                "SECRET_KEY": "test-secret-key-32-characters-long",
            },
        ):
            settings = Settings()

            # Test case sensitivity
            assert settings.model_config["case_sensitive"] is False
            assert settings.model_config["extra"] == "ignore"

    def test_extra_environment_variables_ignored(self):
        """Test that extra environment variables are ignored."""
        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "postgresql://user:pass@localhost:5432/test",
                "SECRET_KEY": "test-secret-key-32-characters-long",
                "UNKNOWN_VAR": "should_be_ignored",
            },
        ):
            settings = Settings()
            # Should not raise an error due to extra="ignore"
            assert settings.app_name == "Expense Tracker API"
