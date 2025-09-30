"""
Unit tests for model classes.
"""

from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.database import Base
from src.models.category.category import Category
from src.models.expense.expense import Expense
from src.models.user.user import User


class TestUserModel:
    """Test cases for User model."""

    def test_user_creation(self):
        """Test basic user creation."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            full_name="Test User",
            is_active=True,
            is_superuser=False,
        )

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.hashed_password == "hashed_password"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.id is None  # Not yet persisted

    def test_user_creation_with_minimal_data(self):
        """Test user creation with minimal required data."""
        user = User(
            email="minimal@example.com",
            username="minimal",
            hashed_password="hashed_password",
        )

        assert user.email == "minimal@example.com"
        assert user.username == "minimal"
        assert user.hashed_password == "hashed_password"
        assert user.full_name is None
        assert user.is_active is True  # Default value
        assert user.is_superuser is False  # Default value

    def test_user_repr(self):
        """Test user string representation."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
        )
        user.id = 123  # Simulate persisted user

        repr_str = repr(user)
        assert "User(id=123, email='test@example.com', username='testuser')" in repr_str

    def test_user_relationships(self):
        """Test user relationships are properly defined."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
        )

        # Check that relationships are defined
        assert hasattr(user, "expenses")
        assert hasattr(user, "categories")

    def test_user_timestamps(self):
        """Test user timestamp fields."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
        )

        # Timestamps should be None initially
        assert user.created_at is None
        assert user.updated_at is None

    def test_user_attributes(self):
        """Test all user attributes are accessible."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            full_name="Test User",
            is_active=True,
            is_superuser=False,
        )

        # Test all attributes are accessible
        assert hasattr(user, "id")
        assert hasattr(user, "email")
        assert hasattr(user, "username")
        assert hasattr(user, "hashed_password")
        assert hasattr(user, "full_name")
        assert hasattr(user, "is_active")
        assert hasattr(user, "is_superuser")
        assert hasattr(user, "created_at")
        assert hasattr(user, "updated_at")


class TestCategoryModel:
    """Test cases for Category model."""

    def test_category_creation(self):
        """Test basic category creation."""
        category = Category(
            name="Test Category",
            description="A test category",
            user_id=1,
            is_system=False,
        )

        assert category.name == "Test Category"
        assert category.description == "A test category"
        assert category.user_id == 1
        assert category.is_system is False
        assert category.id is None  # Not yet persisted

    def test_category_creation_with_minimal_data(self):
        """Test category creation with minimal required data."""
        category = Category(name="Minimal Category", user_id=1)

        assert category.name == "Minimal Category"
        assert category.description is None
        assert category.user_id == 1
        assert category.is_system is False  # Default value

    def test_category_repr(self):
        """Test category string representation."""
        category = Category(name="Test Category", user_id=1)
        category.id = 456  # Simulate persisted category

        repr_str = repr(category)
        assert "Category(id=456, name='Test Category', user_id=1)" in repr_str

    def test_category_relationships(self):
        """Test category relationships are properly defined."""
        category = Category(name="Test Category", user_id=1)

        # Check that relationships are defined
        assert hasattr(category, "user")
        assert hasattr(category, "expenses")

    def test_category_timestamps(self):
        """Test category timestamp fields."""
        category = Category(name="Test Category", user_id=1)

        # Timestamps should be None initially
        assert category.created_at is None
        assert category.updated_at is None

    def test_category_attributes(self):
        """Test all category attributes are accessible."""
        category = Category(
            name="Test Category",
            description="A test category",
            user_id=1,
            is_system=True,
        )

        # Test all attributes are accessible
        assert hasattr(category, "id")
        assert hasattr(category, "name")
        assert hasattr(category, "description")
        assert hasattr(category, "user_id")
        assert hasattr(category, "is_system")
        assert hasattr(category, "created_at")
        assert hasattr(category, "updated_at")


class TestExpenseModel:
    """Test cases for Expense model."""

    def test_expense_creation(self):
        """Test basic expense creation."""
        expense = Expense(
            amount=Decimal("100.50"),
            currency="USD",
            description="Test expense",
            status="pending",
            is_recurring=False,
            recurring_frequency=None,
            expense_date=datetime(2023, 1, 1, 12, 0, 0),
            user_id=1,
            category_id=1,
        )

        assert expense.amount == Decimal("100.50")
        assert expense.currency == "USD"
        assert expense.description == "Test expense"
        assert expense.status == "pending"
        assert expense.is_recurring is False
        assert expense.recurring_frequency is None
        assert expense.expense_date == datetime(2023, 1, 1, 12, 0, 0)
        assert expense.user_id == 1
        assert expense.category_id == 1
        assert expense.id is None  # Not yet persisted

    def test_expense_creation_with_minimal_data(self):
        """Test expense creation with minimal required data."""
        expense = Expense(amount=Decimal("50.00"), user_id=1, category_id=1)

        assert expense.amount == Decimal("50.00")
        assert expense.currency == "USD"  # Default value
        assert expense.description is None
        assert expense.status == "pending"  # Default value
        assert expense.is_recurring is False  # Default value
        assert expense.recurring_frequency is None
        assert expense.user_id == 1
        assert expense.category_id == 1

    def test_expense_repr(self):
        """Test expense string representation."""
        expense = Expense(
            amount=Decimal("75.25"), currency="EUR", user_id=1, category_id=1
        )
        expense.id = 789  # Simulate persisted expense

        repr_str = repr(expense)
        assert "Expense(id=789, amount=75.25, currency='EUR')" in repr_str

    def test_expense_relationships(self):
        """Test expense relationships are properly defined."""
        expense = Expense(amount=Decimal("100.00"), user_id=1, category_id=1)

        # Check that relationships are defined
        assert hasattr(expense, "user")
        assert hasattr(expense, "category")

    def test_expense_timestamps(self):
        """Test expense timestamp fields."""
        expense = Expense(amount=Decimal("100.00"), user_id=1, category_id=1)

        # Timestamps should be None initially
        assert expense.created_at is None
        assert expense.updated_at is None

    def test_expense_attributes(self):
        """Test all expense attributes are accessible."""
        expense = Expense(
            amount=Decimal("100.00"),
            currency="USD",
            description="Test expense",
            status="approved",
            is_recurring=True,
            recurring_frequency="monthly",
            expense_date=datetime(2023, 1, 1),
            user_id=1,
            category_id=1,
        )

        # Test all attributes are accessible
        assert hasattr(expense, "id")
        assert hasattr(expense, "amount")
        assert hasattr(expense, "currency")
        assert hasattr(expense, "description")
        assert hasattr(expense, "status")
        assert hasattr(expense, "is_recurring")
        assert hasattr(expense, "recurring_frequency")
        assert hasattr(expense, "expense_date")
        assert hasattr(expense, "user_id")
        assert hasattr(expense, "category_id")
        assert hasattr(expense, "created_at")
        assert hasattr(expense, "updated_at")

    def test_expense_with_different_currencies(self):
        """Test expense with different currencies."""
        currencies = ["USD", "EUR", "GBP", "JPY", "CAD"]

        for currency in currencies:
            expense = Expense(
                amount=Decimal("100.00"), currency=currency, user_id=1, category_id=1
            )
            assert expense.currency == currency

    def test_expense_with_different_statuses(self):
        """Test expense with different statuses."""
        statuses = ["pending", "approved", "rejected"]

        for status in statuses:
            expense = Expense(
                amount=Decimal("100.00"), status=status, user_id=1, category_id=1
            )
            assert expense.status == status

    def test_expense_with_recurring_frequencies(self):
        """Test expense with different recurring frequencies."""
        frequencies = ["daily", "weekly", "monthly", "yearly"]

        for frequency in frequencies:
            expense = Expense(
                amount=Decimal("100.00"),
                is_recurring=True,
                recurring_frequency=frequency,
                user_id=1,
                category_id=1,
            )
            assert expense.is_recurring is True
            assert expense.recurring_frequency == frequency

    def test_expense_with_decimal_amounts(self):
        """Test expense with various decimal amounts."""
        amounts = [
            Decimal("0.01"),
            Decimal("1.00"),
            Decimal("100.50"),
            Decimal("999.99"),
            Decimal("1000.00"),
        ]

        for amount in amounts:
            expense = Expense(amount=amount, user_id=1, category_id=1)
            assert expense.amount == amount


class TestModelDatabaseIntegration:
    """Integration tests for models with database."""

    @pytest.fixture
    def db_session(self):
        """Create a test database session."""
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_user_persistence(self, db_session):
        """Test user persistence in database."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            full_name="Test User",
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_category_persistence(self, db_session):
        """Test category persistence in database."""
        # First create a user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Then create a category
        category = Category(
            name="Test Category", description="A test category", user_id=user.id
        )

        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        assert category.id is not None
        assert category.created_at is not None
        assert category.updated_at is not None

    def test_expense_persistence(self, db_session):
        """Test expense persistence in database."""
        # First create a user and category
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        category = Category(name="Test Category", user_id=user.id)
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        # Then create an expense
        expense = Expense(
            amount=Decimal("100.50"),
            currency="USD",
            description="Test expense",
            user_id=user.id,
            category_id=category.id,
        )

        db_session.add(expense)
        db_session.commit()
        db_session.refresh(expense)

        assert expense.id is not None
        assert expense.created_at is not None
        assert expense.updated_at is not None

    def test_model_relationships_persistence(self, db_session):
        """Test that model relationships work with database."""
        # Create user
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Create category
        category = Category(name="Test Category", user_id=user.id)
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        # Create expense
        expense = Expense(
            amount=Decimal("100.00"), user_id=user.id, category_id=category.id
        )
        db_session.add(expense)
        db_session.commit()
        db_session.refresh(expense)

        # Test relationships
        assert expense.user_id == user.id
        assert expense.category_id == category.id

        # Test that we can access related objects
        # Note: In a real scenario, we would use relationship loading
        # but for this test, we're just verifying the foreign keys
        assert expense.user_id is not None
        assert expense.category_id is not None
