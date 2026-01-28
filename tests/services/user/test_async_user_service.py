"""
Comprehensive tests for async user service module.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ConflictError, ValidationError
from src.models.user.user import User
from src.schemas.user.user import UserCreate, UserUpdate
from src.schemas.user.user_queries import (
    AuthenticationQuery,
    PasswordChangeQuery,
    UserFilter,
    UserQuery,
    UserValidation,
)
from src.services.user.async_user_service import AsyncUserRepository, AsyncUserService


class TestAsyncUserRepository:
    """Test cases for AsyncUserRepository."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock async database session."""
        session = AsyncMock(spec=AsyncSession)
        # Add query attribute for compatibility with the repository code
        session.query = Mock()
        return session

    @pytest.fixture
    def mock_user_model(self):
        """Create a mock User model."""
        model = Mock()
        return model

    @pytest.fixture
    def async_user_repo(self, mock_db_session, mock_user_model):
        """Create an AsyncUserRepository instance for testing."""
        return AsyncUserRepository(mock_user_model, mock_db_session)

    @pytest.fixture
    def sample_user(self):
        """Create a sample user instance."""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.username = "testuser"
        user.full_name = "Test User"
        user.hashed_password = "hashed_password"
        user.is_active = True
        return user

    @pytest.mark.asyncio
    async def test_get_by_email_success(self, async_user_repo, sample_user):
        """Test successful get user by email."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_user
        async_user_repo.db.execute.return_value = mock_result

        result = await async_user_repo.get_by_email("test@example.com")

        async_user_repo.db.execute.assert_called_once()
        assert result == sample_user

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, async_user_repo):
        """Test get user by email when not found."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        async_user_repo.db.execute.return_value = mock_result

        result = await async_user_repo.get_by_email("nonexistent@example.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_email_exception(self, async_user_repo):
        """Test get user by email with exception."""
        async_user_repo.db.execute.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            await async_user_repo.get_by_email("test@example.com")

    @pytest.mark.asyncio
    async def test_get_by_username_success(self, async_user_repo, sample_user):
        """Test successful get user by username."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_user
        async_user_repo.db.execute.return_value = mock_result

        result = await async_user_repo.get_by_username("testuser")

        async_user_repo.db.execute.assert_called_once()
        assert result == sample_user

    @pytest.mark.asyncio
    async def test_get_by_username_not_found(self, async_user_repo):
        """Test get user by username when not found."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        async_user_repo.db.execute.return_value = mock_result

        result = await async_user_repo.get_by_username("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_username_exception(self, async_user_repo):
        """Test get user by username with exception."""
        async_user_repo.db.execute.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            await async_user_repo.get_by_username("testuser")

    @pytest.mark.asyncio
    async def test_is_email_taken_true(self, async_user_repo, sample_user):
        """Test is email taken when email exists."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_user
        async_user_repo.db.execute.return_value = mock_result

        result = await async_user_repo.is_email_taken("test@example.com")

        assert result is True

    @pytest.mark.asyncio
    async def test_is_email_taken_false(self, async_user_repo):
        """Test is email taken when email doesn't exist."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        async_user_repo.db.execute.return_value = mock_result

        result = await async_user_repo.is_email_taken("nonexistent@example.com")

        assert result is False

    @pytest.mark.asyncio
    async def test_is_email_taken_with_exclude(self, async_user_repo):
        """Test is email taken with exclude user ID."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        async_user_repo.db.execute.return_value = mock_result

        result = await async_user_repo.is_email_taken(
            "test@example.com", exclude_user_id=1
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_is_email_taken_exception(self, async_user_repo):
        """Test is email taken with exception."""
        async_user_repo.db.execute.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            await async_user_repo.is_email_taken("test@example.com")

    @pytest.mark.asyncio
    async def test_is_username_taken_true(self, async_user_repo, sample_user):
        """Test is username taken when username exists."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = sample_user
        async_user_repo.db.execute.return_value = mock_result

        result = await async_user_repo.is_username_taken("testuser")

        assert result is True

    @pytest.mark.asyncio
    async def test_is_username_taken_false(self, async_user_repo):
        """Test is username taken when username doesn't exist."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        async_user_repo.db.execute.return_value = mock_result

        result = await async_user_repo.is_username_taken("nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_is_username_taken_with_exclude(self, async_user_repo):
        """Test is username taken with exclude user ID."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        async_user_repo.db.execute.return_value = mock_result

        result = await async_user_repo.is_username_taken("testuser", exclude_user_id=1)

        assert result is False

    @pytest.mark.asyncio
    async def test_is_username_taken_exception(self, async_user_repo):
        """Test is username taken with exception."""
        async_user_repo.db.execute.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            await async_user_repo.is_username_taken("testuser")


class TestAsyncUserService:
    """Test cases for AsyncUserService."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock async database session."""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def mock_user_repo(self):
        """Create a mock async user repository."""
        repo = AsyncMock()
        return repo

    @pytest.fixture
    def async_user_service(self, mock_db_session, mock_user_repo):
        """Create an AsyncUserService instance for testing."""
        with patch(
            "src.services.user.async_user_service.AsyncUserRepository",
            return_value=mock_user_repo,
        ):
            service = AsyncUserService(mock_db_session)
            service.user_repo = mock_user_repo
            return service

    @pytest.fixture
    def sample_user_data(self):
        """Create sample user data for testing."""
        return UserCreate(
            email="test@example.com",
            username="testuser",
            password="TestPassword123!",
            full_name="Test User",
        )

    @pytest.fixture
    def sample_user(self):
        """Create a sample user instance."""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.username = "testuser"
        user.full_name = "Test User"
        user.hashed_password = "hashed_password"
        user.is_active = True
        return user

    def test_async_user_service_initialization(self, mock_db_session):
        """Test AsyncUserService initialization."""
        with patch(
            "src.services.user.async_user_service.AsyncUserRepository"
        ) as mock_repo_class:
            service = AsyncUserService(mock_db_session)
            assert service.db == mock_db_session
            mock_repo_class.assert_called_once_with(User, mock_db_session)

    @pytest.mark.asyncio
    async def test_create_user_success(
        self, async_user_service, sample_user_data, sample_user
    ):
        """Test successful user creation."""
        async_user_service.user_repo.is_email_taken.return_value = False
        async_user_service.user_repo.is_username_taken.return_value = False
        async_user_service.user_repo.create.return_value = sample_user

        result = await async_user_service.create_user(sample_user_data)

        async_user_service.user_repo.create.assert_called_once()
        assert result == sample_user

    @pytest.mark.asyncio
    async def test_create_user_email_conflict(
        self, async_user_service, sample_user_data
    ):
        """Test user creation with email conflict."""
        async_user_service.user_repo.is_email_taken.return_value = True

        with pytest.raises(ConflictError, match="Email already registered"):
            await async_user_service.create_user(sample_user_data)

    @pytest.mark.asyncio
    async def test_create_user_username_conflict(
        self, async_user_service, sample_user_data
    ):
        """Test user creation with username conflict."""
        async_user_service.user_repo.is_email_taken.return_value = False
        async_user_service.user_repo.is_username_taken.return_value = True

        with pytest.raises(ConflictError, match="Username already taken"):
            await async_user_service.create_user(sample_user_data)

    @pytest.mark.asyncio
    async def test_create_user_exception(self, async_user_service, sample_user_data):
        """Test user creation with exception."""
        async_user_service.user_repo.is_email_taken.return_value = False
        async_user_service.user_repo.is_username_taken.return_value = False
        async_user_service.user_repo.create.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            await async_user_service.create_user(sample_user_data)

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, async_user_service, sample_user):
        """Test successful get user by ID."""
        user_query = UserQuery(user_id=1)
        async_user_service.user_repo.get_by_id.return_value = sample_user

        result = await async_user_service.get_user_by_id(user_query)

        async_user_service.user_repo.get_by_id.assert_called_once_with(1)
        assert result == sample_user

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, async_user_service):
        """Test get user by ID when not found."""
        user_query = UserQuery(user_id=999)
        async_user_service.user_repo.get_by_id.return_value = None

        result = await async_user_service.get_user_by_id(user_query)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_id_exception(self, async_user_service):
        """Test get user by ID with exception."""
        user_query = UserQuery(user_id=1)
        async_user_service.user_repo.get_by_id.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            await async_user_service.get_user_by_id(user_query)

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, async_user_service, sample_user):
        """Test successful get user by email."""
        async_user_service.user_repo.get_by_email.return_value = sample_user

        result = await async_user_service.get_user_by_email("test@example.com")

        async_user_service.user_repo.get_by_email.assert_called_once_with(
            "test@example.com"
        )
        assert result == sample_user

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, async_user_service):
        """Test get user by email when not found."""
        async_user_service.user_repo.get_by_email.return_value = None

        result = await async_user_service.get_user_by_email("nonexistent@example.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_email_exception(self, async_user_service):
        """Test get user by email with exception."""
        async_user_service.user_repo.get_by_email.side_effect = Exception(
            "Database error"
        )

        with pytest.raises(Exception, match="Database error"):
            await async_user_service.get_user_by_email("test@example.com")

    @pytest.mark.asyncio
    async def test_get_user_by_username_success(self, async_user_service, sample_user):
        """Test successful get user by username."""
        async_user_service.user_repo.get_by_username.return_value = sample_user

        result = await async_user_service.get_user_by_username("testuser")

        async_user_service.user_repo.get_by_username.assert_called_once_with("testuser")
        assert result == sample_user

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, async_user_service):
        """Test get user by username when not found."""
        async_user_service.user_repo.get_by_username.return_value = None

        result = await async_user_service.get_user_by_username("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_username_exception(self, async_user_service):
        """Test get user by username with exception."""
        async_user_service.user_repo.get_by_username.side_effect = Exception(
            "Database error"
        )

        with pytest.raises(Exception, match="Database error"):
            await async_user_service.get_user_by_username("testuser")

    @pytest.mark.asyncio
    async def test_get_users_success(self, async_user_service, sample_user):
        """Test successful get users."""
        user_filter = UserFilter(skip=0, limit=10)
        async_user_service.user_repo.get_multi.return_value = [sample_user]

        result = await async_user_service.get_users(user_filter)

        async_user_service.user_repo.get_multi.assert_called_once_with(skip=0, limit=10)
        assert result == [sample_user]

    @pytest.mark.asyncio
    async def test_get_users_exception(self, async_user_service):
        """Test get users with exception."""
        user_filter = UserFilter(skip=0, limit=10)
        async_user_service.user_repo.get_multi.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            await async_user_service.get_users(user_filter)

    @pytest.mark.asyncio
    async def test_update_user_success(self, async_user_service, sample_user):
        """Test successful user update."""
        update_data = UserUpdate(email="new@example.com", full_name="New Name")
        updated_user = Mock(spec=User)
        updated_user.id = 1

        async_user_service.user_repo.get_by_id.return_value = sample_user
        async_user_service.user_repo.is_email_taken.return_value = False
        async_user_service.user_repo.update.return_value = updated_user

        result = await async_user_service.update_user(user_id=1, user_data=update_data)

        assert result == updated_user

    @pytest.mark.asyncio
    async def test_update_user_not_found(self, async_user_service):
        """Test update user when user not found."""
        update_data = UserUpdate(email="new@example.com")
        async_user_service.user_repo.get_by_id.return_value = None

        with pytest.raises(Exception):  # ensure_record_exists will raise
            await async_user_service.update_user(user_id=999, user_data=update_data)

    @pytest.mark.asyncio
    async def test_update_user_email_conflict(self, async_user_service, sample_user):
        """Test update user with email conflict."""
        update_data = UserUpdate(email="conflict@example.com")
        async_user_service.user_repo.get_by_id.return_value = sample_user
        async_user_service.user_repo.is_email_taken.return_value = True

        with pytest.raises(ConflictError, match="Email already registered"):
            await async_user_service.update_user(user_id=1, user_data=update_data)

    @pytest.mark.asyncio
    async def test_update_user_username_conflict(self, async_user_service, sample_user):
        """Test update user with username conflict."""
        update_data = UserUpdate(username="conflictuser")
        async_user_service.user_repo.get_by_id.return_value = sample_user
        async_user_service.user_repo.is_email_taken.return_value = False
        async_user_service.user_repo.is_username_taken.return_value = True

        with pytest.raises(ConflictError, match="Username already taken"):
            await async_user_service.update_user(user_id=1, user_data=update_data)

    @pytest.mark.asyncio
    async def test_update_user_no_changes(self, async_user_service, sample_user):
        """Test update user with no changes."""
        update_data = UserUpdate()  # Empty update
        updated_user = Mock(spec=User)
        updated_user.id = 1

        async_user_service.user_repo.get_by_id.return_value = sample_user
        async_user_service.user_repo.update.return_value = updated_user

        result = await async_user_service.update_user(user_id=1, user_data=update_data)

        assert result == updated_user

    @pytest.mark.asyncio
    async def test_update_user_exception(self, async_user_service, sample_user):
        """Test update user with exception."""
        update_data = UserUpdate(email="new@example.com")
        async_user_service.user_repo.get_by_id.return_value = sample_user
        async_user_service.user_repo.is_email_taken.return_value = False
        async_user_service.user_repo.update.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            await async_user_service.update_user(user_id=1, user_data=update_data)

    @pytest.mark.asyncio
    async def test_delete_user_success(self, async_user_service):
        """Test successful user deletion."""
        user_query = UserQuery(user_id=1)
        async_user_service.user_repo.delete.return_value = True

        result = await async_user_service.delete_user(user_query)

        async_user_service.user_repo.delete.assert_called_once_with(1)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_user_failure(self, async_user_service):
        """Test user deletion failure."""
        user_query = UserQuery(user_id=999)
        async_user_service.user_repo.delete.return_value = False

        result = await async_user_service.delete_user(user_query)

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_user_exception(self, async_user_service):
        """Test delete user with exception."""
        user_query = UserQuery(user_id=1)
        async_user_service.user_repo.delete.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            await async_user_service.delete_user(user_query)

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, async_user_service, sample_user):
        """Test successful user authentication."""
        auth_query = AuthenticationQuery(
            email="test@example.com", password="TestPassword123!"
        )
        async_user_service.user_repo.get_by_email.return_value = sample_user

        with patch(
            "src.services.user.async_user_service.verify_password", return_value=True
        ):
            result = await async_user_service.authenticate_user(auth_query)

        assert result == sample_user

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, async_user_service):
        """Test user authentication when user not found."""
        auth_query = AuthenticationQuery(
            email="nonexistent@example.com", password="password"
        )
        async_user_service.user_repo.get_by_email.return_value = None

        result = await async_user_service.authenticate_user(auth_query)

        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(
        self, async_user_service, sample_user
    ):
        """Test user authentication with wrong password."""
        auth_query = AuthenticationQuery(
            email="test@example.com", password="WrongPassword"
        )
        async_user_service.user_repo.get_by_email.return_value = sample_user

        with patch(
            "src.services.user.async_user_service.verify_password", return_value=False
        ):
            result = await async_user_service.authenticate_user(auth_query)

        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_exception(self, async_user_service):
        """Test user authentication with exception."""
        auth_query = AuthenticationQuery(email="test@example.com", password="password")
        async_user_service.user_repo.get_by_email.side_effect = Exception(
            "Database error"
        )

        with pytest.raises(Exception, match="Database error"):
            await async_user_service.authenticate_user(auth_query)

    @pytest.mark.asyncio
    async def test_change_password_success(self, async_user_service, sample_user):
        """Test successful password change."""
        password_query = PasswordChangeQuery(
            user_id=1,
            current_password="OldPassword123!",
            new_password="NewPassword123!",
        )
        async_user_service.user_repo.get_by_id.return_value = sample_user
        async_user_service.user_repo.update.return_value = sample_user

        with (
            patch(
                "src.services.user.async_user_service.verify_password",
                return_value=True,
            ),
            patch(
                "src.services.user.async_user_service.get_password_hash",
                return_value="new_hashed_password",
            ),
        ):
            result = await async_user_service.change_password(password_query)

        assert result is True
        async_user_service.user_repo.update.assert_called_once_with(
            1, {"hashed_password": "new_hashed_password"}
        )

    @pytest.mark.asyncio
    async def test_change_password_user_not_found(self, async_user_service):
        """Test password change when user not found."""
        password_query = PasswordChangeQuery(
            user_id=999,
            current_password="OldPassword123!",
            new_password="NewPassword123!",
        )
        async_user_service.user_repo.get_by_id.return_value = None

        with pytest.raises(Exception):  # ensure_record_exists will raise
            await async_user_service.change_password(password_query)

    @pytest.mark.asyncio
    async def test_change_password_wrong_current_password(
        self, async_user_service, sample_user
    ):
        """Test password change with wrong current password."""
        password_query = PasswordChangeQuery(
            user_id=1, current_password="WrongPassword", new_password="NewPassword123!"
        )
        async_user_service.user_repo.get_by_id.return_value = sample_user

        with patch(
            "src.services.user.async_user_service.verify_password", return_value=False
        ):
            with pytest.raises(ValidationError, match="Current password is incorrect"):
                await async_user_service.change_password(password_query)

    @pytest.mark.asyncio
    async def test_change_password_exception(self, async_user_service, sample_user):
        """Test password change with exception."""
        password_query = PasswordChangeQuery(
            user_id=1,
            current_password="OldPassword123!",
            new_password="NewPassword123!",
        )
        async_user_service.user_repo.get_by_id.return_value = sample_user
        async_user_service.user_repo.update.side_effect = Exception("Database error")

        with (
            patch(
                "src.services.user.async_user_service.verify_password",
                return_value=True,
            ),
            patch(
                "src.services.user.async_user_service.get_password_hash",
                return_value="new_hashed_password",
            ),
        ):
            with pytest.raises(Exception, match="Database error"):
                await async_user_service.change_password(password_query)

    @pytest.mark.asyncio
    async def test_validate_email_unique_success(self, async_user_service):
        """Test successful email uniqueness validation."""
        validation_data = UserValidation(email="test@example.com")
        async_user_service.user_repo.is_email_taken.return_value = False

        # Should not raise exception
        await async_user_service._validate_email_unique(validation_data)

    @pytest.mark.asyncio
    async def test_validate_email_unique_conflict(self, async_user_service):
        """Test email uniqueness validation with conflict."""
        validation_data = UserValidation(email="existing@example.com")
        async_user_service.user_repo.is_email_taken.return_value = True

        with pytest.raises(ConflictError, match="Email already registered"):
            await async_user_service._validate_email_unique(validation_data)

    @pytest.mark.asyncio
    async def test_validate_email_unique_with_exclude(self, async_user_service):
        """Test email uniqueness validation with exclude user ID."""
        validation_data = UserValidation(email="test@example.com")
        async_user_service.user_repo.is_email_taken.return_value = False

        # Should not raise exception
        await async_user_service._validate_email_unique(
            validation_data, exclude_user_id=1
        )

    @pytest.mark.asyncio
    async def test_validate_username_unique_success(self, async_user_service):
        """Test successful username uniqueness validation."""
        validation_data = UserValidation(username="testuser")
        async_user_service.user_repo.is_username_taken.return_value = False

        # Should not raise exception
        await async_user_service._validate_username_unique(validation_data)

    @pytest.mark.asyncio
    async def test_validate_username_unique_conflict(self, async_user_service):
        """Test username uniqueness validation with conflict."""
        validation_data = UserValidation(username="existinguser")
        async_user_service.user_repo.is_username_taken.return_value = True

        with pytest.raises(ConflictError, match="Username already taken"):
            await async_user_service._validate_username_unique(validation_data)

    @pytest.mark.asyncio
    async def test_validate_username_unique_with_exclude(self, async_user_service):
        """Test username uniqueness validation with exclude user ID."""
        validation_data = UserValidation(username="testuser")
        async_user_service.user_repo.is_username_taken.return_value = False

        # Should not raise exception
        await async_user_service._validate_username_unique(
            validation_data, exclude_user_id=1
        )
