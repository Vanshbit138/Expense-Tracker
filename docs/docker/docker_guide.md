# Docker Guide

Complete guide for deploying and managing the Expense Tracker API using Docker.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Container Architecture](#container-architecture)
- [Configuration](#configuration)
- [Development Workflow](#development-workflow)
- [Production Deployment](#production-deployment)
- [Monitoring & Logs](#monitoring--logs)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

The Expense Tracker API is containerized using Docker with a multi-stage build process that includes:

- **FastAPI Application**: Python 3.10-based REST API
- **PostgreSQL Database**: Persistent data storage
- **Health Checks**: Automated monitoring
- **Security**: Non-root user execution
- **Optimization**: Multi-stage build for smaller images

## 📋 Prerequisites

### System Requirements
- **Docker Engine**: 20.10+ 
- **Docker Compose**: 2.0+
- **RAM**: 2GB+ available
- **Disk Space**: 5GB+ available
- **OS**: Linux, macOS, or Windows with WSL2

### Installation
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# macOS (using Homebrew)
brew install docker docker-compose

# Windows (using Chocolatey)
choco install docker-desktop
```

## 🚀 Quick Start

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd Expense-Tracker
```

### 2. Start Services
```bash
# Build and start all services
docker-compose up --build -d

# Check status
docker-compose ps
```

### 3. Verify Deployment
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/api/v1/docs
```

## 🏗️ Container Architecture

### Multi-Stage Dockerfile

```dockerfile
# Stage 1: Builder
FROM python:3.10-slim as builder
# - Installs build dependencies
# - Creates virtual environment
# - Installs Python packages

# Stage 2: Production
FROM python:3.10-slim as production
# - Copies virtual environment
# - Creates non-root user
# - Sets up application
```

### Service Components

| Service | Image | Purpose | Port |
|---------|-------|---------|------|
| `app` | Custom FastAPI | API Server | 8000 |
| `postgres` | postgres:15-alpine | Database | 5432 |

### Volume Mounts

```yaml
volumes:
  - ./logs:/app/logs          # Application logs
  - postgres_data:/var/lib/postgresql/data  # Database persistence
```

## ⚙️ Configuration

### Environment Variables

The application uses environment variables for configuration:

```yaml
# Database
DATABASE_URL: postgresql://expense_user:expense_password@postgres:5432/expense_tracker

# Security
SECRET_KEY: your-super-secret-jwt-key-change-in-production-32-chars-minimum

# Application
DEBUG: "false"
LOG_LEVEL: INFO
BACKEND_CORS_ORIGINS: '["http://localhost:3000","http://localhost:8080","http://localhost:8000"]'
```

### Custom Configuration

Create a `.env` file for custom settings:

```bash
# Copy example
cp .env.example .env

# Edit configuration
nano .env
```

## 🔄 Development Workflow

### Starting Development Environment

```bash
# Start with live reload
docker-compose up --build

# Background mode
docker-compose up --build -d
```

### Code Changes

The application supports live reload for development:

```bash
# View logs
docker-compose logs -f app

# Restart specific service
docker-compose restart app
```

### Database Management

```bash
# Access database
docker-compose exec postgres psql -U expense_user -d expense_tracker

# Run migrations
docker-compose exec app alembic upgrade head

# Create new migration
docker-compose exec app alembic revision --autogenerate -m "description"
```

### Testing

```bash
# Run tests
docker-compose exec app pytest

# Run with coverage
docker-compose exec app pytest --cov=src

# Run specific test
docker-compose exec app pytest tests/api/test_main.py
```

## 🚀 Production Deployment

### Security Considerations

1. **Change Default Secrets**:
   ```yaml
   SECRET_KEY: "your-production-secret-key-32-chars-minimum"
   ```

2. **Use Environment Files**:
   ```bash
   # Create production environment file
   cp .env.example .env.production
   ```

3. **Resource Limits**:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 512M
         cpus: '0.5'
   ```

### Production Commands

```bash
# Production build
docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml up --build -d

# Scale application
docker-compose up --scale app=3 -d

# Update application
docker-compose pull
docker-compose up -d
```

## 📊 Monitoring & Logs

### Health Checks

```bash
# Application health
curl http://localhost:8000/health

# Container health
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Log Management

```bash
# View logs
docker-compose logs -f app
docker-compose logs -f postgres

# Log levels
docker-compose logs --tail=100 app

# Export logs
docker-compose logs app > app.log
```

### Resource Monitoring

```bash
# Container stats
docker stats

# Specific container
docker stats expense-tracker-api

# Disk usage
docker system df
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Build Failures
```bash
# Clean build
docker-compose build --no-cache

# Check Dockerfile syntax
docker build -t test .
```

#### 2. Database Connection Issues
```bash
# Check database status
docker-compose exec postgres pg_isready -U expense_user

# Reset database
docker-compose down -v
docker-compose up --build -d
```

#### 3. Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :8000

# Use different ports
docker-compose up -d --scale app=0
docker-compose up -d -p 8001:8000
```

### Debugging Commands

```bash
# Container shell access
docker-compose exec app bash

# Database shell
docker-compose exec postgres psql -U expense_user -d expense_tracker

# Check environment variables
docker-compose exec app env | grep -E "(DATABASE|SECRET)"
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [FastAPI Docker Guide](https://fastapi.tiangolo.com/deployment/docker/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)

## 🔗 Related Documentation

- [Troubleshooting Guide](troubleshooting.md) - Detailed problem solutions
- [Production Deployment](production.md) - Production-specific configurations
- [Commands Reference](commands.md) - Quick command reference
