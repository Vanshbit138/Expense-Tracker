# Testing Guide

This document provides comprehensive information about testing the Expense Tracker API.

## Overview

The Expense Tracker API includes a comprehensive test suite designed to ensure high code coverage, reliability, and maintainability. The test suite follows industry best practices and provides complete isolation from external dependencies.

## Test Suite Structure

```
tests/
├── conftest.py                 # Common fixtures and configuration
├── unit/                       # Unit tests for individual components
│   ├── auth/                   # Authentication tests
│   ├── user/                   # User service tests
│   ├── category/               # Category service tests
│   ├── expense/                # Expense service tests
│   ├── analytics/              # Analytics tests
│   ├── core/                   # Core module tests
│   ├── api/                    # API endpoint tests
│   └── validation/             # Validation tests
├── integration/                # Integration tests
└── README.md                   # Test suite documentation
```

## Running Tests

### Prerequisites

Install the required dependencies:

```bash
pip install -r requirements/requirements.txt
pip install -r requirements/dev.txt
```

### Basic Commands

Run all tests:

```bash
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

Run specific test files:

```bash
pytest tests/unit/auth/test_auth.py
pytest tests/unit/user/test_user_service.py
```

Run tests by category:

```bash
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m slow          # Slow tests only
```

### Coverage Reports

Generate coverage report:

```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

This command will:
- Generate an HTML coverage report in `htmlcov/`
- Display terminal coverage report with missing lines
- Show overall coverage percentage

View HTML coverage report:

```bash
# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html

# Windows
start htmlcov/index.html
```

### Coverage Configuration

The test suite is configured to:
- Cover the `src/` directory
- Require minimum 80% coverage (configurable in `pytest.ini`)
- Generate both HTML and terminal reports
- Show missing line coverage

## Test Categories

### Unit Tests

Unit tests focus on testing individual components in isolation:

#### Authentication Tests (`tests/unit/auth/`)
- JWT token creation and verification
- Password hashing and verification
- Authentication dependencies
- API endpoint authentication

#### User Service Tests (`tests/unit/user/`)
- User CRUD operations
- User validation and uniqueness checks
- Password change functionality
- User authentication logic

#### Category Service Tests (`tests/unit/category/`)
- Category CRUD operations
- Category access control
- Category validation
- System category creation

#### Expense Service Tests (`tests/unit/expense/`)
- Expense CRUD operations
- Expense validation
- Analytics and statistics
- Category access validation

#### Core Module Tests (`tests/unit/core/`)
- Configuration validation
- Security functions
- Logging configuration
- Database utilities

#### API Tests (`tests/unit/api/`)
- FastAPI application setup
- Error handling
- Middleware configuration
- Router inclusion

#### Validation Tests (`tests/unit/validation/`)
- Input validation
- Schema validation
- Query parameter validation
- Data type validation

### Integration Tests

Integration tests verify complete workflows:

#### API Integration Tests (`tests/integration/`)
- Complete authentication flows
- CRUD operation workflows
- Error handling scenarios
- CORS and middleware testing

## Test Isolation

### Mocking Strategy

All tests are fully isolated and do not require external dependencies:

- **Database**: All database operations are mocked
- **Network**: No network calls are made
- **External Services**: All external services are mocked
- **Environment**: Test-specific environment variables

### Fixtures

The test suite provides comprehensive fixtures:

- **Mock Objects**: Pre-configured mocks for all components
- **Test Data**: Sample data for testing
- **Settings**: Test-specific configuration
- **Authentication**: Mock JWT tokens and users

## Test Data

### Sample Data

The test suite includes fixtures for common test data:

- **User Data**: Registration and login data
- **Category Data**: Category creation and update data
- **Expense Data**: Expense creation and update data
- **Authentication Data**: JWT tokens and credentials

### Data Validation

All test data is validated against actual schemas to ensure consistency and correctness.

## Error Testing

### Exception Handling

The test suite thoroughly tests error handling:

