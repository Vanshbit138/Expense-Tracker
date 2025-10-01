"""
Test configuration and fixtures.
"""

import os
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Set test environment BEFORE importing app
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-32-chars"
os.environ[
    "BACKEND_CORS_ORIGINS"
] = '["http://localhost:3000", "http://localhost:8080"]'

from src.api.main import app
from src.core.database import Base
from src.core.security import get_password_hash
from src.models.category.category import Category
from src.models.expense.expense import Expense
from src.models.user.user import User

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create tables
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create test client with database override."""
    # Create tables for this test
    Base.metadata.create_all(bind=engine)

    # Override the database dependency
    from src.core.dependencies import get_db

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clean up
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "TestPassword123!",
    }


@pytest.fixture
def test_user(db_session):
    """Create a test user in the database."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "hashed_password": get_password_hash("TestPassword123!"),
        "is_active": True,
        "is_superuser": False,
    }

    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_category_data():
    """Sample category data for testing."""
    return {"name": "Test Category", "description": "A test category"}


@pytest.fixture
def test_category(db_session, test_user):
    """Create a test category in the database."""
    category_data = {
        "name": "Test Category",
        "description": "A test category",
        "user_id": test_user.id,
        "is_system": False,
    }

    category = Category(**category_data)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_expense_data():
    """Sample expense data for testing."""
    from datetime import date
    from decimal import Decimal

    return {
        "amount": Decimal("100.50"),
        "currency": "USD",
        "description": "Test expense",
        "category_id": 1,
        "expense_date": date(2024, 1, 15),
        "status": "pending",
        "is_recurring": False,
        "recurring_frequency": None,
    }


@pytest.fixture
def test_expense(db_session, test_user, test_category):
    """Create a test expense in the database."""
    from datetime import date
    from decimal import Decimal

    expense_data = {
        "amount": Decimal("100.50"),
        "currency": "USD",
        "description": "Test expense",
        "category_id": test_category.id,
        "expense_date": date(2024, 1, 15),
        "status": "pending",
        "is_recurring": False,
        "recurring_frequency": None,
        "user_id": test_user.id,
    }

    expense = Expense(**expense_data)
    db_session.add(expense)
    db_session.commit()
    db_session.refresh(expense)
    return expense


@pytest.fixture
def auth_headers(client, test_user_data):
    """Get authentication headers for API requests."""
    # Register user
    response = client.post("/api/v1/auth/register", json=test_user_data)
    if response.status_code == 201:
        # User registered successfully, now login to get token
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        }
        response = client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code in [200, 201]
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_db_session():
    """Mock database session for unit tests."""
    mock_session = Mock()

    # Mock query chain methods
    mock_query = Mock()
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None
    mock_query.all.return_value = []
    mock_query.offset.return_value = mock_query
    mock_query.limit.return_value = mock_query

    mock_session.query.return_value = mock_query

    # Mock other session methods
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None
    mock_session.delete.return_value = None

    return mock_session


@pytest.fixture
def mock_user_repository():
    """Mock user repository for unit tests."""
    mock_repo = Mock()
    mock_repo.create.return_value = Mock()
    mock_repo.get_by_id.return_value = None
    mock_repo.get_by_email.return_value = None
    mock_repo.get_by_username.return_value = None
    mock_repo.update.return_value = Mock()
    mock_repo.delete.return_value = True
    mock_repo.get_all.return_value = []
    return mock_repo


@pytest.fixture
def mock_category_repository():
    """Mock category repository for unit tests."""
    mock_repo = Mock()
    mock_repo.create.return_value = Mock()
    mock_repo.get_by_id.return_value = None
    mock_repo.get_by_name.return_value = None
    mock_repo.get_user_categories.return_value = []
    mock_repo.get_system_categories.return_value = []
    mock_repo.update.return_value = Mock()
    mock_repo.delete.return_value = True
    mock_repo.is_name_taken.return_value = False
    return mock_repo


@pytest.fixture
def mock_expense_repository():
    """Mock expense repository for unit tests."""
    mock_repo = Mock()
    mock_repo.create.return_value = Mock()
    mock_repo.get_by_id.return_value = None
    mock_repo.get_user_expenses.return_value = []
    mock_repo.update.return_value = Mock()
    mock_repo.delete.return_value = True
    mock_repo.get_by_category.return_value = []
    mock_repo.get_by_date_range.return_value = []
    return mock_repo


@pytest.fixture
def mock_password_service():
    """Mock password service for unit tests."""
    mock_service = Mock()
    mock_service.verify_password.return_value = True
    mock_service.get_password_hash.return_value = "hashed_password"
    return mock_service


@pytest.fixture
def mock_jwt_service():
    """Mock JWT service for unit tests."""
    mock_service = Mock()
    mock_service.create_access_token.return_value = "mock_token"
    mock_service.verify_token.return_value = {"sub": "test@example.com"}
    return mock_service


@pytest.fixture
def mock_category_service():
    """Mock category service for unit tests."""
    mock_service = Mock()
    mock_service.create_category.return_value = Mock()
    mock_service.get_category_by_id.return_value = Mock()
    mock_service.get_user_categories.return_value = []
    mock_service.update_category.return_value = Mock()
    mock_service.delete_category.return_value = True
    mock_service.create_system_categories.return_value = []
    return mock_service


@pytest.fixture
def mock_expense_service():
    """Mock expense service for unit tests."""
    mock_service = Mock()
    mock_service.create_expense.return_value = Mock()
    mock_service.get_expense_by_id.return_value = Mock()
    mock_service.get_user_expenses.return_value = []
    mock_service.update_expense.return_value = Mock()
    mock_service.delete_expense.return_value = True
    return mock_service


@pytest.fixture
def mock_user_service():
    """Mock user service for unit tests."""
    mock_service = Mock()
    mock_service.create_user.return_value = Mock()
    mock_service.get_user_by_id.return_value = Mock()
    mock_service.get_user_by_email.return_value = Mock()
    mock_service.get_user_by_username.return_value = Mock()
    mock_service.update_user.return_value = Mock()
    mock_service.delete_user.return_value = True
    mock_service.authenticate_user.return_value = Mock()
    return mock_service


@pytest.fixture
def test_user_2(db_session):
    """Create a second test user in the database."""
    user_data = {
        "email": "test2@example.com",
        "username": "testuser2",
        "full_name": "Test User 2",
        "hashed_password": get_password_hash("TestPassword123!"),
        "is_active": True,
        "is_superuser": False,
    }

    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
