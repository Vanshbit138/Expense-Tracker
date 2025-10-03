# Configuration Guide

Complete guide for configuring the Expense Tracker application.

## Overview

The Expense Tracker application uses environment variables for configuration. This approach provides flexibility across different environments (development, staging, production) and keeps sensitive information secure.

## Environment Setup

### 1. Create Environment File

Copy the example environment file:

```bash
cp env.example .env
```

### 2. Configure Required Variables

Edit the `.env` file with your specific configuration:

```bash
nano .env  # or use your preferred editor
```

## Configuration Variables

### Required Variables

These variables must be set for the application to function properly.

#### Database Configuration

```bash
# Primary database connection
DATABASE_URL=postgresql://username:password@localhost:5432/expense_tracker

# Test database connection (for running tests)
DATABASE_URL_TEST=postgresql://username:password@localhost:5432/expense_tracker_test
```

**Database URL Format:**
```
postgresql://[user[:password]@][host][:port][/database][?param1=value1&...]
```

**Examples:**
```bash
# Local development
DATABASE_URL=postgresql://postgres:password@localhost:5432/expense_tracker

# Remote database
DATABASE_URL=postgresql://user:pass@db.example.com:5432/expense_tracker

# With SSL
DATABASE_URL=postgresql://user:pass@db.example.com:5432/expense_tracker?sslmode=require
```

#### JWT Configuration

```bash
# Secret key for JWT token signing (MUST be changed in production)
SECRET_KEY=your-secret-key-here-change-in-production

# JWT algorithm
ALGORITHM=HS256

# Token expiration time in minutes (1440 = 24 hours)
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

**Secret Key Requirements:**
- Minimum 32 characters
- Use a cryptographically secure random string
- Different for each environment
- Keep secret and never commit to version control

**Generate a secure secret key:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

### Optional Variables

These variables have default values but can be customized.

#### Application Configuration

```bash
# Enable debug mode (True/False)
DEBUG=True

# Application name
PROJECT_NAME=Expense Tracker API

# Application version
VERSION=1.0.0

# API version prefix
API_V1_STR=/api/v1
```

#### CORS Configuration

```bash
# Allowed CORS origins (comma-separated or JSON array)
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
```

**Examples:**
```bash
# Single origin
BACKEND_CORS_ORIGINS=http://localhost:3000

# Multiple origins (comma-separated)
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080,https://myapp.com

# JSON array format
BACKEND_CORS_ORIGINS=["http://localhost:3000", "https://myapp.com"]
```

#### Pagination Configuration

```bash
# Default page size for paginated endpoints
DEFAULT_PAGE_SIZE=20

# Maximum page size allowed
MAX_PAGE_SIZE=100
```

#### Logging Configuration

```bash
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Enable JSON logging (True/False)
ENABLE_JSON_LOGGING=True

# Log file path
LOG_FILE=logs/expense-tracker.log
```

## Environment-Specific Configurations

### Development Environment

```bash
# .env.development
DEBUG=True
LOG_LEVEL=DEBUG
ENABLE_JSON_LOGGING=False
DATABASE_URL=postgresql://postgres:password@localhost:5432/expense_tracker_dev
SECRET_KEY=dev-secret-key-not-for-production
```

### Staging Environment

```bash
# .env.staging
DEBUG=False
LOG_LEVEL=INFO
ENABLE_JSON_LOGGING=True
DATABASE_URL=postgresql://user:pass@staging-db:5432/expense_tracker_staging
SECRET_KEY=staging-secret-key
```

### Production Environment

```bash
# .env.production
DEBUG=False
LOG_LEVEL=WARNING
ENABLE_JSON_LOGGING=True
DATABASE_URL=postgresql://user:pass@prod-db:5432/expense_tracker_prod
SECRET_KEY=production-secret-key-very-secure
```

## Database Configuration

### PostgreSQL Setup

#### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS (Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download and install from [PostgreSQL official website](https://www.postgresql.org/download/windows/)

#### 2. Create Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE expense_tracker;

# Create test database
CREATE DATABASE expense_tracker_test;

# Create user (optional)
CREATE USER expense_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE expense_tracker TO expense_user;
GRANT ALL PRIVILEGES ON DATABASE expense_tracker_test TO expense_user;

# Exit
\q
```

