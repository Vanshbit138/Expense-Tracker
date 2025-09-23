# Step 5: Database Schema

## Entity Relationship Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Users      │    │   Categories    │    │    Expenses     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ id (PK)         │    │ id (PK)         │    │ id (PK)         │
│ email (UNIQUE)  │    │ name            │    │ amount          │
│ username (UNIQUE)│   │ description     │    │ currency        │
│ hashed_password │    │ is_system       │    │ description     │
│ full_name       │    │ color           │    │ status          │
│ is_active       │    │ user_id (FK)    │    │ is_recurring    │
│ is_superuser    │    │ created_at      │    │ recurring_freq  │
│ created_at      │    │ updated_at      │    │ expense_date    │
│ updated_at      │    └─────────────────┘    │ user_id (FK)    │
└─────────────────┘           │                │ category_id (FK)│
         │                    │                │ created_at      │
         │                    │                │ updated_at      │
         │                    │                └─────────────────┘
         │                    │                         │
         │                    └─────────────────────────┘
         │
         └──────────────────────────────────────────────┘
```

## Table Definitions

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_users_email` on `email`
- `idx_users_username` on `username`

### Categories Table
```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT FALSE,
    color VARCHAR,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_categories_name` on `name`
- `idx_categories_user_id` on `user_id`
- `idx_categories_is_system` on `is_system`

**Constraints:**
- System categories have `user_id = NULL`
- User categories must have valid `user_id`

### Expenses Table
```sql
CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    amount NUMERIC(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD' NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    is_recurring BOOLEAN DEFAULT FALSE,
    recurring_frequency VARCHAR(20),
    expense_date TIMESTAMP NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_expenses_user_id` on `user_id`
- `idx_expenses_category_id` on `category_id`
- `idx_expenses_expense_date` on `expense_date`
- `idx_expenses_status` on `status`
- `idx_expenses_user_date` on `(user_id, expense_date)`

**Constraints:**
- `amount` must be positive
- `currency` must be valid 3-letter code
- `status` must be one of: pending, approved, rejected
- `recurring_frequency` must be one of: daily, weekly, monthly, yearly (if recurring)

## Data Types and Constraints

### Numeric Types
- `SERIAL`: Auto-incrementing integer primary key
- `NUMERIC(10,2)`: Decimal with 10 total digits, 2 after decimal point
- `INTEGER`: Standard integer for foreign keys

### String Types
- `VARCHAR`: Variable-length string with optional length limit
- `TEXT`: Unlimited length text for descriptions
- `VARCHAR(3)`: Fixed 3-character string for currency codes

### Boolean Types
- `BOOLEAN`: True/false values with default constraints

### Date/Time Types
- `TIMESTAMP`: Date and time with timezone support
- `CURRENT_TIMESTAMP`: Default value for created/updated timestamps

## Relationships

### One-to-Many Relationships
1. **Users → Expenses**: One user can have many expenses
2. **Users → Categories**: One user can have many custom categories
3. **Categories → Expenses**: One category can have many expenses

### Many-to-Many Relationships
- **Users ↔ System Categories**: Users can access all system categories

## Data Integrity Rules

### Referential Integrity
- Foreign key constraints ensure data consistency
- `ON DELETE CASCADE` for user-related data
- `ON DELETE RESTRICT` for category references to prevent orphaned expenses

### Business Rules
- User email and username must be unique
- Category names must be unique per user (including system categories)
- Expense amounts must be positive
- System categories cannot be deleted or modified by users
- Users can only access their own expenses and custom categories

### Validation Rules
- Email format validation
- Password strength requirements
- Currency code validation (ISO 4217)
- Date range validation for expense dates
- Status enum validation

## Performance Considerations

### Indexing Strategy
- Primary keys are automatically indexed
- Foreign keys are indexed for join performance
- Composite indexes for common query patterns
- Partial indexes for filtered queries

### Query Optimization
- Use appropriate data types to minimize storage
- Normalize data to reduce redundancy
- Consider denormalization for frequently accessed data
- Implement proper indexing for search patterns

## Migration Strategy

### Initial Migration
1. Create users table
2. Create categories table with system categories
3. Create expenses table
4. Add indexes and constraints
5. Insert default system categories

### Future Migrations
- Add new columns with default values
- Create new indexes for performance
- Add new tables for additional features
- Modify constraints as business rules evolve
