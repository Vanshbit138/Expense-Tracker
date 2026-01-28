"""
Tests for the ExpenseRepository class.
"""

from datetime import date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.database import Base
from src.models.category.category import Category
from src.models.expense.expense import Expense
from src.models.user.user import User
from src.repositories.expense.expense_repository import ExpenseRepository


class TestExpenseRepository:
    """Test cases for ExpenseRepository."""

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
    def expense_repo(self, db_session):
        """Create an ExpenseRepository instance."""
        return ExpenseRepository(db_session)

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

    @pytest.fixture
    def sample_expense(self, db_session, sample_user, sample_category):
        """Create a sample expense for testing."""
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
        return expense

    def test_create_expense(self, expense_repo, sample_user, sample_category):
        """Test creating a new expense."""
        expense = Expense(
            amount=Decimal("50.25"),
            currency="EUR",
            description="New Expense",
            status="pending",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
        )

        created_expense = expense_repo.create(expense)

        assert created_expense.id is not None
        assert created_expense.amount == Decimal("50.25")
        assert created_expense.currency == "EUR"
        assert created_expense.description == "New Expense"
        assert created_expense.status == "pending"
        assert created_expense.user_id == sample_user.id
        assert created_expense.category_id == sample_category.id

    def test_get_by_id_existing_expense(self, expense_repo, sample_expense):
        """Test getting an existing expense by ID."""
        found_expense = expense_repo.get_by_id(
            sample_expense.id, sample_expense.user_id
        )

        assert found_expense is not None
        assert found_expense.id == sample_expense.id
        assert found_expense.amount == sample_expense.amount

    def test_get_by_id_nonexistent_expense(self, expense_repo, sample_user):
        """Test getting a non-existent expense by ID."""
        found_expense = expense_repo.get_by_id(99999, sample_user.id)

        assert found_expense is None

    def test_get_by_id_wrong_user(self, expense_repo, sample_expense, db_session):
        """Test getting an expense with wrong user ID."""
        # Create another user
        other_user = User(
            email="other@example.com",
            username="otheruser",
            hashed_password="hashed_password",
            full_name="Other User",
        )
        db_session.add(other_user)
        db_session.commit()
        db_session.refresh(other_user)

        # Try to get expense with wrong user ID
        found_expense = expense_repo.get_by_id(sample_expense.id, other_user.id)

        assert found_expense is None

    def test_get_user_expenses(self, expense_repo, sample_user, sample_category):
        """Test getting user expenses."""
        # Create multiple expenses for the user
        expense1 = Expense(
            amount=Decimal("25.00"),
            currency="USD",
            description="Expense 1",
            status="completed",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
        )
        expense2 = Expense(
            amount=Decimal("75.00"),
            currency="USD",
            description="Expense 2",
            status="pending",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
        )
        expense_repo.create(expense1)
        expense_repo.create(expense2)

        user_expenses = expense_repo.get_user_expenses(sample_user.id)

        assert len(user_expenses) == 2  # Only the expenses we just created
        assert any(exp.description == "Expense 1" for exp in user_expenses)
        assert any(exp.description == "Expense 2" for exp in user_expenses)

    def test_get_user_expenses_with_pagination(
        self, expense_repo, sample_user, sample_category
    ):
        """Test getting user expenses with pagination."""
        # Create multiple expenses for the user
        for i in range(5):
            expense = Expense(
                amount=Decimal(f"{i * 10}.00"),
                currency="USD",
                description=f"Expense {i}",
                status="completed",
                user_id=sample_user.id,
                category_id=sample_category.id,
                expense_date=datetime.now(),
            )
            expense_repo.create(expense)

        # Test first page
        first_page = expense_repo.get_user_expenses(sample_user.id, skip=0, limit=2)
        assert len(first_page) == 2

        # Test second page
        second_page = expense_repo.get_user_expenses(sample_user.id, skip=2, limit=2)
        assert len(second_page) == 2

        # Test third page
        third_page = expense_repo.get_user_expenses(sample_user.id, skip=4, limit=2)
        assert len(third_page) == 1  # Only 1 remaining expense

    def test_get_user_expenses_with_category_filter(
        self, expense_repo, sample_user, sample_category, db_session
    ):
        """Test getting user expenses with category filter."""
        # Create another category
        other_category = Category(
            name="Other Category",
            description="Other Description",
            user_id=sample_user.id,
            color="#00FF00",
        )
        db_session.add(other_category)
        db_session.commit()
        db_session.refresh(other_category)

        # Create expenses with different categories
        expense1 = Expense(
            amount=Decimal("25.00"),
            currency="USD",
            description="Expense 1",
            status="completed",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
        )
        expense2 = Expense(
            amount=Decimal("75.00"),
            currency="USD",
            description="Expense 2",
            status="completed",
            user_id=sample_user.id,
            category_id=other_category.id,
            expense_date=datetime.now(),
        )
        expense_repo.create(expense1)
        expense_repo.create(expense2)

        # Filter by first category
        filtered_expenses = expense_repo.get_user_expenses(
            sample_user.id, category_id=sample_category.id
        )

        assert len(filtered_expenses) == 1  # Only the expense with the first category
        assert all(exp.category_id == sample_category.id for exp in filtered_expenses)

    def test_get_user_expenses_with_status_filter(
        self, expense_repo, sample_user, sample_category
    ):
        """Test getting user expenses with status filter."""
        # Create expenses with different statuses
        expense1 = Expense(
            amount=Decimal("25.00"),
            currency="USD",
            description="Completed Expense",
            status="completed",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
        )
        expense2 = Expense(
            amount=Decimal("75.00"),
            currency="USD",
            description="Pending Expense",
            status="pending",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
        )
        expense_repo.create(expense1)
        expense_repo.create(expense2)

        # Filter by completed status
        completed_expenses = expense_repo.get_user_expenses(
            sample_user.id, status="completed"
        )

        assert len(completed_expenses) == 1  # Only the completed expense
        assert all(exp.status == "completed" for exp in completed_expenses)

    def test_get_user_expenses_with_date_filter(
        self, expense_repo, sample_user, sample_category
    ):
        """Test getting user expenses with date filter."""
        from datetime import timedelta

        # Create expenses with different dates
        yesterday = datetime.now() - timedelta(days=1)
        tomorrow = datetime.now() + timedelta(days=1)

        expense1 = Expense(
            amount=Decimal("25.00"),
            currency="USD",
            description="Yesterday Expense",
            status="completed",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=yesterday,
        )
        expense2 = Expense(
            amount=Decimal("75.00"),
            currency="USD",
            description="Tomorrow Expense",
            status="completed",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=tomorrow,
        )
        expense_repo.create(expense1)
        expense_repo.create(expense2)

        # Filter by today's date
        today_expenses = expense_repo.get_user_expenses(
            sample_user.id, start_date=date.today(), end_date=date.today()
        )

        assert len(today_expenses) == 0  # No expenses for today

    def test_get_user_expenses_empty_database(self, expense_repo, sample_user):
        """Test getting user expenses from empty database."""
        expenses = expense_repo.get_user_expenses(sample_user.id)

        assert expenses == []

    def test_create_expense_with_recurring(
        self, expense_repo, sample_user, sample_category
    ):
        """Test creating a recurring expense."""
        expense = Expense(
            amount=Decimal("100.00"),
            currency="USD",
            description="Monthly Rent",
            status="completed",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
            is_recurring=True,
            recurring_frequency="monthly",
        )

        created_expense = expense_repo.create(expense)

        assert created_expense.id is not None
        assert created_expense.is_recurring is True
        assert created_expense.recurring_frequency == "monthly"

    def test_create_expense_with_different_currencies(
        self, expense_repo, sample_user, sample_category
    ):
        """Test creating expenses with different currencies."""
        currencies = ["USD", "EUR", "GBP", "JPY"]

        for currency in currencies:
            expense = Expense(
                amount=Decimal("100.00"),
                currency=currency,
                description=f"Expense in {currency}",
                status="completed",
                user_id=sample_user.id,
                category_id=sample_category.id,
                expense_date=datetime.now(),
            )

            created_expense = expense_repo.create(expense)
            assert created_expense.currency == currency

    def test_get_user_expenses_multiple_filters(
        self, expense_repo, sample_user, sample_category
    ):
        """Test getting user expenses with multiple filters."""
        # Create expenses with different attributes
        expense1 = Expense(
            amount=Decimal("25.00"),
            currency="USD",
            description="Completed Expense",
            status="completed",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
        )
        expense2 = Expense(
            amount=Decimal("75.00"),
            currency="USD",
            description="Pending Expense",
            status="pending",
            user_id=sample_user.id,
            category_id=sample_category.id,
            expense_date=datetime.now(),
        )
        expense_repo.create(expense1)
        expense_repo.create(expense2)

        # Filter by both status and category
        filtered_expenses = expense_repo.get_user_expenses(
            sample_user.id, category_id=sample_category.id, status="completed"
        )

        assert len(filtered_expenses) == 1  # Only the completed expense
        assert all(exp.status == "completed" for exp in filtered_expenses)
        assert all(exp.category_id == sample_category.id for exp in filtered_expenses)
