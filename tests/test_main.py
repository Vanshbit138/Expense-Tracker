"""
Test main application endpoints and startup.
"""

from fastapi import status


class TestMainApp:
    """Test main application functionality."""

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs_url" in data
        assert data["message"] == "Welcome to Expense Tracker API"

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["status"] == "healthy"

    def test_openapi_docs_available(self, client):
        """Test that OpenAPI docs are available."""
        response = client.get("/api/v1/docs")
        assert response.status_code == status.HTTP_200_OK

    def test_redoc_available(self, client):
        """Test that ReDoc is available."""
        response = client.get("/api/v1/redoc")
        assert response.status_code == status.HTTP_200_OK

    def test_openapi_json_available(self, client):
        """Test that OpenAPI JSON is available."""
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
