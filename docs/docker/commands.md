# Docker Commands Reference

Quick reference guide for all Docker commands used in the Expense Tracker project.

## 📋 Table of Contents

- [Basic Commands](#basic-commands)
- [Docker Compose Commands](#docker-compose-commands)
- [Container Management](#container-management)
- [Image Management](#image-management)
- [Volume Management](#volume-management)
- [Network Management](#network-management)
- [Logging & Debugging](#logging--debugging)
- [Production Commands](#production-commands)

## 🚀 Basic Commands

### Docker Information
```bash
# Check Docker version
docker --version
docker-compose --version

# System information
docker system info
docker system df

# Check running containers
docker ps
docker ps -a
```

### Container Operations
```bash
# Run container
docker run -d --name expense-tracker-api -p 8000:8000 expense-tracker-api

# Stop container
docker stop expense-tracker-api

# Start container
docker start expense-tracker-api

# Restart container
docker restart expense-tracker-api

# Remove container
docker rm expense-tracker-api
```

## 🐳 Docker Compose Commands

### Basic Operations
```bash
# Start services
docker-compose up
docker-compose up -d                    # Background mode
docker-compose up --build               # Rebuild images
docker-compose up --build -d            # Rebuild and background

# Stop services
docker-compose down
docker-compose down -v                  # Remove volumes
docker-compose down --remove-orphans    # Remove orphaned containers

# Restart services
docker-compose restart
docker-compose restart app              # Restart specific service
```

### Service Management
```bash
# Scale services
docker-compose up --scale app=3 -d

# View service status
docker-compose ps
docker-compose ps -a

# View service logs
docker-compose logs
docker-compose logs -f app              # Follow logs
docker-compose logs --tail=100 app      # Last 100 lines
```

### Build Operations
```bash
# Build services
docker-compose build
docker-compose build app                # Build specific service
docker-compose build --no-cache         # Build without cache
docker-compose build --parallel         # Parallel build

# Pull images
docker-compose pull
docker-compose pull app                 # Pull specific service
```

## 📦 Container Management

### Container Access
```bash
# Execute commands in container
docker-compose exec app bash
docker-compose exec app python --version
docker-compose exec postgres psql -U expense_user -d expense_tracker

# Run one-time commands
docker-compose run app pytest
docker-compose run --rm app alembic upgrade head
```

### Container Inspection
```bash
# Container details
docker inspect expense-tracker-api
docker-compose exec app env             # Environment variables
docker-compose exec app ps aux          # Running processes

# Resource usage
docker stats
docker stats expense-tracker-api
docker-compose exec app top
```

### Container Health
```bash
# Health check
curl http://localhost:8000/health
docker-compose exec app python -c "import requests; requests.get('http://localhost:8000/health')"

# Database health
docker-compose exec postgres pg_isready -U expense_user
```

## 🖼️ Image Management

### Image Operations
```bash
# List images
docker images
docker images expense-tracker-api

# Remove images
docker rmi expense-tracker-api
docker rmi $(docker images -q)         # Remove all images

# Image details
docker inspect expense-tracker-api
docker history expense-tracker-api
```

### Build Operations
```bash
# Build image
docker build -t expense-tracker-api .
docker build --no-cache -t expense-tracker-api .
docker build --target builder -t debug-builder .

# Tag image
docker tag expense-tracker-api:latest expense-tracker-api:v1.0.0
```

## 💾 Volume Management

### Volume Operations
```bash
# List volumes
docker volume ls
docker volume inspect expense-tracker_postgres_data

# Create volume
docker volume create postgres_data

# Remove volume
docker volume rm postgres_data
docker volume prune                     # Remove unused volumes
```

### Data Backup
```bash
# Backup database
docker-compose exec postgres pg_dump -U expense_user expense_tracker > backup.sql

# Restore database
docker-compose exec -T postgres psql -U expense_user -d expense_tracker < backup.sql

# Copy files from container
docker cp expense-tracker-api:/app/logs ./logs
```

## 🌐 Network Management

### Network Operations
```bash
# List networks
docker network ls
docker network inspect expense-tracker_expense-tracker-network

# Create network
docker network create expense-tracker-network

# Remove network
docker network rm expense-tracker-network
```

### Network Debugging
```bash
# Test connectivity
docker-compose exec app ping postgres
docker-compose exec app nslookup postgres

# Check port binding
docker-compose ps
netstat -tulpn | grep :8000
```

## 📊 Logging & Debugging

### Log Management
```bash
# View logs
docker-compose logs app
docker-compose logs postgres
docker-compose logs -f --tail=100 app

# Export logs
docker-compose logs app > app.log
docker-compose logs postgres > postgres.log

# Filter logs
docker-compose logs app | grep ERROR
docker-compose logs app | grep -i "database"
```

### Debugging Commands
```bash
# Container shell access
docker-compose exec app bash
docker-compose exec postgres bash

# Check Python environment
docker-compose exec app python --version
docker-compose exec app pip list
docker-compose exec app python -c "import sys; print(sys.path)"

# Database debugging
docker-compose exec postgres psql -U expense_user -l
docker-compose exec postgres psql -U expense_user -d expense_tracker -c "\dt"
```

## 🚀 Production Commands

### Production Deployment
```bash
# Production build
docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml up --build -d

# Scale for production
docker-compose up --scale app=3 -d

# Rolling update
docker-compose up --build -d --scale app=3
docker-compose stop app_1
docker-compose up -d --scale app=3
```

### Maintenance Commands
```bash
# Update application
docker-compose pull
docker-compose up -d

# Database maintenance
docker-compose exec postgres psql -U expense_user -d expense_tracker -c "VACUUM ANALYZE;"

# Clean up
docker system prune
docker system prune -a
```

### Monitoring Commands
```bash
# Resource monitoring
docker stats --no-stream
docker-compose exec app free -h
docker-compose exec app df -h

# Process monitoring
docker-compose exec app ps aux
docker-compose exec app top
```

## 🔧 Troubleshooting Commands

### Common Issues
```bash
# Container won't start
docker-compose logs app
docker ps -a
docker-compose up --build --force-recreate

# Port conflicts
sudo netstat -tulpn | grep :8000
sudo lsof -i :8000

# Permission issues
sudo chown -R $USER:$USER ./logs
sudo usermod -aG docker $USER
```

### Debugging Tools
```bash
# Check container environment
docker-compose exec app env | grep -E "(DATABASE|SECRET)"

# Test database connection
docker-compose exec app python -c "import psycopg2; psycopg2.connect('postgresql://expense_user:expense_password@postgres:5432/expense_tracker')"

# Validate configuration
docker-compose exec app python -c "from src.core.config import get_settings; print(get_settings())"
```

## 📝 Useful Aliases

Add these to your `~/.bashrc` or `~/.zshrc`:

```bash
# Docker aliases
alias dc='docker-compose'
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f'
alias dcb='docker-compose build'
alias dcr='docker-compose restart'

# Expense Tracker specific
alias et-logs='docker-compose logs -f app'
alias et-db='docker-compose exec postgres psql -U expense_user -d expense_tracker'
alias et-shell='docker-compose exec app bash'
alias et-health='curl http://localhost:8000/health'
```

## 🔗 Related Documentation

- [Docker Guide](docker_guide.md) - Complete setup guide
- [Troubleshooting](troubleshooting.md) - Problem resolution
- [Production Deployment](production.md) - Production configurations
