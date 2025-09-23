# Expense Tracker API

A RESTful Expense Tracker API built with FastAPI, PostgreSQL, and modern Python practices.

## Features

-  **JWT Authentication** - Secure user authentication with 24-hour token expiry
-  **Expense Management** - Full CRUD operations for expense tracking
-  **Category Management** - User-defined and system categories
-  **Analytics & Reporting** - Monthly summaries, category statistics, and trends
-  **Security** - Password hashing with bcrypt, input validation, and SQL injection prevention
-  **Testing** - Comprehensive test suite with 90%+ coverage
-  **Documentation** - Auto-generated OpenAPI documentation

## Tech Stack

- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT (PyJWT, bcrypt)
- **Validation**: Pydantic
- **Testing**: pytest, pytest-asyncio, coverage tools

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 12+
- pip or poetry

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Expense-Tracker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/requirements.txt
   pip install -r requirements/dev.txt  # For development
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your database credentials
   ```

5. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb expense_tracker
   
   # Run migrations
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   python run_server.py
   ```

The API will be available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user profile
- `PUT /api/v1/auth/me` - Update user profile
- `POST /api/v1/auth/change-password` - Change password

### Expenses
- `POST /api/v1/expenses/` - Create expense
- `GET /api/v1/expenses/` - List expenses (with filtering)
- `GET /api/v1/expenses/{id}` - Get expense by ID
- `PUT /api/v1/expenses/{id}` - Update expense
- `DELETE /api/v1/expenses/{id}` - Delete expense
- `GET /api/v1/expenses/monthly/{year}/{month}` - Monthly expenses

### Categories
- `POST /api/v1/categories/` - Create category
- `GET /api/v1/categories/` - List categories
- `GET /api/v1/categories/{id}` - Get category by ID
- `PUT /api/v1/categories/{id}` - Update category
- `DELETE /api/v1/categories/{id}` - Delete category

### Analytics
- `GET /api/v1/analytics/stats` - Expense statistics
- `GET /api/v1/analytics/category-stats` - Category statistics
- `GET /api/v1/analytics/monthly/{year}/{month}` - Monthly analytics

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

### Code Quality

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Lint code
flake8 src tests

# Type checking
mypy src
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Project Structure

```
Expense-Tracker/
├── src/
│   ├── api/                    # FastAPI routers
│   │   ├── main.py            # Main application
│   │   └── routers/           # API endpoints
│   ├── core/                  # Core configuration
│   │   ├── config.py          # Settings
│   │   ├── database.py        # Database setup
│   │   ├── dependencies.py    # FastAPI dependencies
│   │   └── security.py        # Security utilities
│   ├── models/                # SQLAlchemy models
│   ├── repositories/          # Data access layer
│   ├── schemas/               # Pydantic schemas
│   └── services/              # Business logic layer
├── tests/                     # Test suite
├── docs/                      # Documentation
├── alembic/                   # Database migrations
└── requirements/              # Dependencies
```

## Configuration

The application uses environment variables for configuration. See `env.example` for all available options:

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key
- `DEBUG` - Enable debug mode
- `CORS_ORIGINS` - Allowed CORS origins

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the repository.
