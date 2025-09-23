# Step 2: Design

## System Architecture

The Expense Tracker API follows a layered architecture pattern:

```
┌─────────────────┐
│   API Layer     │  ← FastAPI routers and endpoints
├─────────────────┤
│  Service Layer  │  ← Business logic and validation
├─────────────────┤
│Repository Layer │  ← Data access and database operations
├─────────────────┤
│  Database Layer │  ← PostgreSQL with SQLAlchemy ORM
└─────────────────┘
```

## Core Components

### 1. Authentication System
- JWT-based authentication with 24-hour token expiry
- Password hashing using bcrypt
- Protected routes with dependency injection

### 2. User Management
- User registration and profile management
- Email and username uniqueness validation
- Password change functionality

### 3. Expense Management
- CRUD operations for expenses
- Category association and validation
- Date-based filtering and pagination
- Recurring expense support

### 4. Category Management
- User-defined categories
- System default categories
- Category-based expense filtering

### 5. Analytics Engine
- Monthly expense summaries
- Category-wise spending analysis
- Recurring expense tracking
- Statistical calculations

## Database Design

### Entities and Relationships

1. **Users** (1) ←→ (N) **Expenses**
2. **Users** (1) ←→ (N) **Categories** (user-defined)
3. **Categories** (1) ←→ (N) **Expenses**
4. **System Categories** (0) ←→ (N) **Expenses**

### Key Design Decisions

- **Soft Delete**: Categories marked as system cannot be deleted
- **Currency Support**: Multi-currency expense tracking
- **Audit Trail**: Created/updated timestamps on all entities
- **Data Integrity**: Foreign key constraints and validation

## Security Considerations

- Password hashing with bcrypt
- JWT token validation on protected routes
- Input validation using Pydantic schemas
- SQL injection prevention through ORM
- CORS configuration for frontend integration

## Performance Considerations

- Database indexing on frequently queried fields
- Pagination for large datasets
- Query optimization for analytics
- Connection pooling for database operations
