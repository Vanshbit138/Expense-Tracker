"""
Pytest configuration and shared fixtures for Expense Tracker API tests.
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from src.api.main import app
from src.core.database import Base, get_db
from src.models.category.category import Category
from src.models.expense.expense import Expense
from src.models.user.user import User
from src.schemas.category.category import CategoryCreate
from src.schemas.expense.expense import ExpenseCreate
from src.schemas.user.user import UserCreate

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def test_db():
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db) -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database dependency override."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_settings():
    """Mock application settings for testing."""
    with patch("src.core.config.settings") as mock:
        mock.app_name = "Expense Tracker API Test"
        mock.debug = True
        mock.version = "1.0.0"
        mock.api_v1_str = "/api/v1"
        mock.database_url = "sqlite:///./test.db"
        mock.database_url_test = "sqlite:///./test.db"
        mock.secret_key = "test-secret-key-32-characters-long"
        mock.algorithm = "HS256"
        mock.access_token_expire_minutes = 1440
        mock.backend_cors_origins = ["http://localhost:3000"]
        mock.default_page_size = 20
        mock.max_page_size = 100
        mock.log_level = "INFO"
        mock.enable_json_logging = False
        mock.log_file = "logs/test.log"
        yield mock


@pytest.fixture
def sample_user_data() -> Dict[str, Any]:
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "password": "testpassword123",
        "is_active": True,
        "is_superuser": False,
    }


@pytest.fixture
def sample_user(db_session: Session, sample_user_data: Dict[str, Any]) -> User:
    """Create a sample user in the database."""
    from src.services.authentication.password_service import get_password_hash

    user = User(
        email=sample_user_data["email"],
        username=sample_user_data["username"],
        full_name=sample_user_data["full_name"],
        hashed_password=get_password_hash(sample_user_data["password"]),
        is_active=sample_user_data["is_active"],
        is_superuser=sample_user_data["is_superuser"],
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_category_data() -> Dict[str, Any]:
    """Sample category data for testing."""
    return {"name": "Test Category", "description": "A test category for expenses"}


@pytest.fixture
def sample_category(
    db_session: Session, sample_user: User, sample_category_data: Dict[str, Any]
) -> Category:
    """Create a sample category in the database."""
    category = Category(
        name=sample_category_data["name"],
        description=sample_category_data["description"],
        user_id=sample_user.id,
    )

    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def sample_expense_data() -> Dict[str, Any]:
    """Sample expense data for testing."""
    return {
        "amount": Decimal("100.50"),
        "currency": "USD",
        "description": "Test expense",
        "status": "pending",
        "is_recurring": False,
        "recurring_frequency": None,
        "expense_date": datetime.utcnow(),
    }


@pytest.fixture
def sample_expense(
    db_session: Session,
    sample_user: User,
    sample_category: Category,
    sample_expense_data: Dict[str, Any],
) -> Expense:
    """Create a sample expense in the database."""
    expense = Expense(
        amount=sample_expense_data["amount"],
        currency=sample_expense_data["currency"],
        description=sample_expense_data["description"],
        status=sample_expense_data["status"],
        is_recurring=sample_expense_data["is_recurring"],
        recurring_frequency=sample_expense_data["recurring_frequency"],
        expense_date=sample_expense_data["expense_date"],
        user_id=sample_user.id,
        category_id=sample_category.id,
    )

    db_session.add(expense)
    db_session.commit()
    db_session.refresh(expense)
    return expense


@pytest.fixture
def auth_headers(sample_user: User) -> Dict[str, str]:
    """Generate authentication headers for testing."""
    from src.services.authentication.jwt_service import create_access_token

    token = create_access_token(subject=str(sample_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_repository():
    """Mock repository for testing services."""
    return MagicMock()


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    return MagicMock()


@pytest.fixture
def mock_password_context():
    """Mock password context for testing."""
    with patch("src.services.authentication.password_service.pwd_context") as mock:
        mock.verify.return_value = True
        mock.hash.return_value = "hashed_password"
        yield mock


@pytest.fixture
def mock_jwt():
    """Mock JWT operations for testing."""
    with patch("src.services.authentication.jwt_service.jwt") as mock:
        mock.encode.return_value = "test_token"
        mock.decode.return_value = {
            "sub": "1",
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        yield mock


@pytest.fixture
def mock_database_operations():
    """Mock database operations for testing."""
    with patch("src.core.database.get_db") as mock:
        mock.return_value = MagicMock()
        yield mock


@pytest.fixture
def sample_user_create() -> UserCreate:
    """Sample UserCreate schema for testing."""
    return UserCreate(
        email="newuser@example.com",
        username="newuser",
        full_name="New User",
        password="newpassword123",
    )


@pytest.fixture
def sample_category_create() -> CategoryCreate:
    """Sample CategoryCreate schema for testing."""
    return CategoryCreate(name="New Category", description="A new test category")


@pytest.fixture
def sample_expense_create() -> ExpenseCreate:
    """Sample ExpenseCreate schema for testing."""
    return ExpenseCreate(
        amount=Decimal("50.00"),
        currency="USD",
        description="New test expense",
        status="pending",
        is_recurring=False,
        recurring_frequency=None,
        expense_date=datetime.utcnow(),
        category_id=1,
    )


@pytest.fixture
def multiple_users(db_session: Session) -> list[User]:
    """Create multiple users for testing."""
    from src.services.authentication.password_service import get_password_hash

    users = []
    for i in range(3):
        user = User(
            email=f"user{i}@example.com",
            username=f"user{i}",
            full_name=f"User {i}",
            hashed_password=get_password_hash("password123"),
            is_active=True,
            is_superuser=False,
        )
        db_session.add(user)
        users.append(user)

    db_session.commit()
    for user in users:
        db_session.refresh(user)

    return users


@pytest.fixture
def multiple_categories(db_session: Session, sample_user: User) -> list[Category]:
    """Create multiple categories for testing."""
    categories = []
    category_names = ["Food", "Transport", "Entertainment", "Utilities", "Healthcare"]

    for name in category_names:
        category = Category(
            name=name,
            description=f"Category for {name.lower()}",
            user_id=sample_user.id,
        )
        db_session.add(category)
        categories.append(category)

    db_session.commit()
    for category in categories:
        db_session.refresh(category)

    return categories


@pytest.fixture
def multiple_expenses(
    db_session: Session, sample_user: User, multiple_categories: list[Category]
) -> list[Expense]:
    """Create multiple expenses for testing."""
    expenses = []
    amounts = [
        Decimal("25.50"),
        Decimal("100.00"),
        Decimal("75.25"),
        Decimal("200.00"),
        Decimal("50.75"),
    ]

    for i, (amount, category) in enumerate(zip(amounts, multiple_categories)):
        expense = Expense(
            amount=amount,
            currency="USD",
            description=f"Test expense {i+1}",
            status="pending",
            is_recurring=False,
            expense_date=datetime.utcnow() - timedelta(days=i),
            user_id=sample_user.id,
            category_id=category.id,
        )
        db_session.add(expense)
        expenses.append(expense)

    db_session.commit()
    for expense in expenses:
        db_session.refresh(expense)

    return expenses


# Async fixtures for async testing
@pytest.fixture
def mock_async_repository():
    """Mock async repository for testing."""
    return AsyncMock()


@pytest.fixture
def mock_async_service():
    """Mock async service for testing."""
    return AsyncMock()


# Test data factories
class TestDataFactory:
    """Factory for creating test data."""

    @staticmethod
    def create_user_data(**overrides) -> Dict[str, Any]:
        """Create user data with optional overrides."""
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "password": "testpassword123",
            "is_active": True,
            "is_superuser": False,
        }
        data.update(overrides)
        return data

    @staticmethod
    def create_category_data(**overrides) -> Dict[str, Any]:
        """Create category data with optional overrides."""
        data = {"name": "Test Category", "description": "A test category"}
        data.update(overrides)
        return data

    @staticmethod
    def create_expense_data(**overrides) -> Dict[str, Any]:
        """Create expense data with optional overrides."""
        data = {
            "amount": Decimal("100.00"),
            "currency": "USD",
            "description": "Test expense",
            "status": "pending",
            "is_recurring": False,
            "recurring_frequency": None,
            "expense_date": datetime.utcnow(),
        }
        data.update(overrides)
        return data


@pytest.fixture
def test_data_factory():
    """Provide test data factory."""
    return TestDataFactory()


# Environment variable mocking
@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        "DATABASE_URL": "sqlite:///./test.db",
        "SECRET_KEY": "test-secret-key-32-characters-long",
        "LOG_LEVEL": "INFO",
        "ENABLE_JSON_LOGGING": "false",
    }

    with patch.dict(os.environ, env_vars):
        yield env_vars


# Database transaction rollback fixture
@pytest.fixture(autouse=True)
def rollback_transaction(db_session: Session):
    """Automatically rollback database transactions after each test."""
    yield
    db_session.rollback()


# Logging capture fixture
@pytest.fixture
def caplog():
    """Capture log messages during testing."""
    import logging

    caplog_handler = logging.StreamHandler()
    caplog_handler.setLevel(logging.DEBUG)

    # Add handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(caplog_handler)

    yield caplog_handler

    # Remove handler after test
    root_logger.removeHandler(caplog_handler)