#### 3. Run Migrations

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
alembic upgrade head
```

### Database Connection Options

#### Connection Pooling

The application uses SQLAlchemy's connection pooling by default. You can configure it by adding parameters to the DATABASE_URL:

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/expense_tracker?pool_size=10&max_overflow=20
```

**Pool Parameters:**
- `pool_size`: Number of connections to maintain in the pool (default: 5)
- `max_overflow`: Additional connections allowed beyond pool_size (default: 10)
- `pool_timeout`: Seconds to wait for a connection (default: 30)
- `pool_recycle`: Seconds before recreating a connection (default: 3600)

#### SSL Configuration

For production databases, enable SSL:

```bash
DATABASE_URL=postgresql://user:pass@db.example.com:5432/expense_tracker?sslmode=require
```

**SSL Modes:**
- `disable`: No SSL
- `allow`: Try non-SSL, then SSL
- `prefer`: Try SSL, then non-SSL
- `require`: Require SSL
- `verify-ca`: Require SSL and verify CA
- `verify-full`: Require SSL and verify CA and hostname

## Security Configuration

### JWT Security

#### Secret Key Generation

**Using Python:**
```python
import secrets
import string

# Generate a secure random string
secret_key = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))
print(secret_key)
```

**Using OpenSSL:**
```bash
openssl rand -base64 64
```

**Using Node.js:**
```javascript
const crypto = require('crypto');
console.log(crypto.randomBytes(64).toString('base64'));
```

#### Token Expiration

Configure token expiration based on your security requirements:

```bash
# 1 hour (3600 seconds)
ACCESS_TOKEN_EXPIRE_MINUTES=60

# 24 hours (default)
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 7 days
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### CORS Security

Configure CORS origins carefully:

```bash
# Development - allow localhost
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Production - specific domains only
BACKEND_CORS_ORIGINS=["https://myapp.com", "https://www.myapp.com"]

# Staging - allow staging domains
BACKEND_CORS_ORIGINS=["https://staging.myapp.com"]
```

**Security Best Practices:**
- Never use wildcard (`*`) in production
- Specify exact domains and ports
- Use HTTPS in production
- Regularly review and update allowed origins

## Logging Configuration

### Log Levels

Configure log levels based on environment:

```bash
# Development - verbose logging
LOG_LEVEL=DEBUG

# Staging - moderate logging
LOG_LEVEL=INFO

# Production - minimal logging
LOG_LEVEL=WARNING
```

### Log Formats

#### JSON Logging (Recommended for Production)

```bash
ENABLE_JSON_LOGGING=True
```

**Benefits:**
- Easy to parse by log aggregation tools
- Structured data for better analysis
- Consistent format across all log entries

#### Console Logging (Development)

```bash
ENABLE_JSON_LOGGING=False
```

**Benefits:**
- Human-readable format
- Colored output for better visibility
- Easy to read during development

### Log File Configuration

```bash
# Log file path
LOG_FILE=logs/expense-tracker.log

# Ensure log directory exists
mkdir -p logs
```

**Log Rotation:**
Consider setting up log rotation to prevent log files from growing too large:

```bash
# Add to /etc/logrotate.d/expense-tracker
/path/to/expense-tracker/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 app app
}
```

## Environment Validation

The application validates configuration on startup. Common validation errors:

### Database URL Validation

**Error:** `DATABASE_URL must be properly configured in .env file`

**Solution:** Ensure DATABASE_URL is set and contains valid credentials:
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/expense_tracker
```

### Secret Key Validation

**Error:** `SECRET_KEY must be at least 32 characters long for security`

**Solution:** Generate a longer secret key:
```bash
SECRET_KEY=your-very-long-secret-key-at-least-32-characters-long
```

### CORS Origins Validation

**Error:** `Invalid CORS origins configuration`

**Solution:** Use proper format:
```bash
# Correct
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Incorrect
BACKEND_CORS_ORIGINS=http://localhost:3000
```

## Configuration Testing

### Test Configuration

```bash
# Test database connection
python -c "
from src.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database connection successful')
"

# Test configuration loading
python -c "
from src.core.config import settings
print(f'App name: {settings.app_name}')
print(f'Debug mode: {settings.debug}')
print(f'Database URL configured: {bool(settings.database_url)}')
"
```

### Environment-Specific Testing

```bash
# Test with specific environment file
ENV_FILE=.env.staging python run_server.py

# Test configuration validation
python -c "
import os
os.environ['DATABASE_URL'] = 'invalid-url'
try:
    from src.core.config import settings
except Exception as e:
    print(f'Configuration validation working: {e}')
"
```

