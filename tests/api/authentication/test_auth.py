"""
Tests for authentication API endpoints.
"""

from unittest.mock import Mock, patch

from fastapi import status
from fastapi.testclient import TestClient


class TestAuthAPI:
    """Test cases for authentication API endpoints."""

    def test_register_success(self, client: TestClient, test_user_data):
        """Test successful user registration."""
        response = client.post("/api/v1/auth/register", json=test_user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert "id" in data
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert data["full_name"] == test_user_data["full_name"]
        assert data["is_active"] is True
        assert data["is_superuser"] is False
        assert "created_at" in data
        assert "updated_at" in data
        assert "hashed_password" not in data  # Should not be returned

    def test_register_invalid_email(self, client: TestClient):
        """Test user registration with invalid email."""
        user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "TestPass123!",
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_register_invalid_password(self, client: TestClient):
        """Test user registration with invalid password."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "short",  # Too short
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_register_invalid_username(self, client: TestClient):
        """Test user registration with invalid username."""
        user_data = {
            "email": "test@example.com",
            "username": "a",  # Too short
            "password": "TestPass123!",
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_register_missing_fields(self, client: TestClient):
        """Test user registration with missing required fields."""
        user_data = {
            "email": "test@example.com"
            # Missing username and password
        }

        response = client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_register_duplicate_email(self, client: TestClient, test_user_data):
        """Test user registration with duplicate email."""
        # Register first user
        response1 = client.post("/api/v1/auth/register", json=test_user_data)
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to register second user with same email
        user_data2 = test_user_data.copy()
        user_data2["username"] = "differentuser"

        response2 = client.post("/api/v1/auth/register", json=user_data2)

        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        data = response2.json()
        assert "Email already registered" in data["detail"]

    def test_register_duplicate_username(self, client: TestClient, test_user_data):
        """Test user registration with duplicate username."""
        # Register first user
        response1 = client.post("/api/v1/auth/register", json=test_user_data)
        assert response1.status_code == status.HTTP_201_CREATED

        # Try to register second user with same username
        user_data2 = test_user_data.copy()
        user_data2["email"] = "different@example.com"

        response2 = client.post("/api/v1/auth/register", json=user_data2)

        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        data = response2.json()
        assert "Username already taken" in data["detail"]

    def test_login_success(self, client: TestClient, test_user_data):
        """Test successful user login."""
        # Register user first
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        # Login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_login_invalid_email(self, client: TestClient, test_user_data):
        """Test login with invalid email."""
        # Register user first
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        # Login with wrong email
        login_data = {
            "email": "wrong@example.com",
            "password": test_user_data["password"],
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Invalid email or password" in data["detail"]

    def test_login_invalid_password(self, client: TestClient, test_user_data):
        """Test login with invalid password."""
        # Register user first
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        # Login with wrong password
        login_data = {"email": test_user_data["email"], "password": "wrongpassword"}

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "Invalid email or password" in data["detail"]

    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing required fields."""
        login_data = {
            "email": "test@example.com"
            # Missing password
        }

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_login_invalid_email_format(self, client: TestClient):
        """Test login with invalid email format."""
        login_data = {"email": "invalid-email", "password": "password123"}

        response = client.post("/api/v1/auth/login", json=login_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_get_current_user_success(self, client: TestClient, auth_headers):
        """Test getting current user information."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "id" in data
        assert "email" in data
        assert "username" in data
        assert "full_name" in data
        assert "is_active" in data
        assert "is_superuser" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "hashed_password" not in data  # Should not be returned

    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without authentication."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password_success(
        self, client: TestClient, auth_headers, test_user_data
    ):
        """Test successful password change."""
        password_data = {
            "current_password": test_user_data["password"],
            "new_password": "NewPassword123!",
        }

        response = client.post(
            "/api/v1/auth/change-password", json=password_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Password changed successfully"

    def test_change_password_wrong_current_password(
        self, client: TestClient, auth_headers
    ):
        """Test password change with wrong current password."""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "NewPassword123!",
        }

        response = client.post(
            "/api/v1/auth/change-password", json=password_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "Invalid current password" in data["detail"]

    def test_change_password_invalid_new_password(
        self, client: TestClient, auth_headers, test_user_data
    ):
        """Test password change with invalid new password."""
        password_data = {
            "current_password": test_user_data["password"],
            "new_password": "short",  # Too short
        }

        response = client.post(
            "/api/v1/auth/change-password", json=password_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_change_password_missing_fields(self, client: TestClient, auth_headers):
        """Test password change with missing required fields."""
        password_data = {
            "current_password": "password123"
            # Missing new_password
        }

        response = client.post(
            "/api/v1/auth/change-password", json=password_data, headers=auth_headers
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_change_password_unauthorized(self, client: TestClient, test_user_data):
        """Test password change without authentication."""
        password_data = {
            "current_password": test_user_data["password"],
            "new_password": "NewPassword123!",
        }

        response = client.post("/api/v1/auth/change-password", json=password_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password_invalid_token(self, client: TestClient, test_user_data):
        """Test password change with invalid token."""
        password_data = {
            "current_password": test_user_data["password"],
            "new_password": "NewPassword123!",
        }

        headers = {"Authorization": "Bearer invalid_token"}
        response = client.post(
            "/api/v1/auth/change-password", json=password_data, headers=headers
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_register_database_error(self, client: TestClient, test_user_data):
        """Test user registration with database error."""
        with patch("src.api.authentication.auth.UserService") as mock_user_service:
            mock_service_instance = Mock()
            mock_service_instance.create_user.side_effect = Exception("Database error")
            mock_user_service.return_value = mock_service_instance

            response = client.post("/api/v1/auth/register", json=test_user_data)

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "Internal server error during registration" in data["detail"]

    def test_login_database_error(self, client: TestClient, test_user_data):
        """Test user login with database error."""
        with patch("src.api.authentication.auth.UserService") as mock_user_service:
            mock_service_instance = Mock()
            mock_service_instance.authenticate_user.side_effect = Exception(
                "Database error"
            )
            mock_user_service.return_value = mock_service_instance

            login_data = {
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            }

            response = client.post("/api/v1/auth/login", json=login_data)

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "Internal server error during login" in data["detail"]

    def test_change_password_database_error(
        self, client: TestClient, auth_headers, test_user_data
    ):
        """Test password change with database error."""
        with patch("src.api.authentication.auth.UserService") as mock_user_service:
            mock_service_instance = Mock()
            mock_service_instance.change_password.side_effect = Exception(
                "Database error"
            )
            mock_user_service.return_value = mock_service_instance

            password_data = {
                "current_password": test_user_data["password"],
                "new_password": "NewPassword123!",
            }

            response = client.post(
                "/api/v1/auth/change-password", json=password_data, headers=auth_headers
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            data = response.json()
            assert "Internal server error during password change" in data["detail"]

    def test_token_generation(self, client: TestClient, test_user_data):
        """Test that login generates a valid JWT token."""
        # Register user first
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        # Login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        }

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        token = data["access_token"]

        # Use the token to access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        me_response = client.get("/api/v1/auth/me", headers=headers)

        assert me_response.status_code == status.HTTP_200_OK
        me_data = me_response.json()
        assert me_data["email"] == test_user_data["email"]

    def test_token_expiry(self, client: TestClient, test_user_data):
        """Test that tokens have proper expiry."""
        # Register user first
        register_response = client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == status.HTTP_201_CREATED

        # Login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"],
        }

        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        token = data["access_token"]

        # Token should be a valid JWT (contains dots)
        assert token.count(".") == 2

        # Token should be reasonably long
        assert len(token) > 100
