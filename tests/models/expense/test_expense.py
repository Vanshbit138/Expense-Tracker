"""
Tests for the Expense model.
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


class TestExpenseModel:
    """Test cases for Expense model."""

    @pytest.fixture
    def db_session(self):
        """Create a test database session."""
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    @pytest.fixture
    def sample_user(self, db_session):
        """Create a sample user for testing."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password",
            full_name="Test User",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @pytest.fixture
    def sample_category(self, db_session, sample_user):
        """Create a sample category for testing."""
        category = Category(
            name="Test Category",
            description="Test Description",
            user_id=sample_user.id,
            color="#FF0000",
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category

    def test_expense_creation(self, db_session, sample_user, sample_category):
        """Test creating an expense."""
        expense = Expense(
            amount=Decimal("100.50"),
            currency="USD",
            description="Test Expense",
            status="completed",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
        )

        db_session.add(expense)
        db_session.commit()
        db_session.refresh(expense)

        assert expense.id is not None
        assert expense.amount == Decimal("100.50")
        assert expense.currency == "USD"
        assert expense.description == "Test Expense"
        assert expense.status == "completed"
        assert expense.user_id == sample_user.id
        assert expense.category_id == sample_category.id
        assert expense.expense_date is not None

    def test_expense_creation_with_recurring(
        self, db_session, sample_user, sample_category
    ):
        """Test creating a recurring expense."""
        expense = Expense(
            amount=Decimal("200.00"),
            currency="EUR",
            description="Monthly Rent",
            status="completed",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
            is_recurring=True,
            recurring_frequency="monthly",
        )

        db_session.add(expense)
        db_session.commit()
        db_session.refresh(expense)

        assert expense.id is not None
        assert expense.is_recurring is True
        assert expense.recurring_frequency == "monthly"

    def test_expense_creation_with_minimal_data(
        self, db_session, sample_user, sample_category
    ):
        """Test creating an expense with minimal required data."""
        expense = Expense(
            amount=Decimal("25.00"),
            currency="USD",
            description="Minimal Expense",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
        )

        db_session.add(expense)
        db_session.commit()
        db_session.refresh(expense)

        assert expense.id is not None
        assert expense.amount == Decimal("25.00")
        assert expense.currency == "USD"
        assert expense.description == "Minimal Expense"
        assert expense.user_id == sample_user.id
        assert expense.category_id == sample_category.id
        assert expense.status == "pending"  # Default value
        assert expense.is_recurring is False  # Default value

    def test_expense_timestamps(self, db_session, sample_user, sample_category):
        """Test that timestamps are automatically set."""
        expense = Expense(
            amount=Decimal("100.00"),
            currency="USD",
            description="Timestamp Test",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
        )

        db_session.add(expense)
        db_session.commit()
        db_session.refresh(expense)

        assert expense.created_at is not None
        assert expense.updated_at is not None
        # Allow for small time differences due to processing
        time_diff = abs((expense.updated_at - expense.created_at).total_seconds())
        assert time_diff < 1.0  # Less than 1 second difference

    def test_expense_update_timestamp(self, db_session, sample_user, sample_category):
        """Test that updated_at changes when expense is modified."""
        expense = Expense(
            amount=Decimal("100.00"),
            currency="USD",
            description="Update Test",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
        )

        db_session.add(expense)
        db_session.commit()
        db_session.refresh(expense)

        original_updated_at = expense.updated_at

        # Update the expense
        expense.description = "Updated Description"
        db_session.commit()
        db_session.refresh(expense)

        assert expense.updated_at > original_updated_at

    def test_expense_user_relationship(self, db_session, sample_user, sample_category):
        """Test the relationship between expense and user."""
        expense = Expense(
            amount=Decimal("100.00"),
            currency="USD",
            description="Relationship Test",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
        )

        db_session.add(expense)
        db_session.commit()
        db_session.refresh(expense)

        # Test that we can access the user through the relationship
        assert expense.user is not None
        assert expense.user.id == sample_user.id
        assert expense.user.email == sample_user.email

    def test_expense_category_relationship(
        self, db_session, sample_user, sample_category
    ):
        """Test the relationship between expense and category."""
        expense = Expense(
            amount=Decimal("100.00"),
            currency="USD",
            description="Category Relationship Test",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
        )

        db_session.add(expense)
        db_session.commit()
        db_session.refresh(expense)

        # Test that we can access the category through the relationship
        assert expense.category is not None
        assert expense.category.id == sample_category.id
        assert expense.category.name == sample_category.name

    def test_expense_string_representation(
        self, db_session, sample_user, sample_category
    ):
        """Test the string representation of an expense."""
        expense = Expense(
            amount=Decimal("100.00"),
            currency="USD",
            description="String Test",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
        )

        db_session.add(expense)
        db_session.commit()
        db_session.refresh(expense)

        # Test __repr__ method - it only shows id, amount, and currency
        repr_str = repr(expense)
        assert "Expense" in repr_str
        assert str(expense.id) in repr_str
        assert "100.00" in repr_str
        assert "USD" in repr_str

    def test_expense_equality(self, db_session, sample_user, sample_category):
        """Test expense equality."""
        expense1 = Expense(
            amount=Decimal("100.00"),
            currency="USD",
            description="Equality Test 1",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
        )
        expense2 = Expense(
            amount=Decimal("200.00"),
            currency="USD",
            description="Equality Test 2",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
        )

        db_session.add(expense1)
        db_session.add(expense2)
        db_session.commit()
        db_session.refresh(expense1)
        db_session.refresh(expense2)

        # Different expenses should not be equal
        assert expense1 != expense2

        # Same expense should be equal to itself
        assert expense1 == expense1

    def test_expense_with_different_currencies(
        self, db_session, sample_user, sample_category
    ):
        """Test creating expenses with different currencies."""
        currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"]

        for i, currency in enumerate(currencies):
            expense = Expense(
                amount=Decimal("100.00"),
                currency=currency,
                description=f"Expense in {currency}",
                user_id=sample_user.id,
                category_id=sample_category.id,
                expense_date=datetime.now(),
            )

            db_session.add(expense)
            db_session.commit()
            db_session.refresh(expense)

            assert expense.currency == currency

    def test_expense_with_different_statuses(
        self, db_session, sample_user, sample_category
    ):
        """Test creating expenses with different statuses."""
        statuses = ["pending", "completed", "cancelled", "failed"]

        for i, status in enumerate(statuses):
            expense = Expense(
                amount=Decimal("100.00"),
                currency="USD",
                description=f"Expense with status {status}",
                status=status,
                user_id=sample_user.id,
                category_id=sample_category.id,
                expense_date=datetime.now(),
            )

            db_session.add(expense)
            db_session.commit()
            db_session.refresh(expense)

            assert expense.status == status

    def test_expense_with_different_dates(
        self, db_session, sample_user, sample_category
    ):
        """Test creating expenses with different dates."""
        from datetime import timedelta

        dates = [
            datetime.now(),
            datetime.now() - timedelta(days=1),
            datetime.now() + timedelta(days=1),
            datetime(2024, 1, 1),
            datetime(2024, 12, 31),
        ]

        for i, expense_date in enumerate(dates):
            expense = Expense(
                amount=Decimal("100.00"),
                currency="USD",
                description=f"Expense for {expense_date}",
                user_id=sample_user.id,
                category_id=sample_category.id,
                expense_date=expense_date,
            )

            db_session.add(expense)
            db_session.commit()
            db_session.refresh(expense)

            assert expense.expense_date == expense_date

    def test_expense_with_different_amounts(
        self, db_session, sample_user, sample_category
    ):
        """Test creating expenses with different amounts."""
        amounts = [
            Decimal("0.01"),
            Decimal("1.00"),
            Decimal("100.00"),
            Decimal("1000.00"),
            Decimal("999999.99"),
        ]

        for i, amount in enumerate(amounts):
            expense = Expense(
                amount=amount,
                currency="USD",
                description=f"Expense with amount {amount}",
                user_id=sample_user.id,
                category_id=sample_category.id,
                expense_date=datetime.now(),
            )

            db_session.add(expense)
            db_session.commit()
            db_session.refresh(expense)

            assert expense.amount == amount

    def test_expense_recurring_frequencies(
        self, db_session, sample_user, sample_category
    ):
        """Test creating expenses with different recurring frequencies."""
        frequencies = ["daily", "weekly", "monthly", "yearly"]

        for i, frequency in enumerate(frequencies):
            expense = Expense(
                amount=Decimal("100.00"),
                currency="USD",
                description=f"Recurring expense - {frequency}",
                user_id=sample_user.id,
                category_id=sample_category.id,
                expense_date=datetime.now(),
                is_recurring=True,
                recurring_frequency=frequency,
            )

            db_session.add(expense)
            db_session.commit()
            db_session.refresh(expense)

            assert expense.recurring_frequency == frequency
            assert expense.is_recurring is True

    def test_expense_with_long_description(
        self, db_session, sample_user, sample_category
    ):
        """Test creating an expense with a long description."""
        long_description = "This is a very long description for testing purposes. " * 10

        expense = Expense(
            amount=Decimal("100.00"),
            currency="USD",
            description=long_description,
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
        )

        db_session.add(expense)
        db_session.commit()
        db_session.refresh(expense)

        assert expense.description == long_description
        assert len(expense.description) > 100

    def test_expense_default_values(self, db_session, sample_user, sample_category):
        """Test that default values are set correctly."""
        expense = Expense(
            amount=Decimal("100.00"),
            user_id=sample_user.id,
            category_id=sample_category.id,
        )

        db_session.add(expense)
        db_session.commit()
        db_session.refresh(expense)

        assert expense.currency == "USD"  # Default currency
        assert expense.status == "pending"  # Default status
        assert expense.is_recurring is False  # Default value
        assert expense.expense_date is not None  # Default to current time
        assert expense.created_at is not None  # Default to current time
        assert expense.updated_at is not None  # Default to current time
