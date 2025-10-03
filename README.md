# Expense Tracker API

A comprehensive RESTful Expense Tracker API built with FastAPI, PostgreSQL, and modern Python practices. This application provides secure expense management with advanced analytics, category management, and user authentication.

## 🚀 Features

### Core Functionality
- **🔐 JWT Authentication** - Secure user authentication with 24-hour token expiry
- **💰 Expense Management** - Full CRUD operations for expense tracking
- **📂 Category Management** - User-defined and system categories with color coding
- **📊 Analytics & Reporting** - Monthly summaries, category statistics, and trends
- **🔄 Recurring Expenses** - Support for daily, weekly, monthly, and yearly recurring expenses
- **🌍 Multi-Currency** - Support for USD, EUR, GBP, JPY, CAD, and AUD

### Security & Quality
- **🛡️ Security** - Password hashing with bcrypt, input validation, and SQL injection prevention
- **✅ Testing** - Comprehensive test suite with 90%+ coverage
- **📚 Documentation** - Auto-generated OpenAPI documentation
- **🔍 Logging** - Structured JSON logging with correlation IDs
- **⚡ Performance** - Optimized queries and connection pooling

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL 12+
- **ORM**: SQLAlchemy 2.0+
- **Migrations**: Alembic
- **Authentication**: JWT (PyJWT, bcrypt)
- **Validation**: Pydantic 2.0+

### Development & Testing
- **Testing**: pytest, pytest-asyncio, coverage tools
- **Code Quality**: Black, isort, flake8, mypy
- **Logging**: structlog, python-json-logger
- **File Validation**: python-magic

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.10 or higher
- **PostgreSQL**: 12 or higher
- **Git**: For cloning the repository

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Expense-Tracker
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # Install main dependencies
   pip install -r requirements/requirements.txt
   
   # Install development dependencies (optional)
   pip install -r requirements/dev.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your database credentials and secret key
   ```

5. **Set up database**
   ```bash
   # Create PostgreSQL database
   createdb expense_tracker
   
   # Run database migrations
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   python run_server.py
   ```

The API will be available at `http://localhost:8000`

### 📚 API Documentation

Once the server is running, access the interactive documentation:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI Spec**: http://localhost:8000/api/v1/openapi.json

## 📡 API Endpoints

### 🔐 Authentication
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/auth/register` | Register new user | ❌ |
| `POST` | `/api/v1/auth/login` | Login user | ❌ |
| `GET` | `/api/v1/auth/me` | Get current user profile | ✅ |
| `POST` | `/api/v1/auth/change-password` | Change password | ✅ |

### 💰 Expenses
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/expenses/` | Create expense | ✅ |
| `GET` | `/api/v1/expenses/` | List expenses (with filtering) | ✅ |
| `GET` | `/api/v1/expenses/{id}` | Get expense by ID | ✅ |
| `PUT` | `/api/v1/expenses/{id}` | Update expense | ✅ |
| `DELETE` | `/api/v1/expenses/{id}` | Delete expense | ✅ |
| `GET` | `/api/v1/expenses/monthly/{year}/{month}` | Get monthly expenses | ✅ |

### 📂 Categories
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/categories/` | Create category | ✅ |
| `GET` | `/api/v1/categories/` | List user categories | ✅ |
| `GET` | `/api/v1/categories/{id}` | Get category by ID | ✅ |
| `PUT` | `/api/v1/categories/{id}` | Update category | ✅ |
| `DELETE` | `/api/v1/categories/{id}` | Delete category | ✅ |
| `POST` | `/api/v1/categories/init-system-categories` | Initialize system categories | ✅ (Admin) |

### 📊 Analytics
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/v1/analytics/stats` | Get expense statistics | ✅ |
| `GET` | `/api/v1/analytics/category-stats` | Get category statistics | ✅ |
| `GET` | `/api/v1/analytics/monthly/{year}/{month}` | Get monthly analytics | ✅ |

### 🏥 System
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/health` | Health check | ❌ |
| `GET` | `/` | Root endpoint | ❌ |

## 🛠️ Development

### 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/api/test_main.py

# Run tests by category
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m auth          # Authentication tests only

# Run with coverage and fail if below threshold
pytest --cov=src --cov-fail-under=90
```

### 🔧 Code Quality

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Lint code
flake8 src tests

# Type checking
mypy src

# Run all quality checks
black src tests && isort src tests && flake8 src tests && mypy src
```

### 🗄️ Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check migration status
alembic current

# Show migration history
alembic history
```

### 🚀 Running the Server

```bash
# Development server (with auto-reload)
python run_server.py

# Production server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# With specific log level
uvicorn src.api.main:app --log-level debug
```

## 📁 Project Structure

