"""
Test expense endpoints.
"""

from fastapi import status
from decimal import Decimal, ROUND_HALF_UP


class TestExpenses:
    """Test expense functionality."""

    def test_create_expense(self, client, auth_headers, test_expense_data):
        """Test creating an expense."""
        # First create a category
        category_data = {
            "name": "Test Category",
            "description": "A test category",
            "color": "#FF0000",
        }
        category_response = client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers
        )
        assert category_response.status_code == status.HTTP_201_CREATED
        category_id = category_response.json()["id"]

        # Update expense data with category ID
        expense_data = test_expense_data.copy()
        expense_data["category_id"] = category_id

        # Create expense
        response = client.post(
            "/api/v1/expenses/", json=expense_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        # Compare amounts numerically with two decimal places
        api_amount = Decimal(str(data["amount"]))
        req_amount = Decimal(str(expense_data["amount"]))
        assert api_amount.quantize(Decimal("0.00"), rounding=ROUND_HALF_UP) == req_amount.quantize(
            Decimal("0.00"), rounding=ROUND_HALF_UP
        )
        assert data["currency"] == expense_data["currency"]
        assert data["description"] == expense_data["description"]
        assert "id" in data

    def test_create_expense_unauthorized(self, client, test_expense_data):
        """Test creating expense without authentication."""
        response = client.post("/api/v1/expenses/", json=test_expense_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_expenses(self, client, auth_headers):
        """Test getting user expenses."""
        response = client.get("/api/v1/expenses/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    def test_get_expense_by_id(self, client, auth_headers, test_expense_data):
        """Test getting expense by ID."""
        # Create a category first
        category_data = {
            "name": "Test Category",
            "description": "A test category",
            "color": "#FF0000",
        }
        category_response = client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers
        )
        category_id = category_response.json()["id"]

        # Create an expense
        expense_data = test_expense_data.copy()
        expense_data["category_id"] = category_id
        create_response = client.post(
            "/api/v1/expenses/", json=expense_data, headers=auth_headers
        )
        expense_id = create_response.json()["id"]

        # Get the expense
        response = client.get(f"/api/v1/expenses/{expense_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == expense_id

    def test_get_nonexistent_expense(self, client, auth_headers):
        """Test getting nonexistent expense."""
        response = client.get("/api/v1/expenses/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_expense(self, client, auth_headers, test_expense_data):
        """Test updating an expense."""
        # Create a category first
        category_data = {
            "name": "Test Category",
            "description": "A test category",
            "color": "#FF0000",
        }
        category_response = client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers
        )
        category_id = category_response.json()["id"]

        # Create an expense
        expense_data = test_expense_data.copy()
        expense_data["category_id"] = category_id
        create_response = client.post(
            "/api/v1/expenses/", json=expense_data, headers=auth_headers
        )
        expense_id = create_response.json()["id"]

        # Update the expense
        update_data = {"description": "Updated description", "amount": 200.00}
        response = client.put(
            f"/api/v1/expenses/{expense_id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated description"
        assert data["amount"] == "200.00"

    def test_delete_expense(self, client, auth_headers, test_expense_data):
        """Test deleting an expense."""
        # Create a category first
        category_data = {
            "name": "Test Category",
            "description": "A test category",
            "color": "#FF0000",
        }
        category_response = client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers
        )
        category_id = category_response.json()["id"]

        # Create an expense
        expense_data = test_expense_data.copy()
        expense_data["category_id"] = category_id
        create_response = client.post(
            "/api/v1/expenses/", json=expense_data, headers=auth_headers
        )
        expense_id = create_response.json()["id"]

        # Delete the expense
        response = client.delete(f"/api/v1/expenses/{expense_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert "deleted successfully" in response.json()["message"]

        # Verify expense is deleted
        get_response = client.get(
            f"/api/v1/expenses/{expense_id}", headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_monthly_expenses(self, client, auth_headers):
        """Test getting monthly expenses."""
        response = client.get("/api/v1/expenses/monthly/2024/1", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    def test_get_monthly_expenses_invalid_month(self, client, auth_headers):
        """Test getting monthly expenses with invalid month."""
        response = client.get("/api/v1/expenses/monthly/2024/13", headers=auth_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Month must be between 1 and 12" in response.json()["detail"]
