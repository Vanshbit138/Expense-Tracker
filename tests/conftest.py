"""
Test configuration and fixtures.
"""

import os
import sys

# Ensure 'src' is importable when running pytest from project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.main import app
from src.core.database import Base, get_db
from src.core.config import settings

# Create test database (PostgreSQL)
DATABASE_URL_TEST = settings.database_url_test
engine = create_engine(DATABASE_URL_TEST)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Provide a transactional database session for each test (PostgreSQL)."""
    # Ensure tables exist once
    Base.metadata.create_all(bind=engine)

    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database dependency override."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User",
    }


@pytest.fixture
def test_user(client, test_user_data):
    """Create a test user."""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def auth_headers(client, test_user_data, test_user):
    """Get authentication headers for test user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user_data["email"], "password": test_user_data["password"]},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_category_data():
    """Test category data."""
    return {
        "name": "Test Category",
        "description": "A test category",
        "color": "#FF0000",
    }


@pytest.fixture
def test_expense_data():
    """Test expense data."""
    return {
        "amount": 100.50,
        "currency": "USD",
        "description": "Test expense",
        "status": "pending",
        "is_recurring": False,
        "expense_date": "2024-01-01T00:00:00",
        "category_id": 1,
    }
