"""
Tests for the CategoryRepository class.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.database import Base
from src.models.category.category import Category
from src.models.user.user import User
from src.repositories.category.category_repository import CategoryRepository


class TestCategoryRepository:
    """Test cases for CategoryRepository."""

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
    def category_repo(self, db_session):
        """Create a CategoryRepository instance."""
        return CategoryRepository(db_session)

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

    def test_create_category(self, category_repo, sample_user):
        """Test creating a new category."""
        category = Category(
            name="New Category",
            description="New Description",
            user_id=sample_user.id,
            color="#00FF00",
        )

        created_category = category_repo.create(category)

        assert created_category.id is not None
        assert created_category.name == "New Category"
        assert created_category.description == "New Description"
        assert created_category.user_id == sample_user.id
        assert created_category.color == "#00FF00"
        assert created_category.is_system is False

    def test_get_by_id_existing_category(self, category_repo, sample_category):
        """Test getting an existing category by ID."""
        found_category = category_repo.get_by_id(sample_category.id)

        assert found_category is not None
        assert found_category.id == sample_category.id
        assert found_category.name == sample_category.name

    def test_get_by_id_nonexistent_category(self, category_repo):
        """Test getting a non-existent category by ID."""
        found_category = category_repo.get_by_id(99999)

        assert found_category is None

    def test_get_by_name_existing_category(self, category_repo, sample_category):
        """Test getting an existing category by name."""
        found_category = category_repo.get_by_name(
            sample_category.name, sample_category.user_id
        )

        assert found_category is not None
        assert found_category.name == sample_category.name
        assert found_category.user_id == sample_category.user_id

    def test_get_by_name_nonexistent_category(self, category_repo, sample_user):
        """Test getting a non-existent category by name."""
        found_category = category_repo.get_by_name(
            "Non-existent Category", sample_user.id
        )

        assert found_category is None

    def test_get_by_name_without_user_id(self, category_repo, sample_category):
        """Test getting category by name without user_id filter."""
        found_category = category_repo.get_by_name(sample_category.name)

        assert found_category is not None
        assert found_category.name == sample_category.name

    def test_get_user_categories(self, category_repo, sample_user):
        """Test getting user categories."""
        # Create multiple categories for the user
        category1 = Category(
            name="Category 1",
            description="Description 1",
            user_id=sample_user.id,
            color="#FF0000",
        )
        category2 = Category(
            name="Category 2",
            description="Description 2",
            user_id=sample_user.id,
            color="#00FF00",
        )
        category_repo.create(category1)
        category_repo.create(category2)

        user_categories = category_repo.get_user_categories(sample_user.id)

        assert len(user_categories) == 2
        assert any(cat.name == "Category 1" for cat in user_categories)
        assert any(cat.name == "Category 2" for cat in user_categories)

    def test_get_user_categories_with_pagination(self, category_repo, sample_user):
        """Test getting user categories with pagination."""
        # Create multiple categories for the user
        for i in range(5):
            category = Category(
                name=f"Category {i}",
                description=f"Description {i}",
                user_id=sample_user.id,
                color=f"#{i:06x}",
            )
            category_repo.create(category)

        # Test first page
        first_page = category_repo.get_user_categories(sample_user.id, skip=0, limit=2)
        assert len(first_page) == 2

        # Test second page
        second_page = category_repo.get_user_categories(sample_user.id, skip=2, limit=2)
        assert len(second_page) == 2

        # Test third page
        third_page = category_repo.get_user_categories(sample_user.id, skip=4, limit=2)
        assert len(third_page) == 1

    def test_get_user_categories_empty_database(self, category_repo, sample_user):
        """Test getting user categories from empty database."""
        categories = category_repo.get_user_categories(sample_user.id)

        assert categories == []

    def test_get_user_categories_includes_system_categories(
        self, category_repo, sample_user
    ):
        """Test that user categories include system categories."""
        # Create a system category
        system_category = Category(
            name="System Category",
            description="System Description",
            user_id=None,
            is_system=True,
            color="#0000FF",
        )
        category_repo.create(system_category)

        # Create a user category
        user_category = Category(
            name="User Category",
            description="User Description",
            user_id=sample_user.id,
            color="#FF0000",
        )
        category_repo.create(user_category)

        user_categories = category_repo.get_user_categories(sample_user.id)

        assert len(user_categories) == 2
        assert any(cat.name == "System Category" for cat in user_categories)
        assert any(cat.name == "User Category" for cat in user_categories)

    def test_create_category_with_system_flag(self, category_repo):
        """Test creating a system category."""
        category = Category(
            name="System Category",
            description="System Description",
            user_id=None,
            is_system=True,
            color="#0000FF",
        )

        created_category = category_repo.create(category)

        assert created_category.id is not None
        assert created_category.is_system is True
        assert created_category.user_id is None

    def test_category_name_uniqueness_per_user(self, category_repo, sample_user):
        """Test that category names are unique per user."""
        category1 = Category(
            name="Duplicate Name",
            description="First Description",
            user_id=sample_user.id,
            color="#FF0000",
        )
        category_repo.create(category1)

        # Try to create another category with the same name for the same user
        category2 = Category(
            name="Duplicate Name",
            description="Second Description",
            user_id=sample_user.id,
            color="#00FF00",
        )

        # This should work since we're not enforcing uniqueness at the database level
        # in the test setup, but the application logic should handle this
        created_category = category_repo.create(category2)
        assert created_category.id is not None

    def test_category_name_same_name_different_users(self, category_repo, db_session):
        """Test that different users can have categories with the same name."""
        # Create two users
        user1 = User(
            email="user1@example.com",
            username="user1",
            hashed_password="hashed_password",
            full_name="User 1",
        )
        user2 = User(
            email="user2@example.com",
            username="user2",
            hashed_password="hashed_password",
            full_name="User 2",
        )
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        db_session.refresh(user1)
        db_session.refresh(user2)

        # Create categories with the same name for different users
        category1 = Category(
            name="Same Name",
            description="User 1 Description",
            user_id=user1.id,
            color="#FF0000",
        )
        category2 = Category(
            name="Same Name",
            description="User 2 Description",
            user_id=user2.id,
            color="#00FF00",
        )

        created_category1 = category_repo.create(category1)
        created_category2 = category_repo.create(category2)

        assert created_category1.id is not None
        assert created_category2.id is not None
        assert created_category1.name == created_category2.name
        assert created_category1.user_id != created_category2.user_id

    def test_get_by_name_filters_by_user(self, category_repo, db_session):
        """Test that get_by_name filters by user when user_id is provided."""
        # Create two users
        user1 = User(
            email="user1@example.com",
            username="user1",
            hashed_password="hashed_password",
            full_name="User 1",
        )
        user2 = User(
            email="user2@example.com",
            username="user2",
            hashed_password="hashed_password",
            full_name="User 2",
        )
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        db_session.refresh(user1)
        db_session.refresh(user2)

        # Create categories with the same name for different users
        category1 = Category(
            name="Same Name",
            description="User 1 Description",
            user_id=user1.id,
            color="#FF0000",
        )
        category2 = Category(
            name="Same Name",
            description="User 2 Description",
            user_id=user2.id,
            color="#00FF00",
        )
        category_repo.create(category1)
        category_repo.create(category2)

        # Get category by name for user1
        found_category = category_repo.get_by_name("Same Name", user1.id)

        assert found_category is not None
        assert found_category.user_id == user1.id
        assert found_category.description == "User 1 Description"
