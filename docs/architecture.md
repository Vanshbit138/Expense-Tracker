# Architecture Documentation

Comprehensive architecture documentation for the Expense Tracker application.

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Patterns](#architecture-patterns)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Security Architecture](#security-architecture)
- [Scalability Considerations](#scalability-considerations)
- [Technology Stack](#technology-stack)
- [Design Decisions](#design-decisions)
- [Performance Considerations](#performance-considerations)
- [Monitoring and Observability](#monitoring-and-observability)

## System Overview

The Expense Tracker is a RESTful API built with FastAPI that provides comprehensive expense management capabilities. The system follows a layered architecture pattern with clear separation of concerns.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Web App   │  │  Mobile App │  │  API Client │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS/REST API
┌─────────────────────▼───────────────────────────────────────┐
│                FastAPI Application                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                API Layer                            │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │    Auth     │ │  Expenses   │ │  Analytics  │   │   │
│  │  │   Router    │ │   Router    │ │   Router    │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Service Layer                          │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │    User     │ │  Expense    │ │  Category   │   │   │
│  │  │   Service   │ │   Service   │ │   Service   │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Repository Layer                         │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │    User     │ │  Expense    │ │  Category   │   │   │
│  │  │ Repository  │ │ Repository  │ │ Repository  │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │ SQL/ORM
┌─────────────────────▼───────────────────────────────────────┐
│                PostgreSQL Database                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │    Users    │ │  Categories │ │  Expenses   │          │
│  │    Table    │ │    Table    │ │    Table    │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## Architecture Patterns

### 1. Layered Architecture

The application follows a three-layer architecture pattern:

- **API Layer**: Handles HTTP requests, validation, and responses
- **Service Layer**: Contains business logic and orchestration
- **Repository Layer**: Manages data access and persistence

### 2. Dependency Injection

FastAPI's dependency injection system is used throughout the application:

```python
# Example: Database dependency
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage in endpoints
@app.get("/expenses/")
def get_expenses(db: Session = Depends(get_db)):
    # Database session automatically injected
    pass
```

### 3. Repository Pattern

Data access is abstracted through repository interfaces:

```python
class BaseRepository(Generic[T]):
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, obj: T) -> T:
        # Implementation
        pass
    
    def get_by_id(self, id: int) -> Optional[T]:
        # Implementation
        pass
```

### 4. Service Layer Pattern

Business logic is encapsulated in service classes:

```python
class ExpenseService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = ExpenseRepository(db)
    
    def create_expense(self, expense_data: ExpenseCreate, user_id: int) -> Expense:
        # Business logic here
        pass
```

## Component Architecture

### API Layer Components

#### 1. FastAPI Application

**File**: `src/api/main.py`

**Responsibilities:**
- Application initialization
- Middleware configuration
- Router registration
- Exception handling
- CORS configuration

**Key Features:**
- Automatic OpenAPI documentation
- Request validation
- Response serialization
- Error handling

#### 2. Authentication Router

**File**: `src/api/authentication/auth.py`

**Endpoints:**
- `POST /auth/register` - User registration
- `POST /auth/login` - User authentication
- `GET /auth/me` - Get current user
- `POST /auth/change-password` - Change password

**Security Features:**
- JWT token generation
- Password hashing
- Input validation
- Rate limiting (future)

#### 3. Expense Router

**File**: `src/api/expense/expenses.py`

**Endpoints:**
- `POST /expenses/` - Create expense
- `GET /expenses/` - List expenses
- `GET /expenses/{id}` - Get expense
- `PUT /expenses/{id}` - Update expense
- `DELETE /expenses/{id}` - Delete expense
- `GET /expenses/monthly/{year}/{month}` - Monthly expenses

**Features:**
- Pagination
- Date filtering
- User isolation
- Validation

#### 4. Category Router

**File**: `src/api/category/categories.py`

**Endpoints:**
- `POST /categories/` - Create category
- `GET /categories/` - List categories
- `GET /categories/{id}` - Get category
- `PUT /categories/{id}` - Update category
- `DELETE /categories/{id}` - Delete category
- `POST /categories/init-system-categories` - Initialize system categories

**Features:**
- User-specific categories
- System categories
- Color coding
- Admin-only operations

#### 5. Analytics Router

**File**: `src/api/user/analytics.py`

**Endpoints:**
- `GET /analytics/stats` - Expense statistics
- `GET /analytics/category-stats` - Category statistics
- `GET /analytics/monthly/{year}/{month}` - Monthly analytics

**Features:**
- Statistical calculations
- Date range filtering
- Category breakdown
- Performance metrics

### Service Layer Components

#### 1. User Service

**File**: `src/services/user/user_service.py`

**Responsibilities:**
- User registration
- User authentication
- Password management
- Profile management

**Key Methods:**
- `create_user()` - Create new user
- `authenticate_user()` - Authenticate user
- `change_password()` - Change password
- `get_user_by_id()` - Get user by ID

#### 2. Expense Service

**File**: `src/services/expense/expense_service.py`

**Responsibilities:**
- Expense CRUD operations
- Business rule enforcement
- Analytics calculations
- Data validation

**Key Methods:**
- `create_expense()` - Create expense
- `get_user_expenses()` - Get user expenses
- `get_expense_stats()` - Calculate statistics
- `get_monthly_expenses()` - Get monthly data

#### 3. Category Service

**File**: `src/services/category/category_service.py`

**Responsibilities:**
- Category management
- System category initialization
- User category isolation
- Category validation

**Key Methods:**
- `create_category()` - Create category
- `get_user_categories()` - Get user categories
- `create_system_categories()` - Initialize system categories
- `delete_category()` - Delete category

### Repository Layer Components

#### 1. Base Repository

**File**: `src/repositories/async_base_repository.py`

**Responsibilities:**
- Common CRUD operations
- Query optimization
- Transaction management
- Error handling

**Key Methods:**
- `create()` - Create entity
- `get_by_id()` - Get by ID
- `get_all()` - Get all entities
- `update()` - Update entity
- `delete()` - Delete entity

#### 2. User Repository

**File**: `src/repositories/user/user_repository.py`

**Responsibilities:**
- User data access
- User queries
- User validation
- Database operations

#### 3. Expense Repository

**File**: `src/repositories/expense/expense_repository.py`

**Responsibilities:**
- Expense data access
- Complex queries
- Analytics queries
- Performance optimization

#### 4. Category Repository

**File**: `src/repositories/category/category_repository.py`

**Responsibilities:**
- Category data access
- System category queries
- User category queries
- Category validation

### Core Components

#### 1. Configuration Management

**File**: `src/core/config.py`

**Responsibilities:**
- Environment variable management
- Configuration validation
- Default value handling
- Security validation

**Key Features:**
- Pydantic settings
- Environment validation
- Type safety
- Documentation

#### 2. Database Management

**File**: `src/core/database.py`

**Responsibilities:**
- Database connection
- Session management
- Connection pooling
- Transaction handling

**Key Features:**
- SQLAlchemy ORM
- Connection pooling
- Session lifecycle
- Error handling

#### 3. Security Management

**File**: `src/core/security.py`

**Responsibilities:**
- JWT token handling
- Password hashing
- Authentication
- Authorization

**Key Features:**
- JWT token generation
- Password hashing (bcrypt)
- Token validation
- Security utilities

#### 4. Logging Configuration

**File**: `src/core/logging_config.py`

**Responsibilities:**
- Logging setup
- Log formatting
- Log levels
- Log destinations

**Key Features:**
- Structured logging
- JSON format
- Correlation IDs
- Performance metrics

## Data Flow

### 1. User Registration Flow

```
1. Client → POST /auth/register
2. API Router → Validate request schema
3. Service Layer → Check user existence
4. Service Layer → Hash password
5. Repository Layer → Create user in database
6. Database → Return created user
7. Repository → Return user model
8. Service → Return user data
9. API Router → Return JSON response
10. Client ← HTTP 201 Created
```

### 2. Expense Creation Flow

```
1. Client → POST /expenses/ (with JWT token)
2. API Router → Validate JWT token
3. API Router → Validate request schema
4. Service Layer → Business validation
5. Service Layer → Check category exists
6. Repository Layer → Create expense in database
7. Database → Return created expense
8. Repository → Return expense model
9. Service → Return expense data
10. API Router → Return JSON response
11. Client ← HTTP 201 Created
```

### 3. Analytics Query Flow

```
1. Client → GET /analytics/stats (with JWT token)
2. API Router → Validate JWT token
3. Service Layer → Build query parameters
4. Repository Layer → Execute analytics queries
5. Database → Return aggregated data
6. Repository → Return statistics
7. Service → Format analytics data
8. API Router → Return JSON response
9. Client ← HTTP 200 OK
```

## Security Architecture

### 1. Authentication Flow

```
1. User submits credentials → API Layer
2. Service Layer validates credentials → Database
3. JWT token generated → Client
4. Client includes token in subsequent requests
5. Middleware validates token → Service Layer
6. Authorized request processed → Database
```

### 2. Security Measures

#### Password Security
- **Hashing**: bcrypt with salt
- **Minimum Length**: 8 characters
- **Complexity**: Letters and numbers required
- **Storage**: Never stored in plain text

#### JWT Security
- **Algorithm**: HS256
- **Expiration**: 24 hours
- **Secret Key**: Minimum 32 characters
- **Validation**: Signature and expiration checks

#### Input Validation
- **Schema Validation**: Pydantic models
- **Type Safety**: Python type hints
- **Sanitization**: Automatic by Pydantic
- **SQL Injection**: Prevented by SQLAlchemy ORM

#### CORS Security
- **Origins**: Configurable allowed origins
- **Methods**: Specific HTTP methods
- **Headers**: Controlled header access
- **Credentials**: Controlled credential sharing

### 3. Authorization Model

#### User Roles
- **Regular User**: Can manage own data
- **Superuser**: Can manage system categories
- **Admin**: Full system access (future)

#### Data Isolation
- **User Data**: Isolated by user_id
- **Categories**: User-specific and system categories
- **Expenses**: User-specific only
- **Analytics**: User-specific only

## Scalability Considerations

### 1. Horizontal Scaling

#### Stateless Design
- **JWT Tokens**: Enable load balancing
- **No Session Storage**: Stateless requests
- **Database**: Centralized data storage
- **Caching**: Future Redis integration

#### Load Balancing
- **Multiple Instances**: Run multiple app instances
- **Health Checks**: Monitor instance health
- **Session Affinity**: Not required (stateless)
- **Database Connection Pooling**: Efficient connection management

### 2. Vertical Scaling

#### Database Optimization
- **Indexing**: Optimized for common queries
- **Query Optimization**: Efficient SQL generation
- **Connection Pooling**: Configurable pool sizes
- **Read Replicas**: Future implementation

#### Application Optimization
- **Memory Management**: Proper resource cleanup
- **Connection Pooling**: Efficient database connections
- **Caching**: Future Redis integration
- **Async Operations**: Future async/await implementation

### 3. Caching Strategy

#### Application-Level Caching
- **User Data**: Cache user information
- **Categories**: Cache system categories
- **Statistics**: Cache computed statistics
- **TTL**: Time-to-live for cache entries

#### Database-Level Caching
- **Query Cache**: Database query caching
- **Connection Pooling**: Efficient connections
- **Index Optimization**: Proper indexing
- **Query Optimization**: Efficient queries

## Technology Stack

### Backend Technologies

#### Framework
- **FastAPI**: Modern, fast web framework
- **Python 3.10+**: Programming language
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

#### Database
- **PostgreSQL**: Primary database
- **SQLAlchemy**: ORM
- **Alembic**: Database migrations
- **psycopg2**: PostgreSQL adapter

#### Authentication
- **JWT**: Token-based authentication
- **PyJWT**: JWT library
- **bcrypt**: Password hashing
- **passlib**: Password utilities

#### Development Tools
- **pytest**: Testing framework
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

### Infrastructure Technologies

#### Web Server
- **Nginx**: Reverse proxy
- **SSL/TLS**: HTTPS encryption
- **Load Balancing**: Multiple instances

#### Database
- **PostgreSQL**: Primary database
- **Connection Pooling**: Efficient connections
- **Backup**: Automated backups
- **Monitoring**: Database monitoring

#### Deployment
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **systemd**: Service management
- **Cron**: Scheduled tasks

## Design Decisions

### 1. Framework Choice: FastAPI

**Decision**: Use FastAPI instead of Django or Flask

**Rationale**:
- **Performance**: High performance with async support
- **Type Safety**: Built-in type hints and validation
- **Documentation**: Automatic OpenAPI documentation
- **Modern**: Modern Python features and patterns
- **Validation**: Built-in request/response validation

**Trade-offs**:
- **Learning Curve**: Steeper than Flask
- **Ecosystem**: Smaller than Django
- **Maturity**: Newer than Django/Flask

### 2. Database Choice: PostgreSQL

**Decision**: Use PostgreSQL instead of MySQL or SQLite

**Rationale**:
- **ACID Compliance**: Full ACID transactions
- **JSON Support**: Native JSON data types
- **Performance**: Excellent performance
- **Features**: Rich feature set
- **Scalability**: Good horizontal scaling

**Trade-offs**:
- **Complexity**: More complex than SQLite
- **Resource Usage**: Higher than SQLite
- **Learning Curve**: Steeper than MySQL

### 3. ORM Choice: SQLAlchemy

**Decision**: Use SQLAlchemy instead of raw SQL or other ORMs

**Rationale**:
- **Maturity**: Mature and stable
- **Features**: Rich feature set
- **Performance**: Good performance
- **Flexibility**: Flexible query building
- **Documentation**: Excellent documentation

**Trade-offs**:
- **Learning Curve**: Steeper than simpler ORMs
- **Complexity**: More complex than raw SQL
- **Performance**: Slight overhead vs raw SQL

### 4. Authentication: JWT

**Decision**: Use JWT instead of session-based authentication

**Rationale**:
- **Stateless**: No server-side session storage
- **Scalability**: Easy horizontal scaling
- **Security**: Secure token-based authentication
- **Performance**: No database lookups for validation
- **Standards**: Industry standard

**Trade-offs**:
- **Revocation**: Difficult to revoke tokens
- **Size**: Larger than session IDs
- **Security**: Token exposure risk

### 5. Architecture: Layered

**Decision**: Use layered architecture instead of microservices

**Rationale**:
- **Simplicity**: Simpler than microservices
- **Development**: Easier development and testing
- **Deployment**: Single deployment unit
- **Performance**: No network overhead
- **Consistency**: Easier data consistency

**Trade-offs**:
- **Scalability**: Less scalable than microservices
- **Technology**: Single technology stack
- **Independence**: Less service independence

## Performance Considerations

### 1. Database Performance

#### Indexing Strategy
```sql
-- User table indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Expense table indexes
CREATE INDEX idx_expenses_user_id ON expenses(user_id);
CREATE INDEX idx_expenses_date ON expenses(expense_date);
CREATE INDEX idx_expenses_category ON expenses(category_id);
CREATE INDEX idx_expenses_user_date ON expenses(user_id, expense_date);

-- Category table indexes
CREATE INDEX idx_categories_user_id ON categories(user_id);
CREATE INDEX idx_categories_name ON categories(name);
```

#### Query Optimization
- **Selective Queries**: Only select needed columns
- **Efficient Joins**: Optimize join operations
- **Pagination**: Implement proper pagination
- **Caching**: Cache frequently accessed data

### 2. Application Performance

#### Connection Pooling
```python
# Database connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600
)
```

#### Caching Strategy
- **User Data**: Cache user information
- **Categories**: Cache system categories
- **Statistics**: Cache computed statistics
- **TTL**: Appropriate time-to-live values

### 3. API Performance

#### Response Optimization
- **Compression**: Enable gzip compression
- **Pagination**: Implement efficient pagination
- **Filtering**: Efficient filtering and sorting
- **Caching**: HTTP caching headers

#### Request Optimization
- **Validation**: Early request validation
- **Serialization**: Efficient JSON serialization
- **Middleware**: Minimal middleware overhead
- **Async**: Future async implementation

## Monitoring and Observability

### 1. Logging Strategy

#### Structured Logging
```python
# JSON structured logging
logger.info(
    "User created expense",
    user_id=user.id,
    expense_id=expense.id,
    amount=expense.amount,
    category_id=expense.category_id
)
```

#### Log Levels
- **DEBUG**: Detailed information for debugging
- **INFO**: General information about operations
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failed operations
- **CRITICAL**: Critical errors requiring immediate attention

#### Log Destinations
- **Console**: Development and debugging
- **File**: Production logging
- **Centralized**: Future log aggregation

### 2. Metrics Collection

#### Application Metrics
- **Request Count**: Number of requests per endpoint
- **Response Time**: Average response time
- **Error Rate**: Percentage of failed requests
- **Active Users**: Number of active users

#### System Metrics
- **CPU Usage**: CPU utilization
- **Memory Usage**: Memory consumption
- **Disk Usage**: Disk space usage
- **Network I/O**: Network traffic

#### Database Metrics
- **Connection Count**: Active database connections
- **Query Time**: Average query execution time
- **Slow Queries**: Queries taking too long
- **Lock Waits**: Database lock contention

### 3. Health Checks

#### Application Health
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

#### Database Health
```python
@app.get("/health/db")
async def database_health():
    # Check database connection
    # Return health status
    pass
```

#### Dependency Health
```python
@app.get("/health/deps")
async def dependencies_health():
    # Check external dependencies
    # Return health status
    pass
```

### 4. Alerting

#### Error Alerts
- **High Error Rate**: Alert when error rate exceeds threshold
- **Critical Errors**: Alert on critical errors
- **Database Errors**: Alert on database issues
- **Authentication Failures**: Alert on auth failures

#### Performance Alerts
- **High Response Time**: Alert when response time is high
- **High CPU Usage**: Alert when CPU usage is high
- **High Memory Usage**: Alert when memory usage is high
- **Database Slow Queries**: Alert on slow queries

## Future Enhancements

### 1. Microservices Architecture

#### Service Decomposition
- **User Service**: User management
- **Expense Service**: Expense management
- **Category Service**: Category management
- **Analytics Service**: Analytics and reporting
- **Notification Service**: Notifications

#### Communication
- **API Gateway**: Single entry point
- **Service Discovery**: Service registration
- **Load Balancing**: Request distribution
- **Circuit Breaker**: Fault tolerance

### 2. Caching Layer

#### Redis Integration
- **Session Storage**: User sessions
- **Data Caching**: Frequently accessed data
- **Rate Limiting**: Request rate limiting
- **Pub/Sub**: Event messaging

#### Cache Strategy
- **Write-Through**: Write to cache and database
- **Write-Behind**: Write to cache, async to database
- **Cache-Aside**: Application manages cache
- **TTL**: Time-to-live for cache entries

### 3. Event-Driven Architecture

#### Event Sourcing
- **Event Store**: Store all events
- **Event Replay**: Replay events for state
- **CQRS**: Command Query Responsibility Segregation
- **Saga Pattern**: Distributed transactions

#### Message Queues
- **RabbitMQ**: Message broker
- **Apache Kafka**: Event streaming
- **AWS SQS**: Managed message queue
- **Google Pub/Sub**: Cloud messaging

### 4. Advanced Security

#### OAuth 2.0 / OpenID Connect
- **Third-party Authentication**: Google, GitHub, etc.
- **Authorization Server**: Centralized auth
- **Scope-based Access**: Fine-grained permissions
- **Token Refresh**: Automatic token renewal

#### API Security
- **Rate Limiting**: Request rate limiting
- **API Keys**: API key authentication
- **OAuth Scopes**: Permission-based access
- **Audit Logging**: Security event logging

## Conclusion

The Expense Tracker application follows modern architectural patterns and best practices to provide a scalable, maintainable, and secure solution for expense management. The layered architecture ensures clear separation of concerns, while the use of modern technologies like FastAPI and PostgreSQL provides excellent performance and reliability.

The system is designed to be easily extensible and can be enhanced with additional features like caching, microservices, and advanced security as requirements grow. The comprehensive logging and monitoring capabilities ensure that the system can be effectively maintained and debugged in production environments.
