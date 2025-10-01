"""
Tests for User model.
"""

from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from src.models.user.user import User
from src.services.authentication.password_service import get_password_hash


class TestUserModel:
    """Test cases for User model."""

    def test_user_creation(self, db_session):
        """Test creating a user with valid data."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            full_name="Test User",
            is_active=True,
            is_superuser=False,
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_superuser is False
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_user_creation_minimal_data(self, db_session):
        """Test creating a user with minimal required data."""
        user = User(
            email="minimal@example.com",
            username="minimaluser",
            hashed_password=get_password_hash("password123"),
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.email == "minimal@example.com"
        assert user.username == "minimaluser"
        assert user.full_name is None
        assert user.is_active is True  # Default value
        assert user.is_superuser is False  # Default value

    def test_user_email_unique_constraint(self, db_session):
        """Test that email must be unique."""
        user1 = User(
            email="duplicate@example.com",
            username="user1",
            hashed_password=get_password_hash("password123"),
        )

        user2 = User(
            email="duplicate@example.com",
            username="user2",
            hashed_password=get_password_hash("password123"),
        )

        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_username_unique_constraint(self, db_session):
        """Test that username must be unique."""
        user1 = User(
            email="user1@example.com",
            username="duplicate_username",
            hashed_password=get_password_hash("password123"),
        )

        user2 = User(
            email="user2@example.com",
            username="duplicate_username",
            hashed_password=get_password_hash("password123"),
        )

        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_repr(self, db_session):
        """Test user string representation."""
        user = User(
            email="repr@example.com",
            username="repruser",
            hashed_password=get_password_hash("password123"),
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        repr_str = repr(user)
        assert "User" in repr_str
        assert str(user.id) in repr_str
        assert "repr@example.com" in repr_str
        assert "repruser" in repr_str

    def test_user_relationships(self, db_session, test_user):
        """Test user relationships with expenses and categories."""
        # Test that relationships are properly set up
        assert hasattr(test_user, "expenses")
        assert hasattr(test_user, "categories")

        # Test that relationships return empty lists initially
        assert test_user.expenses == []
        assert test_user.categories == []

    def test_user_timestamps(self, db_session):
        """Test that created_at and updated_at are set automatically."""
        user = User(
            email="timestamps@example.com",
            username="timestampsuser",
            hashed_password=get_password_hash("password123"),
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.created_at <= datetime.utcnow()
        assert user.updated_at <= datetime.utcnow()

    def test_user_default_values(self, db_session):
        """Test default values for user fields."""
        user = User(
            email="defaults@example.com",
            username="defaultsuser",
            hashed_password=get_password_hash("password123"),
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.is_active is True
        assert user.is_superuser is False

    @pytest.mark.parametrize(
        "email",
        [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@numbers.com",
        ],
    )
    def test_valid_email_formats(self, db_session, email):
        """Test that valid email formats are accepted."""
        user = User(
            email=email,
            username=f"user_{email.split('@')[0]}",
            hashed_password=get_password_hash("password123"),
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.email == email

    def test_user_update_timestamps(self, db_session):
        """Test that updated_at changes when user is modified."""
        user = User(
            email="update@example.com",
            username="updateuser",
            hashed_password=get_password_hash("password123"),
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        original_updated_at = user.updated_at

        # Wait a small amount to ensure timestamp difference
        import time

        time.sleep(0.01)

        # Update user
        user.full_name = "Updated Name"
        db_session.commit()
        db_session.refresh(user)

        assert user.updated_at > original_updated_at

    def test_user_password_hashing(self, db_session):
        """Test that password is properly hashed."""
        password = "testpassword123"
        user = User(
            email="password@example.com",
            username="passworduser",
            hashed_password=get_password_hash(password),
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        # Password should be hashed, not plain text
        assert user.hashed_password != password
        assert len(user.hashed_password) > 50  # bcrypt hashes are long
        assert user.hashed_password.startswith("$2b$")  # bcrypt prefix
