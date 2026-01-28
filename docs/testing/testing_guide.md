# Testing Guide for Expense Tracker

## Overview

This guide provides comprehensive instructions for running tests, generating coverage reports, and maintaining the test suite for the Expense Tracker application.

## Prerequisites

### Required Dependencies
```bash
# Install main dependencies
pip install -r requirements/requirements.txt

# Install testing dependencies
pip install pytest pytest-cov coverage pytest-xdist
```

### Optional Dependencies
```bash
# For parallel test execution
pip install pytest-xdist

# For test profiling
pip install pytest-benchmark

# For test reporting
pip install pytest-html
```

## Running Tests

### Basic Test Execution

#### Run All Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with extra verbose output
pytest -vv
```

#### Run Specific Tests
```bash
# Run specific test file
pytest tests/auth/test_auth.py

# Run specific test class
pytest tests/auth/test_auth.py::TestPasswordService

# Run specific test method
pytest tests/auth/test_auth.py::TestPasswordService::test_verify_password_success

# Run tests matching pattern
pytest -k "test_password"
```

### Test Execution by Category

#### Unit Tests
```bash
# Run only unit tests
pytest -m unit

# Run unit tests with verbose output
pytest -m unit -v
```

#### Integration Tests
```bash
# Run only integration tests
pytest -m integration

# Run integration tests with verbose output
pytest -m integration -v
```

#### Module-Specific Tests
```bash
# Authentication tests
pytest -m auth

# Expense tests
pytest -m expense

# Category tests
pytest -m category

# User tests
pytest -m user

# Analytics tests
pytest -m analytics

# Validation tests
pytest -m validation

# Logging tests
pytest -m logging

# Core functionality tests
pytest -m core

# API endpoint tests
pytest -m api
```

### Parallel Test Execution
```bash
# Run tests in parallel (auto-detect CPU cores)
pytest -n auto

# Run tests with specific number of workers
pytest -n 4

# Run specific tests in parallel
pytest -m unit -n auto
```

## Coverage Analysis

### Basic Coverage
```bash
# Run tests with coverage
pytest --cov=src

# Run tests with coverage and terminal report
pytest --cov=src --cov-report=term

# Run tests with coverage and HTML report
pytest --cov=src --cov-report=html

# Run tests with coverage and XML report
pytest --cov=src --cov-report=xml
```

### Comprehensive Coverage
```bash
# Run tests with all coverage reports
pytest --cov=src --cov-report=term --cov-report=html --cov-report=xml

# Run tests with coverage and fail if below threshold
pytest --cov=src --cov-fail-under=95

# Run tests with coverage and show missing lines
pytest --cov=src --cov-report=term-missing

# Run tests with coverage and show branch coverage
pytest --cov=src --cov-branch
```

### Coverage Reports

#### HTML Coverage Report
```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Open HTML coverage report
open htmlcov/index.html

# Or on Linux
xdg-open htmlcov/index.html
```

#### Terminal Coverage Report
```bash
# Generate terminal coverage report
pytest --cov=src --cov-report=term

# Generate terminal coverage report with missing lines
pytest --cov=src --cov-report=term-missing
```

#### XML Coverage Report
```bash
# Generate XML coverage report
pytest --cov=src --cov-report=xml

# XML report is saved as coverage.xml
```

### Coverage Analysis Commands
```bash
# Run coverage analysis
coverage run -m pytest

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html

# Generate XML coverage report
coverage xml

# Show coverage report with missing lines
coverage report --show-missing

# Show coverage report with branch coverage
coverage report --include="src/*" --show-missing
```

## Test Configuration

### Pytest Configuration
The test suite uses `pytest.ini` for configuration:
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    auth: Authentication tests
    expense: Expense tests
    category: Category tests
    user: User tests
    analytics: Analytics tests
    validation: Validation tests
    logging: Logging tests
    core: Core functionality tests
    api: API endpoint tests
```

### Coverage Configuration
Coverage is configured in `setup.cfg`:
```ini
[coverage:run]
source = src
omit = 
    */tests/*
    */venv/*
    */__pycache__/*
    */migrations/*
    */alembic/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod
```

## Test Execution Examples

### Development Workflow
```bash
# Quick test run during development
pytest -m unit

# Full test run before commit
pytest --cov=src --cov-fail-under=95

# Test specific feature
pytest -k "password" --cov=src

# Test with coverage report
pytest --cov=src --cov-report=html
```

### CI/CD Pipeline
```bash
# Run all tests with coverage
pytest --cov=src --cov-report=xml --cov-fail-under=95

# Run tests in parallel
pytest -n auto --cov=src --cov-report=xml

# Run specific test categories
pytest -m "unit or integration" --cov=src
```

### Debugging Tests
```bash
# Run tests with debug output
pytest -v -s

# Run specific test with debug
pytest -v -s tests/auth/test_auth.py::TestPasswordService::test_verify_password_success

# Run tests with pdb debugger
pytest --pdb

# Run tests with pdb on failure
pytest --pdb --pdb-failures
```

