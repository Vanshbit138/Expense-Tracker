# Structured Logging Implementation

## Overview
The application implements comprehensive structured logging using `structlog` and `python-json-logger` for production-ready logging.

## Features
- **Structured JSON Logs**: Machine-readable log format
- **Dynamic Log Levels**: Configurable via environment variables
- **Request Correlation**: Unique correlation IDs for request tracking
- **Performance Metrics**: Request timing and processing metrics
- **Error Tracking**: Full stack traces and error context
- **File & Console Logging**: Dual output for development and production

## Configuration

### Environment Variables
```bash
LOG_LEVEL=DEBUG          # DEBUG, INFO, WARNING, ERROR, CRITICAL
ENABLE_JSON_LOGGING=True # True for JSON, False for console format
LOG_FILE=logs/expense-tracker.log
```

### Log Levels
| Level | Description | Use Case |
|-------|-------------|----------|
| DEBUG | Detailed information | Development, troubleshooting |
| INFO | General information | Production monitoring |
| WARNING | Unexpected but recoverable | Production alerts |
| ERROR | Error occurred | Error monitoring |
| CRITICAL | Serious error | Emergency alerts |

## Implementation Details

### 1. Logging Configuration (`src/core/logging_config.py`)
- Custom JSON formatter with additional fields
- Dynamic log level configuration
- File and console handlers
- Logger-specific level configuration

### 2. Logger Usage
Loggers are defined in all service classes and API routers:
- `src/services/user/user_service.py`
- `src/services/category/category_service.py`
- `src/services/expense/expense_service.py`
- `src/api/routers/auth.py`
- `src/api/routers/categories.py`
- `src/api/routers/expenses.py`
- `src/api/routers/analytics.py`

### 3. Log Format
```json
{
  "timestamp": "2025-09-27T11:40:17.053538Z",
  "level": "INFO",
  "logger": "src.services.user.user_service",
  "module": "user_service",
  "function": "create_user",
  "line_number": 45,
  "message": "User created successfully",
  "service": "expense-tracker-api",
  "process_id": 12345,
  "thread_id": 67890,
  "correlation_id": "req-123-456",
  "request_method": "POST",
  "request_path": "/api/v1/auth/register",
  "user_id": "user-789",
  "process_time_ms": 150.5
}
```

## Usage Examples

### Basic Logging
```python
from src.core.logging_config import get_logger

logger = get_logger(__name__)

# Different log levels
logger.debug("Debug information", user_id="123", action="debug_test")
logger.info("Operation completed", user_id="123", action="create_user")
logger.warning("Potential issue", user_id="123", reason="low_balance")
logger.error("Operation failed", user_id="123", error_code="ERR001")
logger.critical("System failure", user_id="123", component="database")
```

### Service Logging
```python
class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_logger(self.__class__.__name__)
    
    def create_user(self, user_data: UserCreate) -> User:
        self.logger.info("Creating new user", email=user_data.email)
        try:
            # User creation logic
            self.logger.info("User created successfully", user_id=user.id)
            return user
        except Exception as e:
            self.logger.error("Failed to create user", error=str(e), exc_info=True)
            raise
```

## Dynamic Log Level Behavior

### DEBUG Level
- Shows all log levels
- Includes detailed debugging information
- Used during development

### INFO Level
- Shows INFO, WARNING, ERROR, CRITICAL
- Suppresses DEBUG logs
- Used in production monitoring

### WARNING Level
- Shows WARNING, ERROR, CRITICAL
- Suppresses DEBUG and INFO logs
- Used for alerting

### ERROR Level
- Shows ERROR and CRITICAL only
- Used for error monitoring

### CRITICAL Level
- Shows only CRITICAL logs
- Used for emergency situations

## Testing Log Levels

### Test Script
```python
# Test different log levels
import os
os.environ['LOG_LEVEL'] = 'DEBUG'
setup_logging()

logger = get_logger(__name__)
logger.debug("This will show in DEBUG level")
logger.info("This will show in INFO level and above")
logger.warning("This will show in WARNING level and above")
logger.error("This will show in ERROR level and above")
logger.critical("This will show in CRITICAL level only")
```

## File Structure
```
logs/
└── expense-tracker.log    # Main log file
```

## Monitoring
- Logs are written to both console and file
- File rotation can be configured
- Logs include correlation IDs for request tracking
- Performance metrics are included in request logs
