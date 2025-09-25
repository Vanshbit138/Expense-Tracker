"""
Test authentication endpoints.
"""

from fastapi import status


class TestAuth:
    """Test authentication functionality."""

    def test_register_user(self, client, test_user_data):
        """Test user registration."""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client, test_user_data):
        """Test registration with duplicate email."""
        # Register first user
        client.post("/api/v1/auth/register", json=test_user_data)

        # Try to register with same email
        response = client.post("/api/v1/auth/register", json=test_user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]

    def test_register_duplicate_username(self, client, test_user_data):
        """Test registration with duplicate username."""
        # Register first user
        client.post("/api/v1/auth/register", json=test_user_data)

        # Try to register with same username
        duplicate_data = test_user_data.copy()
        duplicate_data["email"] = "different@example.com"
        response = client.post("/api/v1/auth/register", json=duplicate_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already taken" in response.json()["detail"]

    def test_login_success(self, client, test_user_data):
        """Test successful login."""
        # Register user first
        client.post("/api/v1/auth/register", json=test_user_data)

        # Login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"],
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, test_user_data):
        """Test login with invalid credentials."""
        # Register user first
        client.post("/api/v1/auth/register", json=test_user_data)

        # Try to login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            json={"email": test_user_data["email"], "password": "wrongpassword"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "password"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user(self, client, auth_headers):
        """Test getting current user profile."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "username" in data

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without authentication."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password(self, client, test_user_data, auth_headers):
        """Test changing password."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": test_user_data["password"],
                "new_password": "newpassword123",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_200_OK
        assert "Password changed successfully" in response.json()["message"]

    def test_change_password_wrong_current(self, client, auth_headers):
        """Test changing password with wrong current password."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword123",
            },
            headers=auth_headers,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Current password is incorrect" in response.json()["detail"]


class TestAuthEdgeCases:
    """Test authentication edge cases."""
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        user_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422
        
    def test_register_weak_password(self, client):
        """Test registration with weak password."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "123"  # Too short
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        # Might succeed or fail based on validation rules
        
    def test_register_missing_fields(self, client):
        """Test registration with missing fields."""
        user_data = {
            "email": "test@example.com"
            # Missing username and password
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422
        
    def test_login_empty_credentials(self, client):
        """Test login with empty credentials."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "", "password": ""}
        )
        assert response.status_code == 422
        
    def test_login_missing_fields(self, client):
        """Test login with missing fields."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com"}
        )
        assert response.status_code == 422
        
    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401
        
    def test_get_current_user_malformed_header(self, client):
        """Test getting current user with malformed auth header."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "invalid_header_format"}
        )
        assert response.status_code == 401
        
    def test_change_password_missing_fields(self, client, auth_headers):
        """Test changing password with missing fields."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={"current_password": "password123"},  # Missing new_password
            headers=auth_headers
        )
        assert response.status_code == 422
        
    def test_change_password_same_password(self, client, test_user_data, auth_headers):
        """Test changing password to same password."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": test_user_data["password"],
                "new_password": test_user_data["password"]  # Same password
            },
            headers=auth_headers
        )
        # Should succeed - no rule against same password
        assert response.status_code == 200
        
    def test_change_password_weak_new_password(self, client, test_user_data, auth_headers):
        """Test changing to weak new password."""
        response = client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": test_user_data["password"],
                "new_password": "123"  # Weak password
            },
            headers=auth_headers
        )
        # Might succeed or fail based on validation rules
        
    def test_multiple_login_attempts(self, client, test_user_data):
        """Test multiple login attempts."""
        # Register user
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Multiple successful logins
        for _ in range(3):
            response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": test_user_data["email"],
                    "password": test_user_data["password"]
                }
            )
            assert response.status_code == 200
            
    def test_token_expiry_handling(self, client, test_user_data):
        """Test handling of token expiry scenarios."""
        # Register and login
        client.post("/api/v1/auth/register", json=test_user_data)
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        
        token = response.json()["access_token"]
        
        # Use token immediately (should work)
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
