"""
Application configuration using Pydantic settings.
"""

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

    # Database Configuration
    database_url: str = "postgresql://postgres:root@localhost:5432/expense_tracker"
    database_url_test: str = (
        "postgresql://postgres:root@localhost:5432/expense_tracker_test"
    )

    # JWT Configuration
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # CORS Configuration
    backend_cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


# Global settings instance
settings = Settings()
