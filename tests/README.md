# Expense Tracker API - Test Suite

This directory contains a comprehensive test suite for the Expense Tracker API backend application. The test suite is designed to achieve 100% code coverage and follows industry best practices for testing FastAPI applications.

## Test Structure

```
tests/
├── conftest.py                 # Pytest configuration and shared fixtures
├── unit/                       # Unit tests for individual components
│   ├── test_auth.py           # Authentication service tests
│   ├── test_category.py       # Category service tests
│   ├── test_config.py         # Configuration module tests
│   ├── test_exceptions.py     # Custom exceptions tests
│   ├── test_expense.py        # Expense service tests
│   ├── test_logging.py        # Logging configuration tests
│   ├── test_models.py         # Database model tests
│   ├── test_security.py       # Security utilities tests
│   ├── test_user.py           # User service tests
│   └── test_api.py            # API endpoint tests
├── integration/               # Integration tests for complete workflows
│   └── test_integration.py    # End-to-end workflow tests
└── README.md                  # This file
```

## Test Coverage

The test suite covers:

### Core Modules (100% Coverage)
- **Configuration Management**: Settings validation, environment variable handling
- **Exception Handling**: Custom exceptions, error propagation, HTTP status codes
- **Logging System**: Structured logging, log levels, formatters
- **Security Utilities**: Password hashing, JWT token management, authentication

### Business Logic (100% Coverage)
- **User Management**: Registration, authentication, profile management, password changes
- **Category Management**: CRUD operations, system categories, user isolation
- **Expense Management**: CRUD operations, filtering, reporting, analytics
- **Authentication Services**: Password verification, token generation, user validation

### API Layer (100% Coverage)
- **Authentication Endpoints**: Register, login, profile management
- **Category Endpoints**: CRUD operations, user-specific categories
- **Expense Endpoints**: CRUD operations, filtering, search
- **Analytics Endpoints**: Summary, breakdowns, trends, reporting

### Database Layer (100% Coverage)
- **Model Classes**: User, Category, Expense models with relationships
- **Repository Pattern**: Data access layer with proper error handling
- **Database Operations**: CRUD operations, transactions, constraints

## Running Tests

### Prerequisites

Ensure you have the required dependencies installed:

```bash
pip install -r requirements/dev.txt
```

### Basic Test Execution

Run all tests:
```bash
python -m pytest tests/
```

Run unit tests only:
```bash
python -m pytest tests/unit/
```

Run integration tests only:
```bash
python -m pytest tests/integration/
```

### Test Execution with Coverage

Generate coverage report:
```bash
python -m pytest --cov=src --cov-report=html --cov-report=term-missing tests/
```

This will:
- Run all tests
- Generate HTML coverage report in `htmlcov/` directory
- Display terminal coverage report with missing lines
- Fail if coverage is below 80% (configurable in `pytest.ini`)

### Using the Test Runner Script

The project includes a convenient test runner script:

```bash
# Run all tests
python run_tests.py all

# Run unit tests only
python run_tests.py unit

# Run integration tests only
python run_tests.py integration

# Run tests with coverage report
python run_tests.py coverage

# Run tests in verbose mode
python run_tests.py all --verbose
```

### Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.slow`: Slow-running tests

Run tests by marker:
```bash
# Run only unit tests
python -m pytest -m unit

# Run only integration tests
python -m pytest -m integration

# Skip slow tests
python -m pytest -m "not slow"
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
asyncio_mode = auto
pythonpath = .
```

### Test Database

Tests use an in-memory SQLite database to ensure:
- Fast test execution
- No external dependencies
- Complete isolation between tests
- Automatic cleanup after each test

## Fixtures and Test Data

### Core Fixtures (`conftest.py`)

- **Database Fixtures**: `db_session`, `test_db` - Database setup and teardown
- **Client Fixtures**: `client` - FastAPI test client with database override
- **Mock Fixtures**: `mock_settings`, `mock_repository`, `mock_logger` - Mocked dependencies
- **Data Fixtures**: `sample_user`, `sample_category`, `sample_expense` - Test data
- **Authentication Fixtures**: `auth_headers` - Pre-configured authentication headers

### Test Data Factories

The `TestDataFactory` class provides methods for creating test data:

```python
factory = TestDataFactory()

# Create user data with overrides
user_data = factory.create_user_data(email="custom@example.com")

# Create category data with overrides
category_data = factory.create_category_data(name="Custom Category")

# Create expense data with overrides
expense_data = factory.create_expense_data(amount=Decimal("200.00"))
```

## Test Patterns and Best Practices

### Arrange-Act-Assert Pattern

All tests follow the AAA pattern:

```python
def test_create_user_success(self, user_service, sample_user_create):
    # Arrange
    mock_user = User(id=1, email=sample_user_create.email)
    user_service.user_repo.create.return_value = mock_user

    # Act
    result = user_service.create_user(sample_user_create)

    # Assert
    assert result == mock_user
    user_service.user_repo.create.assert_called_once()
```

### Comprehensive Error Testing

