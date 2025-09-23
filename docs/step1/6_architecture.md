# Step 6: System Architecture

## High-Level Architecture

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

## Component Details

### API Layer (FastAPI Routers)
- **Authentication Router**: User registration, login, profile management
- **Expenses Router**: CRUD operations for expense management
- **Categories Router**: Category management and system categories
- **Analytics Router**: Reporting and statistical analysis

**Responsibilities:**
- HTTP request/response handling
- Input validation using Pydantic schemas
- Authentication and authorization
- Error handling and status codes
- API documentation generation

### Service Layer (Business Logic)
- **User Service**: User management, authentication, password handling
- **Expense Service**: Expense business logic, validation, analytics
- **Category Service**: Category management, system category handling

**Responsibilities:**
- Business rule enforcement
- Data validation and transformation
- Complex business operations
- Integration between different domains
- Error handling and logging

### Repository Layer (Data Access)
- **User Repository**: User data operations
- **Expense Repository**: Expense data operations and queries
- **Category Repository**: Category data operations

**Responsibilities:**
- Database operations (CRUD)
- Query optimization
- Data mapping between ORM and domain models
- Transaction management
- Database-specific logic

### Database Layer (PostgreSQL)
- **Users Table**: User account information
- **Categories Table**: Expense categories (user and system)
- **Expenses Table**: Expense records and metadata

**Responsibilities:**
- Data persistence
- ACID transaction support
- Data integrity enforcement
- Query performance optimization
- Backup and recovery

## Security Architecture

### Authentication Flow
```
1. User submits credentials → API Layer
2. Service Layer validates credentials → Database
3. JWT token generated → Client
4. Client includes token in subsequent requests
5. Middleware validates token → Service Layer
6. Authorized request processed → Database
```

### Security Measures
- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: 24-hour expiry with secure signing
- **Input Validation**: Pydantic schema validation
- **SQL Injection Prevention**: SQLAlchemy ORM
- **CORS Configuration**: Controlled cross-origin access
- **Rate Limiting**: (Future enhancement)

## Data Flow

### Create Expense Flow
```
1. Client → POST /api/v1/expenses/
2. API Router → Validate request schema
3. Service Layer → Business validation
4. Repository Layer → Database insert
5. Database → Return created record
6. Repository → Return domain model
7. Service → Return business object
8. API Router → Return JSON response
9. Client ← HTTP 201 Created
```

### Analytics Query Flow
```
1. Client → GET /api/v1/analytics/stats
2. API Router → Validate parameters
3. Service Layer → Build query parameters
4. Repository Layer → Execute analytics queries
5. Database → Return aggregated data
6. Repository → Return statistics
7. Service → Format analytics data
8. API Router → Return JSON response
9. Client ← HTTP 200 OK
```

## Scalability Considerations

### Horizontal Scaling
- **Stateless API**: JWT tokens enable load balancing
- **Database Connection Pooling**: Efficient connection management
- **Caching Layer**: (Future) Redis for frequently accessed data
- **Microservices**: (Future) Split into domain-specific services

### Vertical Scaling
- **Database Indexing**: Optimized for common query patterns
- **Query Optimization**: Efficient SQL generation
- **Memory Management**: Proper resource cleanup
- **Connection Pooling**: Configurable pool sizes

## Deployment Architecture

### Development Environment
```
┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │───▶│  PostgreSQL DB  │
│   (Local:8000)  │    │  (Local:5432)   │
└─────────────────┘    └─────────────────┘
```

### Production Environment
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   FastAPI App   │    │  PostgreSQL DB  │
│   (Nginx)       │───▶│   (Docker)      │───▶│   (Managed)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Monitoring and Logging

### Application Metrics
- Request/response times
- Error rates and types
- Database query performance
- Authentication success/failure rates

### Logging Strategy
- **Structured Logging**: JSON format for easy parsing
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Correlation IDs**: Track requests across components
- **Sensitive Data**: Mask passwords and tokens

### Health Checks
- **API Health**: `/health` endpoint
- **Database Health**: Connection and query validation
- **Dependency Health**: External service availability

## Error Handling Strategy

### Error Types
- **Validation Errors**: 400 Bad Request
- **Authentication Errors**: 401 Unauthorized
- **Authorization Errors**: 403 Forbidden
- **Not Found Errors**: 404 Not Found
- **Server Errors**: 500 Internal Server Error

### Error Response Format
```json
{
  "detail": "Error message",
  "type": "error_type",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Error Logging
- Log all errors with context
- Include user information (if available)
- Track error patterns and trends
- Alert on critical errors