## Test Data and Fixtures

### Available Fixtures
The test suite includes comprehensive fixtures in `conftest.py`:

#### Mock Objects
- `mock_db_session`: Database session mock
- `mock_user_repo`: User repository mock
- `mock_category_repo`: Category repository mock
- `mock_expense_repo`: Expense repository mock
- `mock_password_service`: Password service mock
- `mock_jwt_service`: JWT service mock
- `mock_user_service`: User service mock
- `mock_category_service`: Category service mock
- `mock_expense_service`: Expense service mock
- `mock_settings`: Application settings mock
- `mock_logger`: Logger mock

#### Test Data
- `mock_user`: User model instance
- `mock_category`: Category model instance
- `mock_expense`: Expense model instance
- `mock_user_create`: User creation data
- `mock_category_create`: Category creation data
- `mock_expense_create`: Expense creation data
- `test_data_factory`: Test data factory

### Using Fixtures
```python
def test_example(mock_user, mock_password_service):
    # Use fixtures in test
    assert mock_user.email == "test@example.com"
    mock_password_service["hash"].return_value = "hashed_password"
```

## Test Patterns

### Arrange-Act-Assert Pattern
```python
def test_example():
    # Arrange
    mock_data = create_test_data()
    mock_service = Mock()
    mock_service.method.return_value = expected_result
    
    # Act
    result = function_under_test(mock_data)
    
    # Assert
    assert result == expected_result
    mock_service.method.assert_called_once_with(mock_data)
```

### Error Testing
```python
def test_error_scenario():
    # Arrange
    invalid_data = create_invalid_data()
    
    # Act & Assert
    with pytest.raises(ValidationError):
        function_under_test(invalid_data)
```

### Mock Verification
```python
def test_mock_verification():
    # Arrange
    mock_service = Mock()
    
    # Act
    function_under_test(mock_service)
    
    # Assert
    mock_service.method.assert_called_once_with(expected_args)
    assert mock_service.method.call_count == 1
```

## Continuous Integration

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
          pip install pytest pytest-cov coverage
      - name: Run tests
        run: pytest --cov=src --cov-report=xml --cov-fail-under=95
      - name: Upload coverage
        uses: codecov/codecov-action@v1
        with:
          file: ./coverage.xml
```

### Local CI Simulation
```bash
# Simulate CI environment
pytest --cov=src --cov-report=xml --cov-fail-under=95 -v

# Run tests in parallel like CI
pytest -n auto --cov=src --cov-report=xml
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Check if src is in path
python -c "import src; print(src.__file__)"

# Install in development mode
pip install -e .
```

#### Mock Issues
```bash
# Check mock setup
pytest -v tests/auth/test_auth.py::TestPasswordService::test_verify_password_success

# Run with debug output
pytest -v -s tests/auth/test_auth.py::TestPasswordService::test_verify_password_success
```

#### Coverage Issues
```bash
# Check coverage configuration
coverage report --show-missing

# Check source paths
pytest --cov=src --cov-report=term

# Verify coverage files
ls -la htmlcov/
```

### Debug Mode
```bash
# Run tests with debug output
pytest -v -s

# Run specific test with debug
pytest -v -s tests/auth/test_auth.py::TestPasswordService::test_verify_password_success

# Run tests with pdb debugger
pytest --pdb

# Run tests with pdb on failure
pytest --pdb --pdb-failures
```

### Test Discovery
```bash
# List all tests
pytest --collect-only

# List tests in specific file
pytest --collect-only tests/auth/test_auth.py

# List tests with specific marker
pytest --collect-only -m unit

# List tests matching pattern
pytest --collect-only -k "password"
```

## Best Practices

### Test Writing
1. Use descriptive test names
2. Follow Arrange-Act-Assert pattern
3. Test both success and failure scenarios
4. Verify all mock calls
5. Use appropriate assertions
6. Keep tests independent and isolated

### Mock Management
1. Use fixtures for common mocks
2. Reset mocks between tests
3. Verify mock calls and arguments
4. Use appropriate mock return values
5. Mock at the right level of abstraction

### Coverage Optimization
1. Test all code paths
2. Include edge cases and error scenarios
3. Test validation and business rules
4. Verify error handling
5. Test all public interfaces

## Maintenance

### Adding New Tests
1. Create test file in appropriate directory
2. Use existing fixtures from conftest.py
3. Follow established patterns
4. Add appropriate markers
5. Update documentation

### Updating Fixtures
1. Modify conftest.py
2. Update affected tests
3. Verify all tests still pass
4. Update documentation

### Coverage Monitoring
1. Run coverage reports regularly
2. Monitor coverage trends
3. Address coverage gaps
4. Maintain >95% coverage threshold

## Support

For questions or issues with testing:
1. Check this guide
2. Review test patterns and examples
3. Check conftest.py for available fixtures
4. Verify mock configurations
5. Run tests with debug output
6. Check pytest documentation
7. Check coverage.py documentation