Each test covers:
- **Happy Path**: Normal successful execution
- **Error Cases**: Validation errors, database errors, business logic errors
- **Edge Cases**: Boundary conditions, empty inputs, invalid data
- **Exception Handling**: Proper error propagation and HTTP status codes

### Mocking Strategy

- **External Dependencies**: Database, external APIs, file system
- **Service Dependencies**: Cross-service calls, authentication
- **Time-dependent Code**: JWT token expiration, timestamps
- **Random/Unpredictable Code**: Password hashing, UUID generation

### Test Isolation

- Each test is completely isolated
- Database transactions are rolled back after each test
- Mock objects are reset between tests
- No shared state between tests

## Coverage Reports

### HTML Coverage Report

After running tests with coverage, open `htmlcov/index.html` in your browser to view:
- Overall coverage percentage
- File-by-file coverage details
- Line-by-line coverage highlighting
- Missing line identification

### Terminal Coverage Report

The terminal output shows:
- Overall coverage percentage
- Per-file coverage percentages
- Missing lines for each file
- Coverage threshold compliance

### Coverage Thresholds

- **Minimum Coverage**: 80% (configurable in `pytest.ini`)
- **Target Coverage**: 100% for all modules
- **Critical Modules**: 100% coverage required (auth, security, core)

## Continuous Integration

### GitHub Actions Integration

The test suite is designed to work seamlessly with CI/CD pipelines:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements/dev.txt
      - name: Run tests with coverage
        run: python run_tests.py coverage
```

### Pre-commit Hooks

Configure pre-commit hooks to run tests before commits:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: python -m pytest tests/unit/
        language: system
        pass_filenames: false
        always_run: true
```

## Debugging Tests

### Running Specific Tests

```bash
# Run specific test file
python -m pytest tests/unit/test_user.py

# Run specific test method
python -m pytest tests/unit/test_user.py::TestUserService::test_create_user_success

# Run tests matching pattern
python -m pytest -k "test_create_user"
```

### Debug Mode

```bash
# Run tests with debug output
python -m pytest -v -s tests/

# Run tests with pdb debugger
python -m pytest --pdb tests/

# Run tests with detailed output
python -m pytest -vvv tests/
```

### Test Discovery

```bash
# List all tests without running them
python -m pytest --collect-only tests/

# Show test collection errors
python -m pytest --collect-only -v tests/
```

## Extending the Test Suite

### Adding New Tests

1. **Unit Tests**: Add to appropriate `test_*.py` file in `tests/unit/`
2. **Integration Tests**: Add to `test_integration.py` in `tests/integration/`
3. **New Modules**: Create new test file following naming convention

### Test File Template

```python
"""
Unit tests for [module_name].
"""

import pytest
from unittest.mock import MagicMock, patch

from src.module.module_name import ModuleClass


class TestModuleClass:
    """Test cases for ModuleClass."""

    def test_method_success(self):
        """Test successful method execution."""
        # Arrange
        # Act
        # Assert
        pass

    def test_method_error_case(self):
        """Test method error handling."""
        # Arrange
        # Act
        # Assert
        pass
```

### Adding New Fixtures

Add to `conftest.py`:

```python
@pytest.fixture
def new_fixture():
    """Description of the fixture."""
    # Setup code
    yield fixture_value
    # Cleanup code
```

## Performance Testing

### Load Testing

For performance testing, consider adding:

```python
import time
import pytest

@pytest.mark.slow
def test_api_performance(client, auth_headers):
    """Test API response times."""
    start_time = time.time()
    
    response = client.get("/api/v1/expenses/", headers=auth_headers)
    
    end_time = time.time()
    response_time = end_time - start_time
    
    assert response.status_code == 200
    assert response_time < 1.0  # Should respond within 1 second
```

### Memory Testing

```python
import psutil
import pytest

@pytest.mark.slow
def test_memory_usage(client, auth_headers):
    """Test memory usage during operations."""
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    # Perform operations
    for _ in range(100):
        client.get("/api/v1/expenses/", headers=auth_headers)
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    assert memory_increase < 50 * 1024 * 1024  # Less than 50MB increase
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src` is in Python path
2. **Database Errors**: Check database URL configuration
3. **Mock Issues**: Verify mock setup and return values
4. **Coverage Issues**: Check that all code paths are tested

### Test Failures

1. **Check Test Output**: Look for specific error messages
2. **Verify Mocks**: Ensure mocks are properly configured
3. **Check Dependencies**: Verify all required packages are installed
4. **Database State**: Ensure database is properly reset between tests

### Performance Issues

1. **Slow Tests**: Use `@pytest.mark.slow` for time-consuming tests
2. **Memory Leaks**: Check for proper cleanup in fixtures
3. **Database Queries**: Optimize database operations in tests

## Contributing

When adding new features:

1. **Write Tests First**: Follow TDD principles
2. **Maintain Coverage**: Ensure 100% coverage for new code
3. **Update Documentation**: Keep this README updated
4. **Follow Patterns**: Use established test patterns and fixtures
5. **Review Tests**: Have tests reviewed along with code

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