## Docker Configuration

### Docker Environment Variables

```dockerfile
# Dockerfile
ENV DATABASE_URL=postgresql://user:pass@db:5432/expense_tracker
ENV SECRET_KEY=your-secret-key
ENV DEBUG=False
ENV LOG_LEVEL=INFO
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/expense_tracker
      - SECRET_KEY=your-secret-key
      - DEBUG=False
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=expense_tracker
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Production Deployment

### Environment Variables in Production

**Using systemd service:**
```ini
# /etc/systemd/system/expense-tracker.service
[Unit]
Description=Expense Tracker API
After=network.target

[Service]
Type=exec
User=app
Group=app
WorkingDirectory=/opt/expense-tracker
Environment=DATABASE_URL=postgresql://user:pass@db:5432/expense_tracker
Environment=SECRET_KEY=production-secret-key
Environment=DEBUG=False
Environment=LOG_LEVEL=WARNING
ExecStart=/opt/expense-tracker/venv/bin/python run_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Using Docker:**
```bash
docker run -d \
  --name expense-tracker \
  -e DATABASE_URL=postgresql://user:pass@db:5432/expense_tracker \
  -e SECRET_KEY=production-secret-key \
  -e DEBUG=False \
  -e LOG_LEVEL=WARNING \
  -p 8000:8000 \
  expense-tracker:latest
```

### Secrets Management

**Using HashiCorp Vault:**
```bash
# Store secrets in Vault
vault kv put secret/expense-tracker \
  database_url="postgresql://user:pass@db:5432/expense_tracker" \
  secret_key="production-secret-key"

# Retrieve secrets
vault kv get -field=database_url secret/expense-tracker
```

**Using AWS Secrets Manager:**
```bash
# Store secrets
aws secretsmanager create-secret \
  --name "expense-tracker/prod" \
  --secret-string '{"database_url":"postgresql://user:pass@db:5432/expense_tracker","secret_key":"production-secret-key"}'

# Retrieve secrets
aws secretsmanager get-secret-value \
  --secret-id "expense-tracker/prod" \
  --query SecretString \
  --output text
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Failed

**Error:** `sqlalchemy.exc.OperationalError: (psycopg2.OperationalError)`

**Solutions:**
- Check if PostgreSQL is running
- Verify database credentials
- Ensure database exists
- Check network connectivity
- Verify SSL configuration

#### 2. JWT Token Invalid

**Error:** `jwt.exceptions.InvalidTokenError`

**Solutions:**
- Check SECRET_KEY configuration
- Verify token format
- Check token expiration
- Ensure consistent SECRET_KEY across restarts

#### 3. CORS Errors

**Error:** `Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solutions:**
- Add origin to BACKEND_CORS_ORIGINS
- Check CORS configuration format
- Verify HTTPS/HTTP protocol matching

#### 4. Configuration Validation Errors

**Error:** `ValueError: DATABASE_URL must be properly configured`

**Solutions:**
- Check .env file exists
- Verify environment variable names
- Ensure no typos in variable names
- Check file permissions

### Debug Mode

Enable debug mode for detailed error information:

```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

**Note:** Never enable debug mode in production!

### Configuration Validation

The application validates configuration on startup. Check the startup logs for validation errors:

```bash
python run_server.py
```

Look for validation error messages and fix the corresponding configuration variables.

## Best Practices

### Security

1. **Never commit .env files** to version control
2. **Use different secrets** for each environment
3. **Rotate secrets regularly** in production
4. **Use strong, random secrets** (minimum 32 characters)
5. **Restrict CORS origins** to specific domains
6. **Use HTTPS** in production
7. **Enable SSL** for database connections

### Performance

1. **Configure connection pooling** appropriately
2. **Use appropriate log levels** for each environment
3. **Enable JSON logging** in production
4. **Set up log rotation** to prevent disk space issues
5. **Monitor database performance** and adjust pool settings

### Maintenance

1. **Document configuration changes**
2. **Test configuration** in staging before production
3. **Use configuration management tools** for complex deployments
4. **Monitor application logs** for configuration-related errors
5. **Keep configuration files** in version control (without secrets)

## Support

For configuration-related issues:

1. Check this guide
2. Review application logs
3. Test configuration validation
4. Check environment variable format
5. Verify database connectivity
6. Open an issue with configuration details (without secrets)
