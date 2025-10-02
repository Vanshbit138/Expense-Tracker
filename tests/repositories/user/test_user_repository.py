"""
Tests for UserRepository.
"""

from src.models.user.user import User
from src.repositories.user.user_repository import UserRepository
from src.services.authentication.password_service import get_password_hash


class TestUserRepository:
    """Test cases for UserRepository."""

    def test_create_user(self, db_session):
        """Test creating a user through repository."""
        user_repo = UserRepository(db_session)

        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("Pass123!"),
            full_name="Test User",
        )

        created_user = user_repo.create(user)

        assert created_user.id is not None
        assert created_user.email == "test@example.com"
        assert created_user.username == "testuser"
        assert created_user.full_name == "Test User"

    def test_get_by_id_existing_user(self, db_session, test_user):
        """Test getting user by ID when user exists."""
        user_repo = UserRepository(db_session)

        found_user = user_repo.get_by_id(test_user.id)

        assert found_user is not None
        assert found_user.id == test_user.id
        assert found_user.email == test_user.email

    def test_get_by_id_nonexistent_user(self, db_session):
        """Test getting user by ID when user doesn't exist."""
        user_repo = UserRepository(db_session)

        found_user = user_repo.get_by_id(99999)

        assert found_user is None

    def test_get_by_email_existing_user(self, db_session, test_user):
        """Test getting user by email when user exists."""
        user_repo = UserRepository(db_session)

        found_user = user_repo.get_by_email(test_user.email)

        assert found_user is not None
        assert found_user.email == test_user.email
        assert found_user.id == test_user.id

    def test_get_by_email_nonexistent_user(self, db_session):
        """Test getting user by email when user doesn't exist."""
        user_repo = UserRepository(db_session)

        found_user = user_repo.get_by_email("nonexistent@example.com")

        assert found_user is None

    def test_get_by_username_existing_user(self, db_session, test_user):
        """Test getting user by username when user exists."""
        user_repo = UserRepository(db_session)

        found_user = user_repo.get_by_username(test_user.username)

        assert found_user is not None
        assert found_user.username == test_user.username
        assert found_user.id == test_user.id

    def test_get_by_username_nonexistent_user(self, db_session):
        """Test getting user by username when user doesn't exist."""
        user_repo = UserRepository(db_session)

        found_user = user_repo.get_by_username("nonexistentuser")

        assert found_user is None

    def test_get_all_users(self, db_session, test_user, test_user_2):
        """Test getting all users."""
        user_repo = UserRepository(db_session)

        users = user_repo.get_all()

        assert len(users) == 2
        user_ids = [user.id for user in users]
        assert test_user.id in user_ids
        assert test_user_2.id in user_ids

    def test_get_all_users_with_pagination(self, db_session):
        """Test getting users with pagination."""
        # Create multiple users
        users = []
        for i in range(5):
            user = User(
                email=f"user{i}@example.com",
                username=f"user{i}",
                hashed_password=get_password_hash("Pass123!"),
            )
            db_session.add(user)
            users.append(user)

        db_session.commit()

        user_repo = UserRepository(db_session)

        # Test pagination
        first_page = user_repo.get_all(skip=0, limit=2)
        second_page = user_repo.get_all(skip=2, limit=2)

        assert len(first_page) == 2
        assert len(second_page) == 2
        assert first_page[0].id != second_page[0].id

    def test_update_user(self, db_session, test_user):
        """Test updating a user."""
        user_repo = UserRepository(db_session)

        # Update user
        test_user.full_name = "Updated Name"
        test_user.email = "updated@example.com"

        user_repo.update(test_user)

        assert test_user.full_name == "Updated Name"
        assert test_user.email == "updated@example.com"

    def test_delete_existing_user(self, db_session, test_user):
        """Test deleting an existing user."""
        user_repo = UserRepository(db_session)
        user_id = test_user.id

        result = user_repo.delete(user_id)

        assert result is True

        # Verify user is deleted
        deleted_user = user_repo.get_by_id(user_id)
        assert deleted_user is None

    def test_delete_nonexistent_user(self, db_session):
        """Test deleting a non-existent user."""
        user_repo = UserRepository(db_session)

        result = user_repo.delete(99999)

        assert result is False

    def test_is_email_taken_existing_email(self, db_session, test_user):
        """Test checking if email is taken when it exists."""
        user_repo = UserRepository(db_session)

        result = user_repo.is_email_taken(test_user.email)

        assert result is True

    def test_is_email_taken_nonexistent_email(self, db_session):
        """Test checking if email is taken when it doesn't exist."""
        user_repo = UserRepository(db_session)

        result = user_repo.is_email_taken("nonexistent@example.com")

        assert result is False

    def test_is_email_taken_exclude_user(self, db_session, test_user):
        """Test checking if email is taken excluding specific user."""
        user_repo = UserRepository(db_session)

        # Should return False when excluding the user who has the email
        result = user_repo.is_email_taken(test_user.email, exclude_user_id=test_user.id)

        assert result is False

    def test_is_username_taken_existing_username(self, db_session, test_user):
        """Test checking if username is taken when it exists."""
        user_repo = UserRepository(db_session)

        result = user_repo.is_username_taken(test_user.username)

        assert result is True

    def test_is_username_taken_nonexistent_username(self, db_session):
        """Test checking if username is taken when it doesn't exist."""
        user_repo = UserRepository(db_session)

        result = user_repo.is_username_taken("nonexistentuser")

        assert result is False

    def test_is_username_taken_exclude_user(self, db_session, test_user):
        """Test checking if username is taken excluding specific user."""
        user_repo = UserRepository(db_session)

        # Should return False when excluding the user who has the username
        result = user_repo.is_username_taken(
            test_user.username, exclude_user_id=test_user.id
        )

        assert result is False

    def test_repository_initialization(self, db_session):
        """Test repository initialization with database session."""
        user_repo = UserRepository(db_session)

        assert user_repo.db == db_session

    def test_create_user_commits_to_database(self, db_session):
        """Test that create method commits changes to database."""
        user_repo = UserRepository(db_session)

        user = User(
            email="commit@example.com",
            username="committest",
            hashed_password=get_password_hash("Pass123!"),
        )

        created_user = user_repo.create(user)

        # Verify user was committed to database
        found_user = user_repo.get_by_id(created_user.id)
        assert found_user is not None
        assert found_user.email == "commit@example.com"

    def test_update_user_commits_to_database(self, db_session, test_user):
        """Test that update method commits changes to database."""
        user_repo = UserRepository(db_session)

        test_user.full_name = "Database Updated"
        user_repo.update(test_user)

        # Verify changes were committed
        found_user = user_repo.get_by_id(test_user.id)
        assert found_user.full_name == "Database Updated"

    def test_delete_user_commits_to_database(self, db_session, test_user):
        """Test that delete method commits changes to database."""
        user_repo = UserRepository(db_session)
        user_id = test_user.id

        result = user_repo.delete(user_id)

        assert result is True

        # Verify user was actually deleted from database
        found_user = user_repo.get_by_id(user_id)
        assert found_user is None

    def test_get_all_empty_database(self, db_session):
        """Test getting all users from empty database."""
        user_repo = UserRepository(db_session)

        users = user_repo.get_all()

        assert users == []

    def test_get_all_with_large_limit(self, db_session, test_user):
        """Test getting all users with limit larger than total users."""
        user_repo = UserRepository(db_session)

        users = user_repo.get_all(skip=0, limit=1000)

        assert len(users) == 1
        assert users[0].id == test_user.id

    def test_get_all_with_skip_larger_than_total(self, db_session, test_user):
        """Test getting all users with skip larger than total users."""
        user_repo = UserRepository(db_session)

        users = user_repo.get_all(skip=1000, limit=10)

        assert users == []
