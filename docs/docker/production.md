# Docker Production Deployment Guide

Comprehensive guide for deploying the Expense Tracker API in production using Docker.

## 📋 Table of Contents

- [Production Overview](#production-overview)
- [Security Hardening](#security-hardening)
- [Resource Optimization](#resource-optimization)
- [Monitoring & Logging](#monitoring--logging)
- [Backup & Recovery](#backup--recovery)
- [Scaling & Load Balancing](#scaling--load-balancing)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Production Checklist](#production-checklist)

## 🎯 Production Overview

This guide covers deploying the Expense Tracker API in a production environment with:

- **High Availability**: Multi-instance deployment
- **Security**: Hardened containers and network
- **Monitoring**: Comprehensive logging and metrics
- **Backup**: Automated data protection
- **Performance**: Optimized resource usage

## 🔒 Security Hardening

### Container Security

#### 1. Non-Root User (Already Implemented)
```dockerfile
# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser
```

#### 2. Resource Limits
```yaml
# docker-compose.prod.yaml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
```

#### 3. Network Security
```yaml
# Isolated network
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access

services:
  app:
    networks:
      - frontend
      - backend
  postgres:
    networks:
      - backend  # Only internal access
```

### Environment Security

#### 1. Secret Management
```bash
# Use Docker secrets
echo "your-production-secret-key-32-chars-minimum" | docker secret create jwt_secret -
echo "postgresql://user:pass@postgres:5432/db" | docker secret create db_url -
```

#### 2. Environment Variables
```yaml
# docker-compose.prod.yaml
services:
  app:
    environment:
      DEBUG: "false"
      LOG_LEVEL: "WARNING"
      SECRET_KEY_FILE: /run/secrets/jwt_secret
      DATABASE_URL_FILE: /run/secrets/db_url
    secrets:
      - jwt_secret
      - db_url
```

#### 3. SSL/TLS Configuration
```yaml
# Reverse proxy with SSL
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
```

## ⚡ Resource Optimization

### 1. Multi-Stage Build Optimization
```dockerfile
# Optimized Dockerfile
FROM python:3.10-slim as builder

# Install only build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY requirements/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Production stage
FROM python:3.10-slim as production

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Application setup
WORKDIR /app
COPY --chown=appuser:appuser . /app
USER appuser

EXPOSE 8000
CMD ["python", "run_server.py"]
```

### 2. Database Optimization
```yaml
# PostgreSQL optimization
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: expense_tracker
      POSTGRES_USER: expense_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    command: >
      postgres
      -c shared_preload_libraries=pg_stat_statements
      -c max_connections=200
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c maintenance_work_mem=64MB
      -c checkpoint_completion_target=0.9
      -c wal_buffers=16MB
      -c default_statistics_target=100
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgresql.conf:/etc/postgresql/postgresql.conf
```

### 3. Application Optimization
```yaml
# Production application settings
services:
  app:
    environment:
      # Performance settings
      WORKERS: "4"
      WORKER_CLASS: "uvicorn.workers.UvicornWorker"
      TIMEOUT: "30"
      
      # Database connection pooling
      DB_POOL_SIZE: "20"
      DB_MAX_OVERFLOW: "30"
      
      # Caching
      REDIS_URL: "redis://redis:6379/0"
```

## 📊 Monitoring & Logging

### 1. Structured Logging
```yaml
# Logging configuration
services:
  app:
    environment:
      LOG_LEVEL: "INFO"
      ENABLE_JSON_LOGGING: "true"
      LOG_FORMAT: "json"
    volumes:
      - ./logs:/app/logs
      - /var/log/expense-tracker:/app/logs
```

### 2. Health Checks
```yaml
# Comprehensive health checks
services:
  app:
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health', timeout=5)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
      
  postgres:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U expense_user -d expense_tracker"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### 3. Monitoring Stack
```yaml
# Monitoring services
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      
  redis:
    image: redis:alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
```

## 💾 Backup & Recovery

### 1. Database Backup
```bash
#!/bin/bash
# backup.sh

# Create backup directory
mkdir -p /backups/$(date +%Y%m%d)

# Database backup
docker-compose exec -T postgres pg_dump -U expense_user expense_tracker > /backups/$(date +%Y%m%d)/expense_tracker_$(date +%H%M%S).sql

# Compress backup
gzip /backups/$(date +%Y%m%d)/expense_tracker_$(date +%H%M%S).sql

# Cleanup old backups (keep 30 days)
find /backups -type d -mtime +30 -exec rm -rf {} \;
```

### 2. Automated Backup
```yaml
# Backup service
services:
  backup:
    image: postgres:15-alpine
    volumes:
      - ./backup.sh:/backup.sh
      - ./backups:/backups
      - postgres_data:/var/lib/postgresql/data
    command: /bin/sh -c "while true; do /backup.sh; sleep 86400; done"
    depends_on:
      - postgres
```

### 3. Recovery Process
```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./restore.sh <backup_file.sql.gz>"
    exit 1
fi

# Stop application
docker-compose stop app

# Restore database
gunzip -c $BACKUP_FILE | docker-compose exec -T postgres psql -U expense_user -d expense_tracker

# Start application
docker-compose start app
```

## 🔄 Scaling & Load Balancing

### 1. Horizontal Scaling
```yaml
# Scale application instances
services:
  app:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        failure_action: rollback
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
```

### 2. Load Balancer
```yaml
# Nginx load balancer
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app
```

### 3. Nginx Configuration
```nginx
# nginx.conf
upstream expense_tracker {
    server app_1:8000;
    server app_2:8000;
    server app_3:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://expense_tracker;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔐 SSL/TLS Configuration

### 1. Let's Encrypt SSL
```yaml
# SSL with Let's Encrypt
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-ssl.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
      
  certbot:
    image: certbot/certbot
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt
      - /var/www/certbot:/var/www/certbot
    command: certbot certonly --webroot -w /var/www/certbot -d your-domain.com
```

### 2. SSL Configuration
```nginx
# nginx-ssl.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://expense_tracker;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## ✅ Production Checklist

### Pre-Deployment
- [ ] Change all default passwords and secrets
- [ ] Configure SSL/TLS certificates
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategy
- [ ] Test disaster recovery procedures
- [ ] Set resource limits and quotas
- [ ] Configure firewall rules
- [ ] Set up log aggregation

### Security
- [ ] Use non-root containers
- [ ] Enable read-only filesystems
- [ ] Configure network segmentation
- [ ] Implement secret management
- [ ] Enable audit logging
- [ ] Configure intrusion detection
- [ ] Regular security updates

### Performance
- [ ] Optimize database queries
- [ ] Configure connection pooling
- [ ] Set up caching (Redis)
- [ ] Monitor resource usage
- [ ] Configure auto-scaling
- [ ] Load testing completed
- [ ] CDN configuration

### Monitoring
- [ ] Health checks configured
- [ ] Metrics collection active
- [ ] Log aggregation working
- [ ] Alerting rules defined
- [ ] Dashboard configured
- [ ] Uptime monitoring
- [ ] Performance baselines

### Backup & Recovery
- [ ] Automated backups scheduled
- [ ] Backup verification tested
- [ ] Recovery procedures documented
- [ ] Disaster recovery plan
- [ ] Data retention policies
- [ ] Cross-region replication

## 🚀 Deployment Commands

### Production Deployment
```bash
# Deploy to production
docker-compose -f docker-compose.yaml -f docker-compose.prod.yaml up -d

# Scale application
docker-compose up --scale app=3 -d

# Rolling update
docker-compose up --build -d --scale app=3
docker-compose stop app_1
docker-compose up -d --scale app=3

# Health check
curl -f http://localhost:8000/health || exit 1
```

### Maintenance
```bash
# Update application
docker-compose pull
docker-compose up -d

# Database maintenance
docker-compose exec postgres psql -U expense_user -d expense_tracker -c "VACUUM ANALYZE;"

# Log rotation
docker-compose exec app logrotate /etc/logrotate.conf
```

## 🔗 Related Documentation

- [Docker Guide](docker_guide.md) - Basic setup guide
- [Troubleshooting](troubleshooting.md) - Problem resolution
- [Commands Reference](commands.md) - Command reference
