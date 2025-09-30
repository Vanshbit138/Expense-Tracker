"""
Unit tests for API endpoints.
"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

from fastapi import HTTPException, status

from src.models.category.category import Category
from src.models.expense.expense import Expense
from src.models.user.user import User


class TestAuthEndpoints:
    """Test cases for authentication endpoints."""

    def test_register_user_success(self, client, sample_user_data):
        """Test successful user registration."""
        with patch("src.api.authentication.auth.UserService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            mock_user = User(
                id=1,
                email=sample_user_data["email"],
                username=sample_user_data["username"],
                full_name=sample_user_data["full_name"],
                hashed_password="hashed_password",
                is_active=True,
                is_superuser=False,
            )
            mock_service.create_user.return_value = mock_user

            response = client.post("/api/v1/auth/register", json=sample_user_data)

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["email"] == sample_user_data["email"]
            assert data["username"] == sample_user_data["username"]
            assert "id" in data

    def test_register_user_validation_error(self, client):
        """Test user registration with validation error."""
        invalid_data = {
            "email": "invalid-email",  # Invalid email format
            "username": "testuser",
            "password": "123",  # Too short password
        }

        response = client.post("/api/v1/auth/register", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_user_email_already_exists(self, client, sample_user_data):
        """Test user registration with existing email."""
        with patch("src.api.authentication.auth.UserService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.create_user.side_effect = HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

            response = client.post("/api/v1/auth/register", json=sample_user_data)

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert "Email already registered" in data["detail"]

    def test_login_success(self, client, sample_user_data):
        """Test successful user login."""
        with patch("src.api.authentication.auth.UserService") as mock_service_class:
            with patch(
                "src.api.authentication.auth.create_access_token"
            ) as mock_create_token:
                mock_service = MagicMock()
                mock_service_class.return_value = mock_service

                mock_user = User(
                    id=1,
                    email=sample_user_data["email"],
                    username=sample_user_data["username"],
                    hashed_password="hashed_password",
                )
                mock_service.authenticate_user.return_value = mock_user
                mock_create_token.return_value = "test_token"

                login_data = {
                    "email": sample_user_data["email"],
                    "password": sample_user_data["password"],
                }

                response = client.post("/api/v1/auth/login", json=login_data)

                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert "access_token" in data
                assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        with patch("src.api.authentication.auth.UserService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.authenticate_user.side_effect = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

            login_data = {"email": "test@example.com", "password": "wrong_password"}

            response = client.post("/api/v1/auth/login", json=login_data)

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert "Invalid email or password" in data["detail"]

    def test_get_current_user_success(self, client, auth_headers, sample_user):
        """Test getting current user with valid token."""
        with patch("src.api.authentication.auth.get_current_user") as mock_get_user:
            mock_get_user.return_value = sample_user

            response = client.get("/api/v1/auth/me", headers=auth_headers)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["email"] == sample_user.email
            assert data["username"] == sample_user.username

    def test_get_current_user_unauthorized(self, client):
        """Test getting current user without token."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}

        with patch("src.api.authentication.auth.get_current_user") as mock_get_user:
            mock_get_user.side_effect = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

            response = client.get("/api/v1/auth/me", headers=headers)

            assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCategoryEndpoints:
    """Test cases for category endpoints."""

    def test_create_category_success(self, client, auth_headers, sample_category_data):
        """Test successful category creation."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            mock_category = Category(
                id=1,
                name=sample_category_data["name"],
                description=sample_category_data["description"],
                user_id=1,
                is_system=False,
            )
            mock_service.create_category.return_value = mock_category

            response = client.post(
                "/api/v1/categories/", json=sample_category_data, headers=auth_headers
            )

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["name"] == sample_category_data["name"]
            assert data["description"] == sample_category_data["description"]

    def test_create_category_unauthorized(self, client, sample_category_data):
        """Test category creation without authentication."""
        response = client.post("/api/v1/categories/", json=sample_category_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_categories_success(self, client, auth_headers):
        """Test successful categories retrieval."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            mock_categories = [
                Category(id=1, name="Food", user_id=1),
                Category(id=2, name="Transport", user_id=1),
            ]
            mock_service.get_user_categories.return_value = mock_categories

            response = client.get("/api/v1/categories/", headers=auth_headers)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            assert data[0]["name"] == "Food"
            assert data[1]["name"] == "Transport"

    def test_get_category_by_id_success(self, client, auth_headers):
        """Test successful category retrieval by ID."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            mock_category = Category(id=1, name="Food", user_id=1)
            mock_service.get_category_by_id.return_value = mock_category

            response = client.get("/api/v1/categories/1", headers=auth_headers)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["name"] == "Food"

    def test_get_category_by_id_not_found(self, client, auth_headers):
        """Test category retrieval by ID when not found."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.get_category_by_id.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

            response = client.get("/api/v1/categories/999", headers=auth_headers)

            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_category_success(self, client, auth_headers):
        """Test successful category update."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            mock_category = Category(id=1, name="Updated Food", user_id=1)
            mock_service.update_category.return_value = mock_category

            update_data = {"name": "Updated Food", "description": "Updated description"}

            response = client.put(
                "/api/v1/categories/1", json=update_data, headers=auth_headers
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["name"] == "Updated Food"

    def test_delete_category_success(self, client, auth_headers):
        """Test successful category deletion."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.delete_category.return_value = True

            response = client.delete("/api/v1/categories/1", headers=auth_headers)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["message"] == "Category deleted successfully"

    def test_delete_category_not_found(self, client, auth_headers):
        """Test category deletion when not found."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.delete_category.return_value = False

            response = client.delete("/api/v1/categories/999", headers=auth_headers)

            assert response.status_code == status.HTTP_404_NOT_FOUND


class TestExpenseEndpoints:
    """Test cases for expense endpoints."""

    def test_create_expense_success(self, client, auth_headers, sample_expense_data):
        """Test successful expense creation."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            mock_expense = Expense(
                id=1,
                amount=sample_expense_data["amount"],
                currency=sample_expense_data["currency"],
                description=sample_expense_data["description"],
                status=sample_expense_data["status"],
                is_recurring=sample_expense_data["is_recurring"],
                recurring_frequency=sample_expense_data["recurring_frequency"],
                expense_date=sample_expense_data["expense_date"],
                user_id=1,
                category_id=1,
            )
            mock_service.create_expense.return_value = mock_expense

            response = client.post(
                "/api/v1/expenses/", json=sample_expense_data, headers=auth_headers
            )

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["amount"] == float(sample_expense_data["amount"])
            assert data["currency"] == sample_expense_data["currency"]

    def test_create_expense_unauthorized(self, client, sample_expense_data):
        """Test expense creation without authentication."""
        response = client.post("/api/v1/expenses/", json=sample_expense_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_expenses_success(self, client, auth_headers):
        """Test successful expenses retrieval."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            mock_expenses = [
                Expense(id=1, amount=Decimal("50.00"), user_id=1, category_id=1),
                Expense(id=2, amount=Decimal("75.00"), user_id=1, category_id=2),
            ]
            mock_service.get_user_expenses.return_value = mock_expenses

            response = client.get("/api/v1/expenses/", headers=auth_headers)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            assert data[0]["amount"] == 50.0
            assert data[1]["amount"] == 75.0

    def test_get_expenses_with_filters(self, client, auth_headers):
        """Test expenses retrieval with query parameters."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            mock_expenses = [
                Expense(id=1, amount=Decimal("50.00"), user_id=1, category_id=1)
            ]
            mock_service.get_user_expenses.return_value = mock_expenses

            response = client.get(
                "/api/v1/expenses/?skip=0&limit=10&start_date=2023-01-01&end_date=2023-12-31",
                headers=auth_headers,
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 1

    def test_get_expense_by_id_success(self, client, auth_headers):
        """Test successful expense retrieval by ID."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            mock_expense = Expense(
                id=1, amount=Decimal("100.00"), user_id=1, category_id=1
            )
            mock_service.get_expense_by_id.return_value = mock_expense

            response = client.get("/api/v1/expenses/1", headers=auth_headers)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["amount"] == 100.0

    def test_get_expense_by_id_not_found(self, client, auth_headers):
        """Test expense retrieval by ID when not found."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.get_expense_by_id.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
            )

            response = client.get("/api/v1/expenses/999", headers=auth_headers)

            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_expense_success(self, client, auth_headers):
        """Test successful expense update."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            mock_expense = Expense(
                id=1, amount=Decimal("150.00"), user_id=1, category_id=1
            )
            mock_service.update_expense.return_value = mock_expense

            update_data = {"amount": 150.0, "description": "Updated expense"}

            response = client.put(
                "/api/v1/expenses/1", json=update_data, headers=auth_headers
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["amount"] == 150.0

    def test_delete_expense_success(self, client, auth_headers):
        """Test successful expense deletion."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.delete_expense.return_value = True

            response = client.delete("/api/v1/expenses/1", headers=auth_headers)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["message"] == "Expense deleted successfully"

    def test_delete_expense_not_found(self, client, auth_headers):
        """Test expense deletion when not found."""
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.delete_expense.return_value = False

            response = client.delete("/api/v1/expenses/999", headers=auth_headers)

            assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAnalyticsEndpoints:
    """Test cases for analytics endpoints."""

    def test_get_expense_summary_success(self, client, auth_headers):
        """Test successful expense summary retrieval."""
        with patch("src.api.user.analytics.UserService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            mock_summary = {
                "total_expenses": 1000.0,
                "total_categories": 5,
                "average_expense": 200.0,
                "monthly_trend": [100.0, 150.0, 200.0],
            }
            mock_service.get_expense_summary.return_value = mock_summary

            response = client.get("/api/v1/analytics/summary", headers=auth_headers)

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["total_expenses"] == 1000.0
            assert data["total_categories"] == 5

    def test_get_expense_summary_unauthorized(self, client):
        """Test expense summary retrieval without authentication."""
        response = client.get("/api/v1/analytics/summary")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_category_breakdown_success(self, client, auth_headers):
        """Test successful category breakdown retrieval."""
        with patch("src.api.user.analytics.UserService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            mock_breakdown = [
                {"category": "Food", "total": 500.0, "count": 10},
                {"category": "Transport", "total": 300.0, "count": 5},
            ]
            mock_service.get_category_breakdown.return_value = mock_breakdown

            response = client.get(
                "/api/v1/analytics/category-breakdown", headers=auth_headers
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            assert data[0]["category"] == "Food"
            assert data[0]["total"] == 500.0

    def test_get_monthly_trends_success(self, client, auth_headers):
        """Test successful monthly trends retrieval."""
        with patch("src.api.user.analytics.UserService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            mock_trends = [
                {"month": "2023-01", "total": 1000.0, "count": 20},
                {"month": "2023-02", "total": 1200.0, "count": 25},
            ]
            mock_service.get_monthly_trends.return_value = mock_trends

            response = client.get(
                "/api/v1/analytics/monthly-trends", headers=auth_headers
            )

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 2
            assert data[0]["month"] == "2023-01"
            assert data[0]["total"] == 1000.0


class TestAPIErrorHandling:
    """Test cases for API error handling."""

    def test_validation_error_handling(self, client):
        """Test validation error handling."""
        invalid_data = {
            "email": "invalid-email",
            "username": "a",  # Too short
            "password": "123",  # Too short
        }

        response = client.post("/api/v1/auth/register", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data

    def test_internal_server_error_handling(self, client, auth_headers):
        """Test internal server error handling."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.create_category.side_effect = Exception(
                "Database connection failed"
            )

            category_data = {"name": "Test Category", "description": "Test description"}

            response = client.post(
                "/api/v1/categories/", json=category_data, headers=auth_headers
            )

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_not_found_error_handling(self, client, auth_headers):
        """Test not found error handling."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.get_category_by_id.side_effect = HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
            )

            response = client.get("/api/v1/categories/999", headers=auth_headers)

            assert response.status_code == status.HTTP_404_NOT_FOUND
            data = response.json()
            assert "Category not found" in data["detail"]

    def test_forbidden_error_handling(self, client, auth_headers):
        """Test forbidden error handling."""
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.get_category_by_id.side_effect = HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to category",
            )

            response = client.get("/api/v1/categories/1", headers=auth_headers)

            assert response.status_code == status.HTTP_403_FORBIDDEN
            data = response.json()
            assert "Access denied to category" in data["detail"]


