# Postman Testing Guide

## Setup Instructions

### 1. Import Collection
1. Open Postman
2. Click "Import" button
3. Select the `postman_collection.json` file from `docs/testing/`
4. The collection will be imported with all endpoints

### 2. Environment Setup
1. Create a new environment in Postman
2. Add the following variables:
   - `base_url`: `http://localhost:8000`
   - `token`: (leave empty, will be auto-populated)

### 3. Testing Sequence

#### Step 1: Health Check
- Run "Health Check" to verify server is running
- Expected: 200 OK with health status

#### Step 2: Authentication Flow
1. **Register User**: Create a new user account
2. **Login User**: Authenticate and get JWT token (auto-saved)
3. **Change Password**: Update user password

#### Step 3: Category Management
1. **Create Category**: Add a new expense category
2. **Get All Categories**: List all categories
3. **Get Category by ID**: Retrieve specific category
4. **Update Category**: Modify category details

#### Step 4: Expense Management
1. **Create Expense**: Add a new expense
2. **Get All Expenses**: List all expenses
3. **Get Expense by ID**: Retrieve specific expense
4. **Update Expense**: Modify expense details

#### Step 5: Analytics
1. **Get General Stats**: View overall statistics
2. **Get Category Stats**: View category breakdown
3. **Get Monthly Analytics**: View monthly reports

## Expected Results

### Authentication
- Registration: 200 OK with user details
- Login: 200 OK with JWT token
- Password Change: 200 OK with success message

### Categories
- Create: 200 OK with category details
- List: 200 OK with array of categories
- Get: 200 OK with specific category
- Update: 200 OK with updated category

### Expenses
- Create: 200 OK with expense details
- List: 200 OK with array of expenses
- Get: 200 OK with specific expense
- Update: 200 OK with updated expense

### Analytics
- Stats: 200 OK with statistics object
- Category Stats: 200 OK with category breakdown
- Monthly: 200 OK with monthly analytics

## Troubleshooting

### Common Issues
1. **401 Unauthorized**: Token expired or missing
   - Solution: Re-run login request to get new token

2. **404 Not Found**: Endpoint not found
   - Solution: Check base_url variable and server status

3. **500 Internal Server Error**: Server error
   - Solution: Check server logs and database connection

### Log Verification
After each request, check the application logs to verify:
- Request logging with correlation IDs
- Service method logging
- Error logging (if any)
- Performance metrics