- **HTTP Exceptions**: All HTTP status codes
- **Validation Errors**: Input validation failures
- **Database Errors**: Database operation failures
- **Authentication Errors**: Auth and authorization failures
- **Service Errors**: Business logic errors

### Edge Cases

Edge cases are tested to ensure robustness:

- **Boundary Values**: Min/max values
- **Empty Data**: Empty strings, null values
- **Invalid Data**: Malformed input
- **Concurrent Access**: Race conditions

## Performance

### Test Performance

The test suite is optimized for performance:

- **Fast Execution**: All tests run quickly
- **Parallel Execution**: Tests can run in parallel
- **Minimal Setup**: Lightweight test setup
- **Efficient Mocking**: Lightweight mock objects

### Load Testing

For load testing, consider additional tools:

- **Locust**: API load testing
- **pytest-benchmark**: Performance benchmarking
- **Custom Load Tests**: Application-specific testing

## Continuous Integration

### CI/CD Integration

The test suite is designed for CI/CD:

- **Exit Codes**: Proper exit codes for CI systems
- **Coverage Thresholds**: Configurable coverage requirements
- **Test Reports**: Machine-readable reports
- **Parallel Execution**: Support for parallel testing

### GitHub Actions Example

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
          python-version: 3.10
      - name: Install dependencies
        run: |
          pip install -r requirements/requirements.txt
          pip install -r requirements/dev.txt
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src/` is in Python path
2. **Mock Failures**: Check external dependencies are mocked
3. **Coverage Issues**: Verify all code paths are covered
4. **Test Failures**: Check test data matches schemas

### Debugging

Enable debug output:

```bash
pytest -v -s --tb=long
```

Run specific test with debug:

```bash
pytest -v -s tests/unit/auth/test_auth.py::TestJWTService::test_create_access_token_success
```

### Test Maintenance

Regular maintenance tasks:

- **Update Mocks**: Keep mocks in sync with implementations
- **Review Coverage**: Regularly review and improve coverage
- **Refactor Tests**: Maintain test readability
- **Update Data**: Update test data for schema changes

## Best Practices

### Writing Tests

1. **Test One Thing**: Each test verifies one behavior
2. **Clear Names**: Use descriptive test method names
3. **Arrange-Act-Assert**: Follow AAA pattern consistently
4. **Independent Tests**: Tests should not depend on each other
5. **Fast Tests**: Keep tests fast and lightweight

### Mocking

1. **Mock External Dependencies**: Mock all external services
2. **Verify Interactions**: Verify mocked methods are called correctly
3. **Realistic Mocks**: Use realistic mock data and behavior
4. **Minimal Mocking**: Only mock what's necessary

### Coverage

1. **Aim for High Coverage**: Target 90%+ code coverage
2. **Test Edge Cases**: Include boundary condition tests
3. **Test Error Paths**: Test all error conditions
4. **Review Coverage Reports**: Regularly review coverage

## Contributing

### Adding New Tests

When adding new tests:

1. **Follow Naming Conventions**: Use descriptive test names
2. **Add to Appropriate Category**: Place tests in correct directory
3. **Update Fixtures**: Add new fixtures if needed
4. **Document Changes**: Update this guide if needed

### Test Review

When reviewing tests:

1. **Check Coverage**: Ensure new code is covered
2. **Verify Isolation**: Ensure tests don't depend on external resources
3. **Check Performance**: Ensure tests run quickly
4. **Review Clarity**: Ensure tests are clear and maintainable

## Test Configuration

### pytest.ini

The test configuration is defined in `pytest.ini`:

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

### Coverage Configuration

Coverage is configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=90",
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow tests",
]
```

## Summary

The Expense Tracker API test suite provides:

- **Comprehensive Coverage**: 90%+ code coverage
- **Complete Isolation**: No external dependencies
- **Fast Execution**: Quick test runs
- **Easy Maintenance**: Well-organized and documented
- **CI/CD Ready**: Designed for continuous integration
- **High Quality**: Follows industry best practices

This test suite ensures the reliability and maintainability of the Expense Tracker API while providing confidence in code changes and deployments.
