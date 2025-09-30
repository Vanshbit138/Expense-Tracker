"""
Integration tests for Expense Tracker API.
"""

from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

from fastapi import HTTPException

from src.models.category.category import Category
from src.models.expense.expense import Expense
from src.models.user.user import User
from src.services.authentication.password_service import get_password_hash


class TestUserWorkflowIntegration:
    """Integration tests for complete user workflows."""

    def test_user_registration_and_authentication_flow(self, client, db_session):
        """Test complete user registration and authentication flow."""
        # Register new user
        user_data = {
            "email": "integration@example.com",
            "username": "integration_user",
            "full_name": "Integration Test User",
            "password": "secure_password123",
        }

        with patch("src.api.authentication.auth.UserService") as mock_service_class:
            mock_service = mock_service_class.return_value

            # Mock user creation
            created_user = User(
                id=1,
                email=user_data["email"],
                username=user_data["username"],
                full_name=user_data["full_name"],
                hashed_password=get_password_hash(user_data["password"]),
                is_active=True,
                is_superuser=False,
            )
            mock_service.create_user.return_value = created_user

            response = client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code == 201
            data = response.json()
            assert data["email"] == user_data["email"]
            assert data["username"] == user_data["username"]

        # Login user
        login_data = {"email": user_data["email"], "password": user_data["password"]}

        with patch("src.api.authentication.auth.UserService") as mock_service_class:
            with patch(
                "src.api.authentication.auth.create_access_token"
            ) as mock_create_token:
                mock_service = mock_service_class.return_value
                mock_service.authenticate_user.return_value = created_user
                mock_create_token.return_value = "test_access_token"

                response = client.post("/api/v1/auth/login", json=login_data)
                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert data["token_type"] == "bearer"

    def test_user_profile_management_flow(self, client, sample_user):
        """Test user profile management workflow."""
        # Mock authentication
        auth_headers = {"Authorization": "Bearer test_token"}

        with patch("src.api.authentication.auth.get_current_user") as mock_get_user:
            mock_get_user.return_value = sample_user

            # Get user profile
            response = client.get("/api/v1/auth/me", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == sample_user.email
            assert data["username"] == sample_user.username

            # Update user profile
            update_data = {
                "full_name": "Updated Full Name",
                "email": "updated@example.com",
            }

            with patch("src.api.authentication.auth.UserService") as mock_service_class:
                mock_service = mock_service_class.return_value
                updated_user = User(
                    id=sample_user.id,
                    email=update_data["email"],
                    username=sample_user.username,
                    full_name=update_data["full_name"],
                    hashed_password=sample_user.hashed_password,
                    is_active=sample_user.is_active,
                    is_superuser=sample_user.is_superuser,
                )
                mock_service.update_user.return_value = updated_user

                response = client.put(
                    "/api/v1/auth/me", json=update_data, headers=auth_headers
                )
                assert response.status_code == 200
                data = response.json()
                assert data["full_name"] == update_data["full_name"]
                assert data["email"] == update_data["email"]


class TestCategoryWorkflowIntegration:
    """Integration tests for complete category workflows."""

    def test_category_management_workflow(self, client, sample_user):
        """Test complete category management workflow."""
        auth_headers = {"Authorization": "Bearer test_token"}

        with patch("src.api.authentication.auth.get_current_user") as mock_get_user:
            mock_get_user.return_value = sample_user

            # Create multiple categories
            categories_data = [
                {
                    "name": "Food & Dining",
                    "description": "Restaurant and grocery expenses",
                },
                {
                    "name": "Transportation",
                    "description": "Gas, public transport, and vehicle expenses",
                },
                {
                    "name": "Entertainment",
                    "description": "Movies, games, and entertainment expenses",
                },
            ]

            created_categories = []
            for i, cat_data in enumerate(categories_data, 1):
                with patch(
                    "src.api.category.categories.CategoryService"
                ) as mock_service_class:
                    mock_service = mock_service_class.return_value

                    category = Category(
                        id=i,
                        name=cat_data["name"],
                        description=cat_data["description"],
                        user_id=sample_user.id,
                        is_system=False,
                    )
                    mock_service.create_category.return_value = category
                    created_categories.append(category)

                    response = client.post(
                        "/api/v1/categories/", json=cat_data, headers=auth_headers
                    )
                    assert response.status_code == 201
                    data = response.json()
                    assert data["name"] == cat_data["name"]

            # Get all user categories
            with patch(
                "src.api.category.categories.CategoryService"
            ) as mock_service_class:
                mock_service = mock_service_class.return_value
                mock_service.get_user_categories.return_value = created_categories

                response = client.get("/api/v1/categories/", headers=auth_headers)
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 3

            # Update a category
            update_data = {"description": "Updated food description"}

            with patch(
                "src.api.category.categories.CategoryService"
            ) as mock_service_class:
                mock_service = mock_service_class.return_value
                updated_category = Category(
                    id=1,
                    name="Food & Dining",
                    description="Updated food description",
                    user_id=sample_user.id,
                )
                mock_service.update_category.return_value = updated_category

                response = client.put(
                    "/api/v1/categories/1", json=update_data, headers=auth_headers
                )
                assert response.status_code == 200
                data = response.json()
                assert data["description"] == "Updated food description"

            # Delete a category
            with patch(
                "src.api.category.categories.CategoryService"
            ) as mock_service_class:
                mock_service = mock_service_class.return_value
                mock_service.delete_category.return_value = True

                response = client.delete("/api/v1/categories/1", headers=auth_headers)
                assert response.status_code == 200
                data = response.json()
                assert "deleted successfully" in data["message"]

    def test_system_categories_creation_workflow(self, client, sample_user):
        """Test system categories creation workflow."""
        auth_headers = {"Authorization": "Bearer test_token"}

        with patch("src.api.authentication.auth.get_current_user") as mock_get_user:
            mock_get_user.return_value = sample_user

            with patch(
                "src.api.category.categories.CategoryService"
            ) as mock_service_class:
                mock_service = mock_service_class.return_value

                # Mock system categories
                system_categories = [
                    Category(
                        id=i,
                        name=f"System Category {i}",
                        user_id=sample_user.id,
                        is_system=True,
                    )
                    for i in range(1, 11)
                ]
                mock_service.create_system_categories.return_value = system_categories

                response = client.post(
                    "/api/v1/categories/system", headers=auth_headers
                )
                assert response.status_code == 201
                data = response.json()
                assert len(data) == 10
                assert all(cat["is_system"] for cat in data)


class TestExpenseWorkflowIntegration:
    """Integration tests for complete expense workflows."""

    def test_expense_management_workflow(self, client, sample_user, sample_category):
        """Test complete expense management workflow."""
        auth_headers = {"Authorization": "Bearer test_token"}

        with patch("src.api.authentication.auth.get_current_user") as mock_get_user:
            mock_get_user.return_value = sample_user

            # Create multiple expenses
            expenses_data = [
                {
                    "amount": 50.0,
                    "currency": "USD",
                    "description": "Lunch at restaurant",
                    "status": "pending",
                    "is_recurring": False,
                    "recurring_frequency": None,
                    "expense_date": "2023-01-01T12:00:00",
                    "category_id": sample_category.id,
                },
                {
                    "amount": 25.0,
                    "currency": "USD",
                    "description": "Gas for car",
                    "status": "approved",
                    "is_recurring": False,
                    "recurring_frequency": None,
                    "expense_date": "2023-01-02T08:00:00",
                    "category_id": sample_category.id,
                },
                {
                    "amount": 100.0,
                    "currency": "USD",
                    "description": "Monthly rent",
                    "status": "approved",
                    "is_recurring": True,
                    "recurring_frequency": "monthly",
                    "expense_date": "2023-01-01T00:00:00",
                    "category_id": sample_category.id,
                },
            ]

            created_expenses = []
            for i, exp_data in enumerate(expenses_data, 1):
                with patch(
                    "src.api.expense.expenses.ExpenseService"
                ) as mock_service_class:
                    mock_service = mock_service_class.return_value

                    expense = Expense(
                        id=i,
                        amount=Decimal(str(exp_data["amount"])),
                        currency=exp_data["currency"],
                        description=exp_data["description"],
                        status=exp_data["status"],
                        is_recurring=exp_data["is_recurring"],
                        recurring_frequency=exp_data["recurring_frequency"],
                        expense_date=datetime.fromisoformat(
                            exp_data["expense_date"].replace("Z", "+00:00")
                        ),
                        user_id=sample_user.id,
                        category_id=exp_data["category_id"],
                    )
                    mock_service.create_expense.return_value = expense
                    created_expenses.append(expense)

                    response = client.post(
                        "/api/v1/expenses/", json=exp_data, headers=auth_headers
                    )
                    assert response.status_code == 201
                    data = response.json()
                    assert data["amount"] == exp_data["amount"]

            # Get all user expenses
            with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
                mock_service = mock_service_class.return_value
                mock_service.get_user_expenses.return_value = created_expenses

                response = client.get("/api/v1/expenses/", headers=auth_headers)
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 3

            # Get expenses with filters
            with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
                mock_service = mock_service_class.return_value
                pending_expenses = [
                    exp for exp in created_expenses if exp.status == "pending"
                ]
                mock_service.get_user_expenses.return_value = pending_expenses

                response = client.get(
                    "/api/v1/expenses/?status=pending", headers=auth_headers
                )
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["status"] == "pending"

            # Update an expense
            update_data = {"status": "approved", "description": "Updated expense"}

            with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
                mock_service = mock_service_class.return_value
                updated_expense = Expense(
                    id=1,
                    amount=Decimal("50.0"),
                    currency="USD",
                    description="Updated expense",
                    status="approved",
                    is_recurring=False,
                    recurring_frequency=None,
                    expense_date=datetime(2023, 1, 1, 12, 0, 0),
                    user_id=sample_user.id,
                    category_id=sample_category.id,
                )
                mock_service.update_expense.return_value = updated_expense

                response = client.put(
                    "/api/v1/expenses/1", json=update_data, headers=auth_headers
                )
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "approved"
                assert data["description"] == "Updated expense"

            # Delete an expense
            with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
                mock_service = mock_service_class.return_value
                mock_service.delete_expense.return_value = True

                response = client.delete("/api/v1/expenses/1", headers=auth_headers)
                assert response.status_code == 200
                data = response.json()
                assert "deleted successfully" in data["message"]

    def test_expense_filtering_workflow(self, client, sample_user, multiple_expenses):
        """Test expense filtering and search workflow."""
        auth_headers = {"Authorization": "Bearer test_token"}

        with patch("src.api.authentication.auth.get_current_user") as mock_get_user:
            mock_get_user.return_value = sample_user

            # Test filtering by date range
            with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
                mock_service = mock_service_class.return_value
                mock_service.get_user_expenses.return_value = multiple_expenses

                response = client.get(
                    "/api/v1/expenses/?start_date=2023-01-01&end_date=2023-12-31",
                    headers=auth_headers,
                )
                assert response.status_code == 200
                data = response.json()
                assert len(data) == len(multiple_expenses)

            # Test filtering by amount range
            with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
                mock_service = mock_service_class.return_value
                filtered_expenses = [
                    exp for exp in multiple_expenses if 40 <= float(exp.amount) <= 80
                ]
                mock_service.get_user_expenses.return_value = filtered_expenses

                response = client.get(
                    "/api/v1/expenses/?min_amount=40&max_amount=80",
                    headers=auth_headers,
                )
                assert response.status_code == 200
                data = response.json()
                assert len(data) == len(filtered_expenses)

            # Test filtering by category
            with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
                mock_service = mock_service_class.return_value
                category_expenses = [
                    exp for exp in multiple_expenses if exp.category_id == 1
                ]
                mock_service.get_expenses_by_category.return_value = category_expenses

                response = client.get(
                    "/api/v1/expenses/?category_id=1", headers=auth_headers
                )
                assert response.status_code == 200
                data = response.json()
                assert len(data) == len(category_expenses)


class TestAnalyticsWorkflowIntegration:
    """Integration tests for analytics workflows."""

    def test_analytics_dashboard_workflow(self, client, sample_user, multiple_expenses):
        """Test complete analytics dashboard workflow."""
        auth_headers = {"Authorization": "Bearer test_token"}

        with patch("src.api.authentication.auth.get_current_user") as mock_get_user:
            mock_get_user.return_value = sample_user

            # Test expense summary
            with patch("src.api.user.analytics.UserService") as mock_service_class:
                mock_service = mock_service_class.return_value

                summary_data = {
                    "total_expenses": 1000.0,
                    "total_categories": 5,
                    "average_expense": 200.0,
                    "monthly_trend": [100.0, 150.0, 200.0, 250.0, 300.0],
                    "pending_expenses": 2,
                    "approved_expenses": 3,
                }
                mock_service.get_expense_summary.return_value = summary_data

                response = client.get("/api/v1/analytics/summary", headers=auth_headers)
                assert response.status_code == 200
                data = response.json()
                assert data["total_expenses"] == 1000.0
                assert data["total_categories"] == 5

            # Test category breakdown
            with patch("src.api.user.analytics.UserService") as mock_service_class:
                mock_service = mock_service_class.return_value

                breakdown_data = [
                    {
                        "category": "Food",
                        "total": 500.0,
                        "count": 10,
                        "percentage": 50.0,
                    },
                    {
                        "category": "Transport",
                        "total": 300.0,
                        "count": 5,
                        "percentage": 30.0,
                    },
                    {
                        "category": "Entertainment",
                        "total": 200.0,
                        "count": 3,
                        "percentage": 20.0,
                    },
                ]
                mock_service.get_category_breakdown.return_value = breakdown_data

                response = client.get(
                    "/api/v1/analytics/category-breakdown", headers=auth_headers
                )
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 3
                assert data[0]["category"] == "Food"
                assert data[0]["total"] == 500.0

            # Test monthly trends
            with patch("src.api.user.analytics.UserService") as mock_service_class:
                mock_service = mock_service_class.return_value

                trends_data = [
                    {"month": "2023-01", "total": 1000.0, "count": 20, "average": 50.0},
                    {"month": "2023-02", "total": 1200.0, "count": 25, "average": 48.0},
                    {"month": "2023-03", "total": 1100.0, "count": 22, "average": 50.0},
                ]
                mock_service.get_monthly_trends.return_value = trends_data

                response = client.get(
                    "/api/v1/analytics/monthly-trends", headers=auth_headers
                )
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 3
                assert data[0]["month"] == "2023-01"
                assert data[0]["total"] == 1000.0

    def test_expense_reporting_workflow(self, client, sample_user, multiple_expenses):
        """Test expense reporting workflow."""
        auth_headers = {"Authorization": "Bearer test_token"}

        with patch("src.api.authentication.auth.get_current_user") as mock_get_user:
            mock_get_user.return_value = sample_user

            # Test export expenses
            with patch("src.api.user.analytics.UserService") as mock_service_class:
                mock_service = mock_service_class.return_value
                mock_service.export_expenses.return_value = b"CSV_DATA_HERE"

                response = client.get("/api/v1/analytics/export", headers=auth_headers)
                assert response.status_code == 200
                assert response.headers["content-type"] == "text/csv"
                assert response.content == b"CSV_DATA_HERE"

            # Test expense statistics
            with patch("src.api.user.analytics.UserService") as mock_service_class:
                mock_service = mock_service_class.return_value

                stats_data = {
                    "total_amount": 1000.0,
                    "expense_count": 20,
                    "average_amount": 50.0,
                    "min_amount": 10.0,
                    "max_amount": 200.0,
                    "currency_breakdown": {"USD": 800.0, "EUR": 200.0},
                }
                mock_service.get_expense_statistics.return_value = stats_data

                response = client.get(
                    "/api/v1/analytics/statistics", headers=auth_headers
                )
                assert response.status_code == 200
                data = response.json()
                assert data["total_amount"] == 1000.0
                assert data["expense_count"] == 20


class TestErrorHandlingIntegration:
    """Integration tests for error handling across the application."""

    def test_authentication_error_handling(self, client):
        """Test authentication error handling across endpoints."""
        # Test accessing protected endpoint without token
        response = client.get("/api/v1/categories/")
        assert response.status_code == 401

        # Test accessing protected endpoint with invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/categories/", headers=headers)
        assert response.status_code == 401

    def test_authorization_error_handling(self, client, sample_user):
        """Test authorization error handling."""
        auth_headers = {"Authorization": "Bearer test_token"}

        with patch("src.api.authentication.auth.get_current_user") as mock_get_user:
            mock_get_user.return_value = sample_user

            # Test accessing resource that doesn't belong to user
            with patch(
                "src.api.category.categories.CategoryService"
            ) as mock_service_class:
                mock_service = mock_service_class.return_value
                mock_service.get_category_by_id.side_effect = HTTPException(
                    status_code=403, detail="Access denied to category"
                )

                response = client.get("/api/v1/categories/999", headers=auth_headers)
                assert response.status_code == 403

    def test_validation_error_handling(self, client):
        """Test validation error handling across endpoints."""
        # Test user registration with invalid data
        invalid_user_data = {
            "email": "invalid-email",
            "username": "a",  # Too short
            "password": "123",  # Too short
        }

        response = client.post("/api/v1/auth/register", json=invalid_user_data)
        assert response.status_code == 422

        # Test expense creation with invalid data
        invalid_expense_data = {
            "amount": -100.0,  # Negative amount
            "currency": "INVALID",  # Invalid currency
            "category_id": "not_a_number",  # Invalid category ID
        }

        response = client.post("/api/v1/expenses/", json=invalid_expense_data)
        assert response.status_code == 422

    def test_database_error_handling(self, client, sample_user):
        """Test database error handling."""
        auth_headers = {"Authorization": "Bearer test_token"}

        with patch("src.api.authentication.auth.get_current_user") as mock_get_user:
            mock_get_user.return_value = sample_user

            # Test database connection error
            with patch(
                "src.api.category.categories.CategoryService"
            ) as mock_service_class:
                mock_service = mock_service_class.return_value
                mock_service.create_category.side_effect = Exception(
                    "Database connection failed"
                )

                category_data = {
                    "name": "Test Category",
                    "description": "Test description",
                }
                response = client.post(
                    "/api/v1/categories/", json=category_data, headers=auth_headers
                )
                assert response.status_code == 500

    def test_not_found_error_handling(self, client, sample_user):
        """Test not found error handling."""
        auth_headers = {"Authorization": "Bearer test_token"}

        with patch("src.api.authentication.auth.get_current_user") as mock_get_user:
            mock_get_user.return_value = sample_user

            # Test resource not found
            with patch(
                "src.api.category.categories.CategoryService"
            ) as mock_service_class:
                mock_service = mock_service_class.return_value
                mock_service.get_category_by_id.side_effect = HTTPException(
                    status_code=404, detail="Category not found"
                )

                response = client.get("/api/v1/categories/999", headers=auth_headers)
                assert response.status_code == 404


class TestPerformanceIntegration:
    """Integration tests for performance and scalability."""

    def test_large_dataset_handling(self, client, sample_user):
        """Test handling of large datasets."""
        auth_headers = {"Authorization": "Bearer test_token"}

        with patch("src.api.authentication.auth.get_current_user") as mock_get_user:
            mock_get_user.return_value = sample_user

            # Test pagination with large dataset
            with patch("src.api.expense.expenses.ExpenseService") as mock_service_class:
                mock_service = mock_service_class.return_value

                # Mock large dataset
                large_expense_list = [
                    Expense(
                        id=i,
                        amount=Decimal("50.0"),
                        user_id=sample_user.id,
                        category_id=1,
                    )
                    for i in range(1, 1001)  # 1000 expenses
                ]
                mock_service.get_user_expenses.return_value = large_expense_list[
                    :20
                ]  # First page

                response = client.get(
                    "/api/v1/expenses/?skip=0&limit=20", headers=auth_headers
                )
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 20

    def test_concurrent_request_handling(self, client, sample_user):
        """Test handling of concurrent requests."""
        auth_headers = {"Authorization": "Bearer test_token"}

        with patch("src.api.authentication.auth.get_current_user") as mock_get_user:
            mock_get_user.return_value = sample_user

            # Test multiple concurrent requests
            with patch(
                "src.api.category.categories.CategoryService"
            ) as mock_service_class:
                mock_service = mock_service_class.return_value
                mock_service.get_user_categories.return_value = []

                # Simulate concurrent requests
                responses = []
                for _ in range(10):
                    response = client.get("/api/v1/categories/", headers=auth_headers)
                    responses.append(response)

                # All requests should succeed
                for response in responses:
                    assert response.status_code == 200
