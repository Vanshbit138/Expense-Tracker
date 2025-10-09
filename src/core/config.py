"""
Application configuration using Pydantic settings.
"""

import os
from typing import List, Union

from pydantic import ConfigDict, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",  # Allow extra environment variables
    )

    # FastAPI Configuration
    app_name: str = "Expense Tracker API"
    debug: bool = False
    version: str = "1.0.0"
    api_v1_str: str = "/api/v1"

    # Database Configuration - These MUST be set in .env file
    database_url: str = ""  # Will be validated to ensure it's set
    database_url_test: str = ""  # Will be validated to ensure it's set

    # JWT Configuration - These MUST be set in .env file
    secret_key: str = ""  # Will be validated to ensure it's set
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # CORS Configuration
    backend_cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    # Logging Configuration
    log_level: str = "INFO"
    enable_json_logging: bool = True
    log_file: str = "logs/expense-tracker.log"

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    @field_validator("database_url", "database_url_test")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL is properly configured."""
        # Skip validation for test environments
        if os.getenv("TESTING") == "true":
            return v or "sqlite:///:memory:"

        if not v:
            raise ValueError(
                f"{cls.__name__}.database_url must be set in .env file. "
                "Example: postgresql://username:password@localhost:5432/expense_tracker"
            )
        if "username:password" in v or "your_username:your_password" in v:
            raise ValueError(
                "DATABASE_URL must be properly configured in .env file with real credentials"
            )
        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key is properly configured."""
        # Skip validation for test environments
        if os.getenv("TESTING") == "true":
            return v or "test-secret-key-for-testing-only-32-chars"

        if not v:
            # Log critical security failure
            import logging

            logger = logging.getLogger(__name__)
            logger.critical(
                "Security configuration failure - SECRET_KEY not set",
                message="Application cannot start without proper security configuration",
            )
            raise ValueError(
                f"{cls.__name__}.secret_key must be set in .env file. "
                "Generate a secure key for production use."
            )
        if v == "your-secret-key-here-change-in-production":
            raise ValueError(
                "SECRET_KEY must be changed from default value in .env file"
            )
        if len(v) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters long for security"
            )
        return v


# Global settings instance - lazy loading
_settings = None


def get_settings() -> Settings:
    """Get settings instance with lazy loading."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


# For backward compatibility - this will be set when first accessed
settings = None


def __getattr__(name):
    """Lazy loading for settings."""
    if name == "settings":
        global settings
        if settings is None:
            settings = get_settings()
        return settings
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
