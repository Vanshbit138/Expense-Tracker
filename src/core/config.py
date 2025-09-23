"""
Application configuration settings.
"""

from typing import List

from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database Configuration
    database_url: str = "postgresql://username:password@localhost:5432/expense_tracker"
    database_url_test: str = (
        "postgresql://username:password@localhost:5432/expense_tracker_test"
    )

    # JWT Configuration
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours

    # Application Configuration
    debug: bool = True
    project_name: str = "Expense Tracker API"
    version: str = "1.0.0"
    api_v1_str: str = "/api/v1"

    # CORS Configuration
    backend_cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    @validator("backend_cors_origins", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
