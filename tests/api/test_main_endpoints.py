"""
Tests for main API endpoints.
"""

from fastapi import status
from fastapi.testclient import TestClient


class TestMainEndpoints:
    """Test cases for main API endpoints."""

    def test_health_endpoint(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "Expense Tracker API" in data["message"]

    def test_docs_endpoint(self, client: TestClient):
        """Test API documentation endpoint."""
        response = client.get("/api/v1/docs")

        assert response.status_code == status.HTTP_200_OK
        # Should return HTML content
        assert "text/html" in response.headers["content-type"]

    def test_redoc_endpoint(self, client: TestClient):
        """Test ReDoc documentation endpoint."""
        response = client.get("/api/v1/redoc")

        assert response.status_code == status.HTTP_200_OK
        # Should return HTML content
        assert "text/html" in response.headers["content-type"]

    def test_openapi_endpoint(self, client: TestClient):
        """Test OpenAPI schema endpoint."""
        response = client.get("/api/v1/openapi.json")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Should be valid OpenAPI schema
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        assert data["info"]["title"] == "Expense Tracker API"
        assert data["info"]["version"] == "1.0.0"