class TestAPIIntegration:
    """Integration tests for API endpoints."""

    def test_complete_user_workflow(self, client):
        """Test complete user workflow: register, login, get profile."""
        # Register user
        user_data = {
            "email": "integration@example.com",
            "username": "integration",
            "full_name": "Integration User",
            "password": "password123",
        }

        with patch("src.api.authentication.auth.UserService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            mock_user = User(
                id=1,
                email=user_data["email"],
                username=user_data["username"],
                full_name=user_data["full_name"],
                hashed_password="hashed_password",
            )
            mock_service.create_user.return_value = mock_user

            response = client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code == status.HTTP_201_CREATED

        # Login user
        login_data = {"email": user_data["email"], "password": user_data["password"]}

        with patch("src.api.authentication.auth.UserService") as mock_service_class:
            with patch(
                "src.api.authentication.auth.create_access_token"
            ) as mock_create_token:
                mock_service = MagicMock()
                mock_service_class.return_value = mock_service
                mock_service.authenticate_user.return_value = mock_user
                mock_create_token.return_value = "test_token"

                response = client.post("/api/v1/auth/login", json=login_data)
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                token = data["access_token"]

        # Get user profile
        headers = {"Authorization": f"Bearer {token}"}

        with patch("src.api.authentication.auth.get_current_user") as mock_get_user:
            mock_get_user.return_value = mock_user

            response = client.get("/api/v1/auth/me", headers=headers)
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["email"] == user_data["email"]

    def test_complete_category_workflow(self, client, auth_headers):
        """Test complete category workflow: create, read, update, delete."""
        # Create category
        category_data = {
            "name": "Integration Category",
            "description": "Category for integration testing",
        }

        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            mock_category = Category(
                id=1,
                name=category_data["name"],
                description=category_data["description"],
                user_id=1,
            )
            mock_service.create_category.return_value = mock_category

            response = client.post(
                "/api/v1/categories/", json=category_data, headers=auth_headers
            )
            assert response.status_code == status.HTTP_201_CREATED

        # Get category
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.get_category_by_id.return_value = mock_category

            response = client.get("/api/v1/categories/1", headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK

        # Update category
        update_data = {"description": "Updated description"}

        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.update_category.return_value = mock_category

            response = client.put(
                "/api/v1/categories/1", json=update_data, headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK

        # Delete category
        with patch("src.api.category.categories.CategoryService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.delete_category.return_value = True

            response = client.delete("/api/v1/categories/1", headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK

    def test_complete_expense_workflow(self, client, auth_headers):
        """Test complete expense workflow: create, read, update, delete."""
        # Create expense
        expense_data = {
            "amount": 100.0,
            "currency": "USD",
            "description": "Integration test expense",
            "status": "pending",
            "is_recurring": False,
            "recurring_frequency": None,
            "expense_date": "2023-01-01T00:00:00",
            "category_id": 1,
        }

        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service

            mock_expense = Expense(
                id=1,
                amount=Decimal("100.00"),
                currency="USD",
                description="Integration test expense",
                status="pending",
                is_recurring=False,
                recurring_frequency=None,
                expense_date=datetime(2023, 1, 1),
                user_id=1,
                category_id=1,
            )
            mock_service.create_expense.return_value = mock_expense

            response = client.post(
                "/api/v1/expenses/", json=expense_data, headers=auth_headers
            )
            assert response.status_code == status.HTTP_201_CREATED

        # Get expense
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.get_expense_by_id.return_value = mock_expense

            response = client.get("/api/v1/expenses/1", headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK

        # Update expense
        update_data = {"description": "Updated expense"}

        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.update_expense.return_value = mock_expense

            response = client.put(
                "/api/v1/expenses/1", json=update_data, headers=auth_headers
            )
            assert response.status_code == status.HTTP_200_OK

        # Delete expense
        with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
            mock_service = MagicMock()
            mock_service_class.return_value = mock_service
            mock_service.delete_expense.return_value = True

            response = client.delete("/api/v1/expenses/1", headers=auth_headers)
            assert response.status_code == status.HTTP_200_OK
