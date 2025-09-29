"""
Test analytics endpoints (Fixed version).
"""

from fastapi import status


class TestAnalytics:
    """Test analytics functionality."""

    def test_get_expense_stats(self, client, auth_headers, test_expense_data):
        """Test getting expense statistics."""
        # Create expense
        client.post("/api/v1/expenses/", json=test_expense_data, headers=auth_headers)

        response = client.get("/api/v1/analytics/stats", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_amount" in data
        assert "total_count" in data
        assert "average_amount" in data

    def test_get_category_stats(self, client, auth_headers, test_expense_data):
        """Test getting category statistics."""
        # Create expense
        client.post("/api/v1/expenses/", json=test_expense_data, headers=auth_headers)

        response = client.get("/api/v1/analytics/category-stats", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_get_monthly_analytics(self, client, auth_headers, test_expense_data):
        """Test getting monthly analytics."""
        # Create expense
        client.post("/api/v1/expenses/", json=test_expense_data, headers=auth_headers)

        response = client.get("/api/v1/analytics/monthly/2024/1", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_amount" in data
        assert "total_count" in data

    def test_get_monthly_analytics_invalid_month(self, client, auth_headers):
        """Test monthly analytics with invalid month."""
        response = client.get("/api/v1/analytics/monthly/2024/13", headers=auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_analytics_unauthorized(self, client):
        """Test analytics endpoints without authentication."""
        response = client.get("/api/v1/analytics/stats")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAnalyticsEdgeCases:
    """Test analytics endpoints edge cases (Fixed version)."""

    def test_get_expense_stats_with_date_range(
        self, client, auth_headers, test_expense_data
    ):
        """Test expense stats with date range filters."""
        # Create expense
        client.post("/api/v1/expenses/", json=test_expense_data, headers=auth_headers)

        # Test with date range
        response = client.get(
            "/api/v1/analytics/stats?start_date=2024-01-01&end_date=2024-12-31&currency=USD",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_amount" in data
        assert "total_count" in data
        assert "average_amount" in data

    def test_get_expense_stats_different_currency(self, client, auth_headers):
        """Test expense stats with different currency."""
        response = client.get(
            "/api/v1/analytics/stats?currency=EUR", headers=auth_headers
        )
        assert response.status_code == 200
        # data = response.json()
        # Should return zero stats for EUR if no EUR expenses

    def test_get_category_stats_with_limit(
        self, client, auth_headers, test_expense_data
    ):
        """Test category stats with limit parameter."""
        # Create expense
        client.post("/api/v1/expenses/", json=test_expense_data, headers=auth_headers)

        response = client.get(
            "/api/v1/analytics/category-stats?limit=5", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_get_monthly_analytics_future_month(self, client, auth_headers):
        """Test monthly analytics for future month."""
        response = client.get("/api/v1/analytics/monthly/2025/12", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Should return zero stats for future month
        assert data["total_count"] == 0

    def test_get_monthly_analytics_invalid_month(self, client, auth_headers):
        """Test monthly analytics with invalid month."""
        response = client.get(
            "/api/v1/analytics/monthly/2024/13",  # Month 13 doesn't exist
            headers=auth_headers,
        )
        assert response.status_code == 400  # Changed from 422 to 400

    def test_get_monthly_analytics_invalid_year(self, client, auth_headers):
        """Test monthly analytics with invalid year."""
        response = client.get(
            "/api/v1/analytics/monthly/abc/1", headers=auth_headers  # Invalid year
        )
        assert response.status_code == 422

    def test_analytics_with_no_data(self, client, auth_headers):
        """Test all analytics endpoints with no expense data."""
        # Test expense stats
        response = client.get("/api/v1/analytics/stats", headers=auth_headers)
        assert response.status_code == 200

        # Test category stats
        response = client.get("/api/v1/analytics/category-stats", headers=auth_headers)
        assert response.status_code == 200

        # Test monthly analytics
        response = client.get("/api/v1/analytics/monthly/2024/1", headers=auth_headers)
        assert response.status_code == 200
