"""
Tests for the Category model.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.database import Base
from src.models.category.category import Category
from src.models.user.user import User


class TestCategoryModel:
    """Test cases for Category model."""

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

    def test_category_creation(self, db_session, sample_user):
        """Test creating a category."""
        category = Category(
            name="Test Category",
            description="Test Description",
            user_id=sample_user.id,
            color="#FF0000",
        )

        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        assert category.id is not None
        assert category.name == "Test Category"
        assert category.description == "Test Description"
        assert category.user_id == sample_user.id
        assert category.color == "#FF0000"
        assert category.is_system is False

    def test_category_creation_with_system_flag(self, db_session):
        """Test creating a system category."""
        category = Category(
            name="System Category",
            description="System Description",
            user_id=None,
            is_system=True,
            color="#0000FF",
        )

        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        assert category.id is not None
        assert category.name == "System Category"
        assert category.description == "System Description"
        assert category.user_id is None
        assert category.is_system is True
        assert category.color == "#0000FF"

    def test_category_creation_with_minimal_data(self, db_session, sample_user):
        """Test creating a category with minimal required data."""
        category = Category(name="Minimal Category", user_id=sample_user.id)

        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        assert category.id is not None
        assert category.name == "Minimal Category"
        assert category.user_id == sample_user.id
        assert category.description is None
        assert category.color is None
        assert category.is_system is False

    def test_category_timestamps(self, db_session, sample_user):
        """Test that timestamps are automatically set."""
        category = Category(name="Timestamp Test", user_id=sample_user.id)

        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        assert category.created_at is not None
        assert category.updated_at is not None
        # Allow for small time differences due to processing
        time_diff = abs((category.updated_at - category.created_at).total_seconds())
        assert time_diff < 1.0  # Less than 1 second difference

    def test_category_update_timestamp(self, db_session, sample_user):
        """Test that updated_at changes when category is modified."""
        category = Category(name="Update Test", user_id=sample_user.id)

        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        original_updated_at = category.updated_at

        # Update the category
        category.description = "Updated Description"
        db_session.commit()
        db_session.refresh(category)

        assert category.updated_at > original_updated_at

    def test_category_user_relationship(self, db_session, sample_user):
        """Test the relationship between category and user."""
        category = Category(name="Relationship Test", user_id=sample_user.id)

        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        # Test that we can access the user through the relationship
        assert category.user is not None
        assert category.user.id == sample_user.id
        assert category.user.email == sample_user.email

    def test_category_expenses_relationship(self, db_session, sample_user):
        """Test the relationship between category and expenses."""
        from datetime import datetime
        from decimal import Decimal

        from src.models.expense.expense import Expense

        category = Category(name="Expense Test", user_id=sample_user.id)

        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        # Create an expense for this category
        expense = Expense(
            amount=Decimal("100.00"),
            currency="USD",
            description="Test Expense",
            status="completed",
            user_id=sample_user.id,
            category_id=category.id,
            expense_date=datetime.now(),
        )

        db_session.add(expense)
        db_session.commit()
        db_session.refresh(expense)

        # Test that we can access expenses through the relationship
        assert len(category.expenses) == 1
        assert category.expenses[0].id == expense.id
        assert category.expenses[0].description == "Test Expense"

    def test_category_string_representation(self, db_session, sample_user):
        """Test the string representation of a category."""
        category = Category(name="String Test", user_id=sample_user.id)

        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        # Test __repr__ method
        repr_str = repr(category)
        assert "Category" in repr_str
        assert str(category.id) in repr_str
        assert "String Test" in repr_str

    def test_category_equality(self, db_session, sample_user):
        """Test category equality."""
        category1 = Category(name="Equality Test 1", user_id=sample_user.id)
        category2 = Category(name="Equality Test 2", user_id=sample_user.id)

        db_session.add(category1)
        db_session.add(category2)
        db_session.commit()
        db_session.refresh(category1)
        db_session.refresh(category2)

        # Different categories should not be equal
        assert category1 != category2

        # Same category should be equal to itself
        assert category1 == category1

    def test_category_with_different_colors(self, db_session, sample_user):
        """Test creating categories with different colors."""
        colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF"]

        for i, color in enumerate(colors):
            category = Category(
                name=f"Color Test {i}", user_id=sample_user.id, color=color
            )

            db_session.add(category)
            db_session.commit()
            db_session.refresh(category)

            assert category.color == color

    def test_category_with_long_description(self, db_session, sample_user):
        """Test creating a category with a long description."""
        long_description = "This is a very long description for testing purposes. " * 10

        category = Category(
            name="Long Description Test",
            description=long_description,
            user_id=sample_user.id,
        )

        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        assert category.description == long_description
        assert len(category.description) > 100

    def test_category_system_vs_user_categories(self, db_session, sample_user):
        """Test creating both system and user categories."""
        # Create a system category
        system_category = Category(
            name="System Category",
            description="System Description",
            user_id=None,
            is_system=True,
            color="#000000",
        )

        # Create a user category
        user_category = Category(
            name="User Category",
            description="User Description",
            user_id=sample_user.id,
            is_system=False,
            color="#FFFFFF",
        )

        db_session.add(system_category)
        db_session.add(user_category)
        db_session.commit()
        db_session.refresh(system_category)
        db_session.refresh(user_category)

        assert system_category.is_system is True
        assert system_category.user_id is None
        assert user_category.is_system is False
        assert user_category.user_id == sample_user.id
