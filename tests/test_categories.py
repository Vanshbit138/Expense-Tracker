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
        assert "Category name already exists" in response.json()["detail"]

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
        assert "Not enough permissions" in response.json()["detail"]
