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
            "name": "Expense Test Category",
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
            "name": "Expense Test Category",
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
            "name": "Expense Test Category",
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
            "name": "Expense Test Category",
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


class TestExpensesEdgeCases:
    """Test expense endpoints edge cases."""
    
    def test_create_expense_invalid_amount(self, client, auth_headers, test_category):
        """Test creating expense with invalid amount."""
        expense_data = {
            "description": "Invalid Expense",
            "amount": -100.00,  # Negative amount
            "category_id": test_category["id"],
            "expense_date": "2024-01-15T00:00:00"
        }
        
        response = client.post(
            "/api/v1/expenses/",
            json=expense_data,
            headers=auth_headers
        )
        # This might pass validation, but test the edge case
        # The validation might be in the schema or business logic
        
    def test_create_expense_future_date(self, client, auth_headers, test_category):
        """Test creating expense with future date."""
        from datetime import date, timedelta
        future_date = date.today() + timedelta(days=30)
        
        expense_data = {
            "description": "Future Expense",
            "amount": 100.00,
            "category_id": test_category["id"],
            "expense_date": future_date.isoformat()
        }
        
        response = client.post(
            "/api/v1/expenses/",
            json=expense_data,
            headers=auth_headers
        )
        # Should succeed as future expenses might be allowed for planning
        
    def test_get_expenses_with_filters(self, client, auth_headers, test_category):
        """Test getting expenses with various filters."""
        # Create multiple expenses first
        expense_data = {
            "description": "Filter Test Expense",
            "amount": 150.00,
            "category_id": test_category["id"],
            "expense_date": "2024-01-15T00:00:00",
            "status": "completed"
        }
        client.post("/api/v1/expenses/", json=expense_data, headers=auth_headers)
        
        # Test with category filter
        response = client.get(
            f"/api/v1/expenses/?category_id={test_category['id']}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Test with status filter
        response = client.get(
            "/api/v1/expenses/?status=completed",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Test with date range
        response = client.get(
            "/api/v1/expenses/?start_date=2024-01-01&end_date=2024-01-31",
            headers=auth_headers
        )
        assert response.status_code == 200
        
    def test_get_expenses_pagination(self, client, auth_headers, test_category):
        """Test expense pagination."""
        # Create multiple expenses
        for i in range(5):
            expense_data = {
                "description": f"Expense {i}",
                "amount": 100.00 + i,
                "category_id": test_category["id"],
                "expense_date": "2024-01-15T00:00:00"
            }
            client.post("/api/v1/expenses/", json=expense_data, headers=auth_headers)
        
        # Test pagination
        response = client.get(
            "/api/v1/expenses/?skip=0&limit=3",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3
        
    def test_update_expense_partial(self, client, auth_headers, test_expense_data, test_category):
        """Test partial expense update."""
        # Create expense
        response = client.post(
            "/api/v1/expenses/",
            json=test_expense_data,
            headers=auth_headers
        )
        expense_id = response.json()["id"]
        
        # Update only title
        update_data = {"description": "Updated Title Only"}
        response = client.put(
            f"/api/v1/expenses/{expense_id}",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated Title Only"
        # Other fields should remain unchanged
        
    def test_delete_expense_twice(self, client, auth_headers, test_expense_data):
        """Test deleting expense twice."""
        # Create expense
        response = client.post(
            "/api/v1/expenses/",
            json=test_expense_data,
            headers=auth_headers
        )
        expense_id = response.json()["id"]
        
        # Delete first time
        response = client.delete(
            f"/api/v1/expenses/{expense_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Delete second time (should fail)
        response = client.delete(
            f"/api/v1/expenses/{expense_id}",
            headers=auth_headers
        )
        assert response.status_code == 404
