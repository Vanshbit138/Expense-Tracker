"""
Test analytics endpoints.
"""

from fastapi import status


class TestAnalytics:
    """Test analytics functionality."""

    def test_get_expense_stats(self, client, auth_headers):
        """Test getting expense statistics."""
        response = client.get("/api/v1/analytics/stats", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_amount" in data
        assert "total_count" in data
        assert "average_amount" in data
        assert "currency" in data

    def test_get_category_stats(self, client, auth_headers):
        """Test getting category statistics."""
        response = client.get("/api/v1/analytics/category-stats", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    def test_get_monthly_analytics(self, client, auth_headers):
        """Test getting monthly analytics."""
        response = client.get("/api/v1/analytics/monthly/2024/1", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_amount" in data
        assert "total_count" in data
        assert "average_amount" in data
        assert "currency" in data
        assert "top_categories" in data
        assert "recurring_count" in data

    def test_get_monthly_analytics_invalid_month(self, client, auth_headers):
        """Test getting monthly analytics with invalid month."""
        response = client.get("/api/v1/analytics/monthly/2024/13", headers=auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Month must be between 1 and 12" in response.json()["detail"]

    def test_analytics_unauthorized(self, client):
        """Test analytics endpoints without authentication."""
        endpoints = [
            "/api/v1/analytics/stats",
            "/api/v1/analytics/category-stats",
            "/api/v1/analytics/monthly/2024/1",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
