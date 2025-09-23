# Step 4: API Endpoints Overview

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication Endpoints

### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "Full Name"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### POST /auth/login
Authenticate user and return JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### GET /auth/me
Get current user profile.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### PUT /auth/me
Update current user profile.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "full_name": "New Full Name"
}
```

### POST /auth/change-password
Change user password.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}
```

## Expense Endpoints

### POST /expenses/
Create a new expense.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "amount": 100.50,
  "currency": "USD",
  "description": "Grocery shopping",
  "status": "pending",
  "is_recurring": false,
  "expense_date": "2024-01-01T00:00:00",
  "category_id": 1
}
```

### GET /expenses/
Get user expenses with optional filtering.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `skip` (int): Number of expenses to skip (default: 0)
- `limit` (int): Number of expenses to return (default: 20, max: 100)
- `category_id` (int): Filter by category ID
- `status` (str): Filter by status (pending, approved, rejected)
- `start_date` (date): Filter by start date
- `end_date` (date): Filter by end date

### GET /expenses/{expense_id}
Get specific expense by ID.

**Headers:** `Authorization: Bearer <token>`

### PUT /expenses/{expense_id}
Update expense.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "amount": 150.00,
  "description": "Updated description"
}
```

### DELETE /expenses/{expense_id}
Delete expense.

**Headers:** `Authorization: Bearer <token>`

### GET /expenses/monthly/{year}/{month}
Get expenses for specific month.

**Headers:** `Authorization: Bearer <token>`

## Category Endpoints

### POST /categories/
Create a new category.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Food & Dining",
  "description": "Restaurants and groceries",
  "color": "#FF6B6B"
}
```

### GET /categories/
Get user categories.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `skip` (int): Number of categories to skip (default: 0)
- `limit` (int): Number of categories to return (default: 100, max: 100)

### GET /categories/{category_id}
Get specific category by ID.

**Headers:** `Authorization: Bearer <token>`

### PUT /categories/{category_id}
Update category.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Updated Category Name",
  "description": "Updated description"
}
```

### DELETE /categories/{category_id}
Delete category.

**Headers:** `Authorization: Bearer <token>`

### POST /categories/init-system-categories
Initialize system categories (admin only).

**Headers:** `Authorization: Bearer <token>`

## Analytics Endpoints

### GET /analytics/stats
Get expense statistics.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `start_date` (date): Start date for statistics
- `end_date` (date): End date for statistics
- `currency` (str): Currency for statistics (default: USD)

**Response:** `200 OK`
```json
{
  "total_amount": 1500.00,
  "total_count": 25,
  "average_amount": 60.00,
  "currency": "USD"
}
```

### GET /analytics/category-stats
Get expense statistics by category.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `start_date` (date): Start date for statistics
- `end_date` (date): End date for statistics
- `limit` (int): Number of top categories to return (default: 10, max: 50)

### GET /analytics/monthly/{year}/{month}
Get monthly analytics.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "total_amount": 500.00,
  "total_count": 10,
  "average_amount": 50.00,
  "currency": "USD",
  "top_categories": [
    {
      "category_id": 1,
      "total_amount": 200.00,
      "total_count": 5
    }
  ],
  "recurring_count": 2
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["field_name"],
      "msg": "error message",
      "type": "error_type"
    }
  ]
}
```
