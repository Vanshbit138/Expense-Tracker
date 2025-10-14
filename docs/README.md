# Expense Tracker API Documentation

Complete documentation for the Expense Tracker API implementation, covering all features, architecture, deployment, and testing.

## 📚 Documentation Overview

This documentation provides comprehensive coverage of the Expense Tracker API, from quick start guides to detailed technical specifications.

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended)
```bash
# Clone repository
git clone <repository-url>
cd Expense-Tracker

# Start with Docker Compose
docker-compose up --build -d

# Check health
curl http://localhost:8000/health
```

### Option 2: Local Development
```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
nano .env

# Install dependencies
pip install -r requirements/requirements.txt

# Start server
python run_server.py
```

### Access Documentation
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI Spec**: http://localhost:8000/api/v1/openapi.json

## 📖 Documentation Structure

### 🏗️ Architecture & Design
- **[Architecture Guide](architecture.md)** - Complete system architecture and design decisions
- **[Database Schema](step1/5_database_schema.md)** - Database design and relationships
- **[Implementation Overview](implementation/overview.md)** - Implementation details and patterns

### 🔧 Configuration & Setup
- **[Configuration Guide](configuration_guide.md)** - Detailed configuration instructions
- **[Deployment Guide](deployment_guide.md)** - Production deployment instructions
- **[Docker Documentation](docker/)** - Complete Docker deployment guide
- **[Testing Guide](testing/testing_guide.md)** - Testing framework and examples

### 📡 API Reference
- **[API Reference](api_reference.md)** - Complete API documentation with examples
- **[Postman Collection](testing/postman_collection.json)** - Ready-to-use API testing
- **[Postman Guide](testing/postman_guide.md)** - Step-by-step testing guide

### 📋 Project Management
- **[Changelog](changelog.md)** - Version history and release notes
- **[Planning Documents](step1/)** - Project planning and design documents

## 🎯 Key Features

### 🔐 Security
- **JWT Authentication** - Secure token-based authentication
- **Password Hashing** - bcrypt with salt for password security
- **Input Validation** - Comprehensive request validation
- **CORS Configuration** - Controlled cross-origin access
- **SQL Injection Prevention** - ORM-based protection

### 📊 Logging System
- **Structured JSON Logging** - Machine-readable log format
- **Dynamic Log Levels** - Configurable logging levels
- **Request Correlation IDs** - Track requests across components
- **Performance Metrics** - Request timing and performance data
- **File and Console Logging** - Multiple log destinations

### 🚀 API Endpoints
- **Authentication** - User registration, login, password management
- **Expenses** - Complete CRUD operations for expense tracking
- **Categories** - User-defined and system categories
- **Analytics** - Statistics, reporting, and insights
- **System** - Health checks and system information

### 🧪 Testing
- **Comprehensive Test Suite** - 90%+ test coverage
- **Unit Tests** - Individual component testing
- **Integration Tests** - API endpoint testing
- **Mock-based Testing** - Isolated testing environment
- **Postman Collection** - Ready-to-use API testing

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **PostgreSQL** - Robust relational database
- **SQLAlchemy** - Python ORM
- **Alembic** - Database migrations
- **Pydantic** - Data validation

### Development
- **pytest** - Testing framework
- **Black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **mypy** - Type checking

### Infrastructure
- **Docker** - Containerization with multi-stage builds
- **Docker Compose** - Multi-service orchestration
- **PostgreSQL** - Containerized database
- **Nginx** - Reverse proxy and load balancing
- **systemd** - Service management
- **Cron** - Scheduled tasks

## 📁 File Structure

```
docs/
├── 📄 README.md                    # This file
├── 📄 architecture.md              # System architecture
├── 📄 api_reference.md             # Complete API documentation
├── 📄 configuration_guide.md       # Configuration instructions
├── 📄 deployment_guide.md          # Deployment instructions
├── 📄 changelog.md                 # Version history
├── 📁 docker/                      # Docker documentation
│   ├── README.md                   # Docker overview
│   ├── docker_guide.md             # Complete Docker guide
│   ├── troubleshooting.md          # Docker troubleshooting
│   ├── production.md               # Production deployment
│   └── commands.md                 # Docker commands reference
├── 📁 implementation/              # Implementation details
│   ├── overview.md
│   └── logging/
│       └── implementation.md
├── 📁 step1/                       # Planning documents
│   ├── 1_planning.md
│   ├── 2_design.md
│   ├── 3_user_stories.md
│   ├── 4_api_endpoints_overview.md
│   ├── 5_database_schema.md
│   └── 6_architecture.md
└── 📁 testing/                     # Testing documentation
    ├── postman_collection.json
    ├── postman_guide.md
    ├── testing_guide.md
    └── api_testing_results.md
```

## 🚀 Getting Started

### For Developers
1. Read the [Architecture Guide](architecture.md) to understand the system
2. Follow the [Configuration Guide](configuration_guide.md) for setup
3. Use the [API Reference](api_reference.md) for development
4. Check the [Testing Guide](testing/testing_guide.md) for testing

### For DevOps
1. Review the [Docker Documentation](docker/) for containerized deployment
2. Check the [Deployment Guide](deployment_guide.md) for production setup
3. Use the [Configuration Guide](configuration_guide.md) for environment setup
4. Follow the [Architecture Guide](architecture.md) for infrastructure planning

### For API Users
1. Start with the [API Reference](api_reference.md) for endpoint documentation
2. Use the [Postman Collection](testing/postman_collection.json) for testing
3. Follow the [Postman Guide](testing/postman_guide.md) for step-by-step testing

## 🔧 Configuration

### Environment Variables
```bash
# Required
DATABASE_URL=postgresql://user:pass@localhost:5432/expense_tracker
SECRET_KEY=your-secret-key-here

# Optional
DEBUG=False
LOG_LEVEL=INFO
ENABLE_JSON_LOGGING=True
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

### Logging Configuration
```bash
LOG_LEVEL=DEBUG          # DEBUG, INFO, WARNING, ERROR, CRITICAL
ENABLE_JSON_LOGGING=True # True for JSON, False for console
LOG_FILE=logs/expense-tracker.log
```

## 🧪 Testing

### Run Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific test categories
pytest -m unit          # Unit tests
pytest -m integration   # Integration tests
pytest -m auth          # Authentication tests
```

### API Testing
- Import `docs/testing/postman_collection.json` into Postman
- Follow `docs/testing/postman_guide.md` for testing steps
- Check `docs/testing/api_testing_results.md` for test results

## 📊 Monitoring

### Health Checks
- **Application**: `GET /health`
- **Database**: Check connection status
- **Dependencies**: Verify external services

### Logging
- **Structured Logs**: JSON format for easy parsing
- **Correlation IDs**: Track requests across components
- **Performance Metrics**: Request timing and performance data
- **Error Tracking**: Comprehensive error logging

## 🤝 Contributing

1. Read the [Architecture Guide](architecture.md) to understand the system
2. Follow the [Configuration Guide](configuration_guide.md) for development setup
3. Use the [Testing Guide](testing/testing_guide.md) for testing
4. Check the [Changelog](changelog.md) for version history

## 📞 Support

For questions or issues:
- 📖 Check this documentation
- 🐛 Open an [issue](https://github.com/your-repo/Expense-Tracker/issues)
- 💬 Start a [discussion](https://github.com/your-repo/Expense-Tracker/discussions)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
