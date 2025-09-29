"""
Test configuration and fixtures.
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure 'src' is importable when running pytest from project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from src.api.main import app  # noqa: E402
from src.core.config import settings  # noqa: E402
from src.core.database import Base, get_db  # noqa: E402

# Create test database (PostgreSQL)
DATABASE_URL_TEST = settings.database_url_test
engine = create_engine(DATABASE_URL_TEST)

# Create all tables
Base.metadata.create_all(bind=engine)

# Create session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the database dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Create database session for testing."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User",
    }


@pytest.fixture
def test_user(client, test_user_data):
    """Create test user."""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers."""
    login_data = {
        "email": test_user["email"],
        "password": "testpass123",
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_category_data():
    """Test category data."""
    return {
        "name": "Test Category",
        "description": "Test category description",
    }


@pytest.fixture
def test_expense_data():
    """Test expense data."""
    return {
        "amount": 100.50,
        "currency": "USD",
        "description": "Test expense",
        "category_id": 1,
    }


@pytest.fixture
def cleanup_database():
    """Clean up database after tests."""
    yield
    # Clean up any test data if needed
    pass
