# Docker Troubleshooting Guide

Comprehensive troubleshooting guide for Docker-related issues with the Expense Tracker API.

## 📋 Table of Contents

- [Common Issues](#common-issues)
- [Build Problems](#build-problems)
- [Runtime Errors](#runtime-errors)
- [Database Issues](#database-issues)
- [Network Problems](#network-problems)
- [Performance Issues](#performance-issues)
- [Debugging Commands](#debugging-commands)
- [Error Logs](#error-logs)

## 🚨 Common Issues

### Issue: Container Won't Start

**Symptoms:**
- Container exits immediately after starting
- `docker ps` shows no running containers
- Application logs show startup errors

**Solutions:**
```bash
# Check container logs
docker-compose logs app

# Check container status
docker ps -a

# Restart with verbose logging
docker-compose up --build --force-recreate

# Check resource availability
docker system df
free -h
```

### Issue: Port Already in Use

**Symptoms:**
- `Error: bind: address already in use`
- Port 8000 or 5432 unavailable

**Solutions:**
```bash
# Find process using port
sudo netstat -tulpn | grep :8000
sudo lsof -i :8000

# Kill process (if safe)
sudo kill -9 <PID>

# Use different ports
docker-compose up -p 8001:8000 -p 5433:5432
```

### Issue: Permission Denied

**Symptoms:**
- `Permission denied` errors
- Cannot write to volumes
- File access issues

**Solutions:**
```bash
# Fix volume permissions
sudo chown -R $USER:$USER ./logs

# Check Docker daemon permissions
sudo usermod -aG docker $USER
newgrp docker

# Restart Docker service
sudo systemctl restart docker
```

## 🔨 Build Problems

### Issue: Dockerfile Build Fails

**Common Causes:**
- Missing dependencies
- Invalid syntax
- Network issues during package installation

**Solutions:**
```bash
# Clean build without cache
docker-compose build --no-cache

# Build specific service
docker-compose build app

# Check Dockerfile syntax
docker build -t test-build .

# Increase build timeout
export DOCKER_BUILDKIT=1
docker-compose build --progress=plain
```

### Issue: Package Installation Fails

**Symptoms:**
- `pip install` errors
- Package not found
- Version conflicts

**Solutions:**
```bash
# Update requirements.txt
pip freeze > requirements.txt

# Check package availability
docker run --rm python:3.10-slim pip search <package-name>

# Use specific package versions
# In requirements.txt:
fastapi==0.104.1
uvicorn==0.24.0
```

### Issue: Multi-stage Build Issues

**Symptoms:**
- Build context too large
- Stage dependencies not found
- Copy operations fail

**Solutions:**
```bash
# Check .dockerignore
cat .dockerignore

# Reduce build context
docker build --no-cache -t test .

# Debug build stages
docker build --target builder -t debug-builder .
docker run -it debug-builder bash
```

## ⚡ Runtime Errors

### Issue: Application Crashes on Startup

**Symptoms:**
- FastAPI fails to start
- Import errors
- Configuration issues

**Solutions:**
```bash
# Check application logs
docker-compose logs -f app

# Debug container environment
docker-compose exec app env

# Check Python path
docker-compose exec app python -c "import sys; print(sys.path)"

# Verify imports
docker-compose exec app python -c "from src.api.main import app"
```

### Issue: Environment Variable Problems

**Symptoms:**
- `SettingsError` from Pydantic
- Missing configuration values
- Invalid environment format

**Solutions:**
```bash
# Check environment variables
docker-compose exec app env | grep -E "(DATABASE|SECRET|DEBUG)"

# Validate .env file
docker-compose exec app python -c "from src.core.config import get_settings; print(get_settings())"

# Fix CORS origins format
# In docker-compose.yaml:
BACKEND_CORS_ORIGINS: '["http://localhost:3000","http://localhost:8080"]'
```

### Issue: Missing Dependencies

**Symptoms:**
- `ModuleNotFoundError`
- Import errors for specific packages

**Solutions:**
```bash
# Add missing dependency to requirements.txt
echo "email-validator>=2.0.0" >> requirements/requirements.txt

# Rebuild container
docker-compose build --no-cache app

# Check installed packages
docker-compose exec app pip list
```

## 🗄️ Database Issues

### Issue: Database Connection Failed

**Symptoms:**
- `sqlalchemy.exc.OperationalError`
- Database not accessible
- Connection timeout

**Solutions:**
```bash
# Check database status
docker-compose exec postgres pg_isready -U expense_user

# Test database connection
docker-compose exec postgres psql -U expense_user -d expense_tracker -c "SELECT 1;"

# Check database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up --build -d
```

### Issue: Migration Failures

**Symptoms:**
- Alembic migration errors
- Database schema issues
- Table creation failures

**Solutions:**
```bash
# Check migration status
docker-compose exec app alembic current

# Run migrations manually
docker-compose exec app alembic upgrade head

# Create new migration
docker-compose exec app alembic revision --autogenerate -m "fix_schema"

# Reset migrations (development only)
docker-compose exec postgres psql -U expense_user -d expense_tracker -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

### Issue: Database Data Loss

**Symptoms:**
- Tables empty after restart
- Data not persisting
- Volume mount issues

**Solutions:**
```bash
# Check volume mounts
docker volume ls
docker volume inspect expense-tracker_postgres_data

# Backup data
docker-compose exec postgres pg_dump -U expense_user expense_tracker > backup.sql

# Restore data
docker-compose exec -T postgres psql -U expense_user -d expense_tracker < backup.sql
```

## 🌐 Network Problems

### Issue: Services Can't Communicate

**Symptoms:**
- Application can't reach database
- Internal network errors
- DNS resolution issues

**Solutions:**
```bash
# Check network connectivity
docker-compose exec app ping postgres

# Test database connection from app
docker-compose exec app python -c "import psycopg2; psycopg2.connect('postgresql://expense_user:expense_password@postgres:5432/expense_tracker')"

# Check Docker networks
docker network ls
docker network inspect expense-tracker_expense-tracker-network
```

### Issue: External Access Problems

**Symptoms:**
- Can't access API from host
- Port forwarding issues
- Firewall blocking

**Solutions:**
```bash
# Check port binding
docker-compose ps

# Test local access
curl http://localhost:8000/health

# Check firewall
sudo ufw status
sudo iptables -L

# Use host networking (development only)
docker-compose up --network host
```

## 📈 Performance Issues

### Issue: Slow Container Startup

**Symptoms:**
- Long startup times
- Resource constraints
- Image size issues

**Solutions:**
```bash
# Check image size
docker images expense-tracker-api

# Optimize Dockerfile
# Use .dockerignore to reduce build context
# Use multi-stage builds

# Monitor resource usage
docker stats
htop
```

### Issue: High Memory Usage

**Symptoms:**
- Container using excessive memory
- System slowdown
- Out of memory errors

**Solutions:**
```bash
# Set memory limits
# In docker-compose.yaml:
deploy:
  resources:
    limits:
      memory: 512M

# Monitor memory usage
docker stats --no-stream

# Check for memory leaks
docker-compose exec app python -c "import psutil; print(psutil.virtual_memory())"
```

### Issue: Slow Database Queries

**Symptoms:**
- API response delays
- Database connection timeouts
- Query performance issues

**Solutions:**
```bash
# Check database performance
docker-compose exec postgres psql -U expense_user -d expense_tracker -c "SELECT * FROM pg_stat_activity;"

# Monitor slow queries
docker-compose exec postgres psql -U expense_user -d expense_tracker -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Optimize database
docker-compose exec postgres psql -U expense_user -d expense_tracker -c "VACUUM ANALYZE;"
```

## 🔍 Debugging Commands

### Container Debugging
```bash
# Access container shell
docker-compose exec app bash
docker-compose exec postgres bash

# Check container processes
docker-compose exec app ps aux

# Check container resources
docker-compose exec app top
docker-compose exec app df -h
```

### Application Debugging
```bash
# Check Python environment
docker-compose exec app python --version
docker-compose exec app pip list

# Test imports
docker-compose exec app python -c "import src.api.main"

# Check configuration
docker-compose exec app python -c "from src.core.config import get_settings; s = get_settings(); print(f'Debug: {s.debug}, DB: {s.database_url[:20]}...')"
```

### Database Debugging
```bash
# Check database status
docker-compose exec postgres pg_isready -U expense_user

# List databases
docker-compose exec postgres psql -U expense_user -l

# Check connections
docker-compose exec postgres psql -U expense_user -d expense_tracker -c "SELECT * FROM pg_stat_activity;"

# Check tables
docker-compose exec postgres psql -U expense_user -d expense_tracker -c "\dt"
```

## 📝 Error Logs

### Common Error Messages

#### Pydantic Settings Error
```
pydantic_settings.exceptions.SettingsError: error parsing value for field "backend_cors_origins"
```
**Solution:** Fix CORS origins format in docker-compose.yaml

#### Database Connection Error
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```
**Solution:** Check database service status and network connectivity

#### Import Error
```
ModuleNotFoundError: No module named 'email_validator'
```
**Solution:** Add missing dependency to requirements.txt

#### Port Binding Error
```
Error: bind: address already in use
```
**Solution:** Kill process using port or use different port

### Log Analysis
```bash
# Filter error logs
docker-compose logs app | grep -i error

# Follow logs in real-time
docker-compose logs -f --tail=100 app

# Export logs for analysis
docker-compose logs app > app.log
docker-compose logs postgres > postgres.log
```

## 🆘 Getting Additional Help

If issues persist:

1. **Check Docker version compatibility**
2. **Review system resources**
3. **Check for conflicting services**
4. **Consult Docker documentation**
5. **Check project issues on GitHub**

## 🔗 Related Documentation

- [Docker Guide](docker_guide.md) - Complete setup guide
- [Production Deployment](production.md) - Production-specific issues
- [Commands Reference](commands.md) - Useful commands