```
Expense-Tracker/
├── 📁 src/                           # Source code
│   ├── 📁 api/                       # FastAPI routers
│   │   ├── 📁 authentication/        # Auth endpoints
│   │   ├── 📁 category/              # Category endpoints
│   │   ├── 📁 expense/               # Expense endpoints
│   │   ├── 📁 user/                  # User & analytics endpoints
│   │   └── main.py                   # Main FastAPI application
│   ├── 📁 core/                      # Core configuration
│   │   ├── config.py                 # Application settings
│   │   ├── database.py               # Database configuration
│   │   ├── dependencies.py           # FastAPI dependencies
│   │   ├── security.py               # Security utilities
│   │   ├── logging_config.py         # Logging configuration
│   │   └── middleware.py             # Custom middleware
│   ├── 📁 models/                    # SQLAlchemy models
│   │   ├── 📁 authentication/        # Auth models
│   │   ├── 📁 category/              # Category models
│   │   ├── 📁 expense/               # Expense models
│   │   └── 📁 user/                  # User models
│   ├── 📁 repositories/              # Data access layer
│   │   ├── 📁 authentication/        # Auth repositories
│   │   ├── 📁 category/              # Category repositories
│   │   ├── 📁 expense/               # Expense repositories
│   │   ├── 📁 user/                  # User repositories
│   │   └── async_base_repository.py  # Base repository
│   ├── 📁 schemas/                   # Pydantic schemas
│   │   ├── 📁 authentication/        # Auth schemas
│   │   ├── 📁 category/              # Category schemas
│   │   ├── 📁 expense/               # Expense schemas
│   │   └── 📁 user/                  # User schemas
│   ├── 📁 services/                  # Business logic layer
│   │   ├── 📁 authentication/        # Auth services
│   │   ├── 📁 category/              # Category services
│   │   ├── 📁 expense/               # Expense services
│   │   ├── 📁 user/                  # User services
│   │   └── async_base_service.py     # Base service
│   └── 📁 interfaces/                # Interface definitions
├── 📁 tests/                         # Test suite
│   ├── 📁 api/                       # API tests
│   ├── 📁 core/                      # Core tests
│   ├── 📁 models/                    # Model tests
│   ├── 📁 repositories/              # Repository tests
│   ├── 📁 schemas/                   # Schema tests
│   ├── 📁 services/                  # Service tests
│   └── conftest.py                   # Test fixtures
├── 📁 docs/                          # Documentation
│   ├── 📁 implementation/            # Implementation docs
│   ├── 📁 step1/                     # Planning docs
│   ├── 📁 testing/                   # Testing docs
│   └── README.md                     # Documentation index
├── 📁 alembic/                       # Database migrations
├── 📁 requirements/                  # Dependencies
├── 📁 logs/                          # Log files
├── run_server.py                     # Server entry point
├── run_tests.sh                      # Test runner script
├── pyproject.toml                    # Project configuration
├── pytest.ini                       # Pytest configuration
└── README.md                         # This file
```

## ⚙️ Configuration

The application uses environment variables for configuration. Copy `env.example` to `.env` and configure the following:

### Required Variables
```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/expense_tracker
DATABASE_URL_TEST=postgresql://username:password@localhost:5432/expense_tracker_test

# JWT Configuration
SECRET_KEY=your-secret-key-here-change-in-production  # Must be at least 32 characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
```

### Optional Variables
```bash
# Application Configuration
DEBUG=True
PROJECT_NAME=Expense Tracker API
VERSION=1.0.0
API_V1_STR=/api/v1

# CORS Configuration
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# Logging Configuration
LOG_LEVEL=INFO
ENABLE_JSON_LOGGING=True
LOG_FILE=logs/expense-tracker.log
```

## 📖 Documentation

Comprehensive documentation is available in the `docs/` folder:

- **[Architecture Guide](docs/step1/6_architecture.md)** - System architecture and design decisions
- **[Database Schema](docs/step1/5_database_schema.md)** - Database design and relationships
- **[API Reference](docs/testing/postman_guide.md)** - Complete API documentation
- **[Testing Guide](docs/testing/testing_guide.md)** - Testing instructions and examples
- **[Implementation Overview](docs/implementation/overview.md)** - Implementation details

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run the test suite**: `pytest --cov=src --cov-fail-under=90`
5. **Run code quality checks**: `black src tests && isort src tests && flake8 src tests && mypy src`
6. **Commit your changes**: `git commit -m 'Add amazing feature'`
7. **Push to the branch**: `git push origin feature/amazing-feature`
8. **Open a Pull Request**

### Development Guidelines
- Follow the existing code style (Black, isort)
- Write tests for new functionality
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- 📖 Check the [documentation](docs/)
- 🐛 Open an [issue](https://github.com/your-repo/Expense-Tracker/issues)
- 💬 Start a [discussion](https://github.com/your-repo/Expense-Tracker/discussions)

## 🎯 Roadmap

- [ ] Rate limiting and request throttling
- [ ] Redis caching for improved performance
- [ ] File upload support for expense receipts
- [ ] Email notifications for recurring expenses
- [ ] Advanced reporting and data export
- [ ] Mobile app integration
- [ ] Multi-tenant support
