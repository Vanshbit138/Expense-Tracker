# API Reference

Complete API reference for the Expense Tracker application.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints except `/auth/register` and `/auth/login` require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "data": { ... },
  "message": "Success message (optional)"
}
```

### Error Response
```json
{
  "detail": "Error message",
  "type": "error_type",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |

---

## Authentication Endpoints

### Register User

**POST** `/auth/register`

Register a new user account.

#### Request Body
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

#### Response
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Validation Rules
- `email`: Valid email format, unique
- `username`: 3-50 characters, alphanumeric and underscores only, unique
- `password`: Minimum 8 characters, must contain letters and numbers
- `full_name`: Optional, maximum 100 characters

---

### Login User

**POST** `/auth/login`

Authenticate user and receive JWT token.

#### Request Body
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

#### Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### Get Current User

**GET** `/auth/me`

Get current authenticated user information.

#### Headers
```
Authorization: Bearer <jwt-token>
```

#### Response
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

---

### Change Password

**POST** `/auth/change-password`

Change user password.

#### Headers
```
Authorization: Bearer <jwt-token>
```

#### Request Body
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword123"
}
```

#### Response
```json
{
  "message": "Password changed successfully"
}
```

---

## Expense Endpoints

### Create Expense

**POST** `/expenses/`

Create a new expense record.

#### Headers
```
Authorization: Bearer <jwt-token>
```

#### Request Body
```json
{
  "amount": 25.50,
  "currency": "USD",
  "description": "Lunch at restaurant",
  "category_id": 1,
  "expense_date": "2024-01-15",
  "status": "pending",
  "is_recurring": false,
  "recurring_frequency": null
}
```

#### Response
```json
{
  "id": 1,
  "amount": 25.50,
  "currency": "USD",
  "description": "Lunch at restaurant",
  "category_id": 1,
  "expense_date": "2024-01-15",
  "status": "pending",
  "is_recurring": false,
  "recurring_frequency": null,
  "user_id": 1,
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

#### Validation Rules
- `amount`: Positive decimal, maximum 999,999.99
- `currency`: One of: USD, EUR, GBP, JPY, CAD, AUD
- `description`: 1-500 characters, required
- `category_id`: Positive integer, must exist
- `expense_date`: Valid date
- `status`: One of: pending, approved, rejected
- `recurring_frequency`: One of: daily, weekly, monthly, yearly (if recurring)

---

### List Expenses

**GET** `/expenses/`

Get user's expenses with optional filtering.

#### Headers
```
Authorization: Bearer <jwt-token>
```

#### Query Parameters
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `skip` | integer | Number of expenses to skip | 0 |
| `limit` | integer | Number of expenses to return (1-100) | 20 |
| `start_date` | date | Filter expenses from this date | null |
| `end_date` | date | Filter expenses to this date | null |

#### Example Request
```
GET /expenses/?skip=0&limit=10&start_date=2024-01-01&end_date=2024-01-31
```

#### Response
```json
[
  {
    "id": 1,
    "amount": 25.50,
    "currency": "USD",
    "description": "Lunch at restaurant",
    "category_id": 1,
    "expense_date": "2024-01-15",
    "status": "pending",
    "is_recurring": false,
    "recurring_frequency": null,
    "user_id": 1,
    "created_at": "2024-01-15T12:00:00Z",
    "updated_at": "2024-01-15T12:00:00Z"
  }
]
```

---

### Get Expense

**GET** `/expenses/{expense_id}`

Get a specific expense by ID.

#### Headers
```
Authorization: Bearer <jwt-token>
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `expense_id` | integer | Expense ID |

#### Response
```json
{
  "id": 1,
  "amount": 25.50,
  "currency": "USD",
  "description": "Lunch at restaurant",
  "category_id": 1,
  "expense_date": "2024-01-15",
  "status": "pending",
  "is_recurring": false,
  "recurring_frequency": null,
  "user_id": 1,
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

---

### Update Expense

**PUT** `/expenses/{expense_id}`

Update an existing expense.

#### Headers
```
Authorization: Bearer <jwt-token>
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `expense_id` | integer | Expense ID |

#### Request Body
```json
{
  "amount": 30.00,
  "description": "Updated lunch description",
  "status": "approved"
}
```

#### Response
```json
{
  "id": 1,
  "amount": 30.00,
  "currency": "USD",
  "description": "Updated lunch description",
  "category_id": 1,
  "expense_date": "2024-01-15",
  "status": "approved",
  "is_recurring": false,
  "recurring_frequency": null,
  "user_id": 1,
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:30:00Z"
}
```

---

### Delete Expense

**DELETE** `/expenses/{expense_id}`

Delete an expense.

#### Headers
```
Authorization: Bearer <jwt-token>
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `expense_id` | integer | Expense ID |

#### Response
```json
{
  "message": "Expense deleted successfully"
}
```

---

### Get Monthly Expenses

**GET** `/expenses/monthly/{year}/{month}`

Get expenses for a specific month.

#### Headers
```
Authorization: Bearer <jwt-token>
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `year` | integer | Year (e.g., 2024) |
| `month` | integer | Month (1-12) |

#### Response
```json
[
  {
    "id": 1,
    "amount": 25.50,
    "currency": "USD",
    "description": "Lunch at restaurant",
    "category_id": 1,
    "expense_date": "2024-01-15",
    "status": "pending",
    "is_recurring": false,
    "recurring_frequency": null,
    "user_id": 1,
    "created_at": "2024-01-15T12:00:00Z",
    "updated_at": "2024-01-15T12:00:00Z"
  }
]
```

---

## Category Endpoints

### Create Category

**POST** `/categories/`

Create a new expense category.

#### Headers
```
Authorization: Bearer <jwt-token>
```

#### Request Body
```json
{
  "name": "Groceries",
  "description": "Food and household items",
  "color": "#FF5733"
}
```

#### Response
```json
{
  "id": 1,
  "name": "Groceries",
  "description": "Food and household items",
  "is_system": false,
  "color": "#FF5733",
  "user_id": 1,
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

#### Validation Rules
- `name`: 1-100 characters, unique per user
- `description`: Optional, maximum 500 characters
- `color`: Optional, valid hex color code

---

### List Categories

**GET** `/categories/`

Get user's categories.

#### Headers
```
Authorization: Bearer <jwt-token>
```

#### Query Parameters
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `skip` | integer | Number of categories to skip | 0 |
| `limit` | integer | Number of categories to return (1-100) | 100 |

#### Response
```json
[
  {
    "id": 1,
    "name": "Groceries",
    "description": "Food and household items",
    "is_system": false,
    "color": "#FF5733",
    "user_id": 1,
    "created_at": "2024-01-15T12:00:00Z",
    "updated_at": "2024-01-15T12:00:00Z"
  }
]
```

---

### Get Category

**GET** `/categories/{category_id}`

Get a specific category by ID.

#### Headers
```
Authorization: Bearer <jwt-token>
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `category_id` | integer | Category ID |

#### Response
```json
{
  "id": 1,
  "name": "Groceries",
  "description": "Food and household items",
  "is_system": false,
  "color": "#FF5733",
  "user_id": 1,
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

---

### Update Category

**PUT** `/categories/{category_id}`

Update an existing category.

#### Headers
```
Authorization: Bearer <jwt-token>
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `category_id` | integer | Category ID |

#### Request Body
```json
{
  "name": "Updated Groceries",
  "description": "Updated description",
  "color": "#00FF00"
}
```

#### Response
```json
{
  "id": 1,
  "name": "Updated Groceries",
  "description": "Updated description",
  "is_system": false,
  "color": "#00FF00",
  "user_id": 1,
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:30:00Z"
}
```

---

### Delete Category

**DELETE** `/categories/{category_id}`

Delete a category.

#### Headers
```
Authorization: Bearer <jwt-token>
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `category_id` | integer | Category ID |

#### Response
```json
{
  "message": "Category deleted successfully"
}
```

---

### Initialize System Categories

**POST** `/categories/init-system-categories`

Initialize system categories (admin only).

#### Headers
```
Authorization: Bearer <jwt-token>
```

#### Response
```json
{
  "message": "Created 5 system categories",
  "categories": [
    {
      "id": 1,
      "name": "Food & Dining",
      "description": "Restaurants, groceries, and food expenses",
      "is_system": true,
      "color": "#FF5733",
      "user_id": null,
      "created_at": "2024-01-15T12:00:00Z",
      "updated_at": "2024-01-15T12:00:00Z"
    }
  ]
}
```

---

## Analytics Endpoints

### Get Expense Statistics

**GET** `/analytics/stats`

Get expense statistics for the user.

#### Headers
```
Authorization: Bearer <jwt-token>
```

#### Query Parameters
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `start_date` | date | Start date for statistics | null |
| `end_date` | date | End date for statistics | null |
| `currency` | string | Currency filter | null |

#### Response
```json
{
  "total_expenses": 1500.50,
  "average_expense": 75.03,
  "expense_count": 20,
  "currency": "USD",
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "by_status": {
    "pending": 5,
    "approved": 12,
    "rejected": 3
  }
}
```

---

### Get Category Statistics

**GET** `/analytics/category-stats`

Get expense statistics by category.

#### Headers
```
Authorization: Bearer <jwt-token>
```

#### Query Parameters
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `start_date` | date | Start date for statistics | null |
| `end_date` | date | End date for statistics | null |
| `limit` | integer | Number of categories to return (1-50) | 10 |

#### Response
```json
[
  {
    "category_id": 1,
    "category_name": "Groceries",
    "total_amount": 500.00,
    "expense_count": 8,
    "average_amount": 62.50,
    "percentage": 33.33
  }
]
```

---

### Get Monthly Analytics

**GET** `/analytics/monthly/{year}/{month}`

Get monthly analytics for a specific month.

#### Headers
```
Authorization: Bearer <jwt-token>
```

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `year` | integer | Year (e.g., 2024) |
| `month` | integer | Month (1-12) |

#### Response
```json
{
  "month": 1,
  "year": 2024,
  "total_expenses": 750.25,
  "expense_count": 15,
  "average_daily": 24.20,
  "top_categories": [
    {
      "category_id": 1,
      "category_name": "Groceries",
      "amount": 300.00,
      "percentage": 40.0
    }
  ],
  "daily_breakdown": [
    {
      "date": "2024-01-01",
      "total": 50.00,
      "count": 2
    }
  ]
}
```

---

## System Endpoints

### Health Check

**GET** `/health`

Check application health status.

#### Response
```json
{
  "status": "healthy"
}
```

---

### Root Endpoint

**GET** `/`

Get application information.

#### Response
```json
{
  "message": "Welcome to the Expense Tracker API"
}
```

---

## Error Handling

### Validation Errors (422)

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Authentication Errors (401)

```json
{
  "detail": "Incorrect email or password"
}
```

### Authorization Errors (403)

```json
{
  "detail": "Not enough permissions"
}
```

### Not Found Errors (404)

```json
{
  "detail": "Expense not found"
}
```

### Server Errors (500)

```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently, there are no rate limits implemented. Future versions will include:
- 100 requests per minute per user
- 1000 requests per hour per user
- Burst protection for authentication endpoints

---

## Pagination

List endpoints support pagination with the following parameters:

- `skip`: Number of items to skip (default: 0)
- `limit`: Number of items to return (default: varies by endpoint)

Example:
```
GET /expenses/?skip=20&limit=10
```

---

## Filtering and Sorting

### Date Filtering
Most endpoints support date filtering:
- `start_date`: Filter from this date (inclusive)
- `end_date`: Filter to this date (inclusive)

### Currency Filtering
Expense-related endpoints support currency filtering:
- `currency`: Filter by specific currency code

---

## Data Models

### User Model
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Expense Model
```json
{
  "id": 1,
  "amount": 25.50,
  "currency": "USD",
  "description": "Lunch at restaurant",
  "category_id": 1,
  "expense_date": "2024-01-15",
  "status": "pending",
  "is_recurring": false,
  "recurring_frequency": null,
  "user_id": 1,
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

### Category Model
```json
{
  "id": 1,
  "name": "Groceries",
  "description": "Food and household items",
  "is_system": false,
  "color": "#FF5733",
  "user_id": 1,
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

---

## SDKs and Libraries

### Python
```python
import requests

# Set up client
base_url = "http://localhost:8000/api/v1"
headers = {"Authorization": "Bearer <your-token>"}

# Create expense
response = requests.post(
    f"{base_url}/expenses/",
    json={
        "amount": 25.50,
        "currency": "USD",
        "description": "Lunch",
        "category_id": 1,
        "expense_date": "2024-01-15"
    },
    headers=headers
)
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

// Set up client
const client = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Authorization': 'Bearer <your-token>'
  }
});

// Create expense
const response = await client.post('/expenses/', {
  amount: 25.50,
  currency: 'USD',
  description: 'Lunch',
  category_id: 1,
  expense_date: '2024-01-15'
});
```

### cURL Examples

#### Register User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

#### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

#### Create Expense
```bash
curl -X POST "http://localhost:8000/api/v1/expenses/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "amount": 25.50,
    "currency": "USD",
    "description": "Lunch at restaurant",
    "category_id": 1,
    "expense_date": "2024-01-15"
  }'
```

---

## Changelog

### Version 1.0.0
- Initial release
- User authentication and registration
- Expense CRUD operations
- Category management
- Basic analytics and reporting
- JWT-based authentication
- Comprehensive test coverage
