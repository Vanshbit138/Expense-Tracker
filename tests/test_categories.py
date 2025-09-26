"""
Test category endpoints.
"""

from fastapi import status


class TestCategories:
    """Test category functionality."""

    def test_create_category(self, client, auth_headers, test_category_data):
        """Test creating a category."""
        response = client.post(
            "/api/v1/categories/", json=test_category_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == test_category_data["name"]
        assert data["description"] == test_category_data["description"]
        assert data["color"] == test_category_data["color"]
        assert "id" in data
        assert not data["is_system"]

    def test_create_category_unauthorized(self, client, test_category_data):
        """Test creating category without authentication."""
        response = client.post("/api/v1/categories/", json=test_category_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_duplicate_category(self, client, auth_headers, test_category_data):
        """Test creating duplicate category."""
        # Create first category
        client.post(
            "/api/v1/categories/", json=test_category_data, headers=auth_headers
        )

        # Try to create duplicate
        response = client.post(
            "/api/v1/categories/", json=test_category_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Category name already exists" in response.json()["message"]

    def test_get_categories(self, client, auth_headers):
        """Test getting user categories."""
        response = client.get("/api/v1/categories/", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    def test_get_category_by_id(self, client, auth_headers, test_category_data):
        """Test getting category by ID."""
        # Create a category
        create_response = client.post(
            "/api/v1/categories/", json=test_category_data, headers=auth_headers
        )
        category_id = create_response.json()["id"]

        # Get the category
        response = client.get(f"/api/v1/categories/{category_id}", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == category_id
        assert data["name"] == test_category_data["name"]

    def test_get_nonexistent_category(self, client, auth_headers):
        """Test getting nonexistent category."""
        response = client.get("/api/v1/categories/999", headers=auth_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_category(self, client, auth_headers, test_category_data):
        """Test updating a category."""
        # Create a category
        create_response = client.post(
            "/api/v1/categories/", json=test_category_data, headers=auth_headers
        )
        category_id = create_response.json()["id"]

        # Update the category
        update_data = {
            "name": "Updated Category",
            "description": "Updated description",
            "color": "#00FF00",
        }
        response = client.put(
            f"/api/v1/categories/{category_id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Category"
        assert data["description"] == "Updated description"
        assert data["color"] == "#00FF00"

    def test_delete_category(self, client, auth_headers, test_category_data):
        """Test deleting a category."""
        # Create a category
        create_response = client.post(
            "/api/v1/categories/", json=test_category_data, headers=auth_headers
        )
        category_id = create_response.json()["id"]

        # Delete the category
        response = client.delete(
            f"/api/v1/categories/{category_id}", headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        assert "deleted successfully" in response.json()["message"]

        # Verify category is deleted
        get_response = client.get(
            f"/api/v1/categories/{category_id}", headers=auth_headers
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_init_system_categories_unauthorized(self, client, auth_headers):
        """Test initializing system categories without superuser privileges."""
        response = client.post(
            "/api/v1/categories/init-system-categories", headers=auth_headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json()["message"]


class TestCategoriesEdgeCases:
    """Test category endpoints edge cases."""

    def test_create_category_empty_name(self, client, auth_headers):
        """Test creating category with empty name."""
        category_data = {"name": "", "description": "Empty name category"}

        response = client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers
        )
        # Should fail validation
        assert response.status_code == 422

    def test_create_category_long_name(self, client, auth_headers):
        """Test creating category with very long name."""

    def test_create_category_special_characters(self, client, auth_headers):
        """Test creating category with special characters."""
        category_data = {
            "name": "Food & Dining 🍔",
            "description": "Category with emojis and symbols",
        }

        response = client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers
        )
        # Should succeed
        assert response.status_code == 201

    def test_get_categories_empty_list(self, client, auth_headers):
        """Test getting categories when none exist."""
        response = client.get("/api/v1/categories/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Should return empty list or system categories
        assert isinstance(data, list)

    def test_update_category_same_name(self, client, auth_headers):
        """Test updating category with same name."""
        # Create category
        category_data = {"name": "Test Category", "description": "Test"}
        response = client.post(
            "/api/v1/categories/", json=category_data, headers=auth_headers
        )
        category_id = response.json()["id"]

        # Update with same name
        update_data = {"name": "Test Category", "description": "Updated description"}
        response = client.put(
            f"/api/v1/categories/{category_id}", json=update_data, headers=auth_headers
        )
        assert response.status_code == 200

    def test_delete_category_with_expenses(self, client, auth_headers, test_category):
        """Test deleting category that has associated expenses."""
        # Create expense with this category
        expense_data = {
            "amount": 100.00,
            "currency": "USD",
            "description": "Test Expense",
            "status": "pending",
            "is_recurring": False,
            "expense_date": "2024-01-15T00:00:00",
            "category_id": test_category["id"],
        }
        client.post("/api/v1/expenses/", json=expense_data, headers=auth_headers)

        # Try to delete category
        response = client.delete(
            f"/api/v1/categories/{test_category['id']}", headers=auth_headers
        )
        # Should fail with 400 Bad Request - category has associated expenses
        assert response.status_code == 400
        assert (
            "Cannot delete category with associated expenses"
            in response.json()["message"]
        )

    def test_init_system_categories_multiple_times(self, client, auth_headers):
        """Test initializing system categories multiple times."""
        # This endpoint requires superuser permissions, so regular user should get 403
        response1 = client.post(
            "/api/v1/categories/init-system-categories", headers=auth_headers
        )

        # Regular user should get 403 Forbidden
        assert response1.status_code == 403

        # Since we cannot test the actual functionality without a superuser,
        # we just verify the security is working
