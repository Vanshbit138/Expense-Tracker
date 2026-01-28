# Deployment Guide

Complete guide for deploying the Expense Tracker application to various environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Monitoring and Logging](#monitoring-and-logging)
- [Backup and Recovery](#backup-and-recovery)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Python**: 3.10 or higher
- **PostgreSQL**: 12 or higher
- **Memory**: Minimum 512MB RAM
- **Storage**: Minimum 1GB free space
- **Network**: Port 8000 available (or configurable)

### Software Dependencies

- Git
- Python virtual environment
- PostgreSQL client
- pip (Python package manager)

## Local Development

### 1. Clone Repository

```bash
git clone <repository-url>
cd Expense-Tracker
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install main dependencies
pip install -r requirements/requirements.txt

# Install development dependencies
pip install -r requirements/dev.txt
```

### 4. Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit configuration
nano .env
```

**Required configuration:**
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/expense_tracker
SECRET_KEY=your-secret-key-here-change-in-production
```

### 5. Set Up Database

```bash
# Create PostgreSQL database
createdb expense_tracker

# Run migrations
alembic upgrade head
```

### 6. Run Application

```bash
# Development server
python run_server.py

# Or using uvicorn directly
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 7. Verify Installation

```bash
# Check health endpoint
curl http://localhost:8000/health

# Check API documentation
open http://localhost:8000/api/v1/docs
```

## Docker Deployment

### 1. Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Create Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/expense_tracker
      - SECRET_KEY=your-secret-key-here
      - DEBUG=False
      - LOG_LEVEL=INFO
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=expense_tracker
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
```

### 3. Create Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:8000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 4. Deploy with Docker

```bash
# Build and start services
docker-compose up -d

# Check logs
docker-compose logs -f app

# Check status
docker-compose ps

# Stop services
docker-compose down
```

## Production Deployment

### 1. Server Preparation

#### Ubuntu/Debian Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.10 python3.10-venv postgresql postgresql-contrib nginx git

# Create application user
sudo useradd -m -s /bin/bash expense-tracker
sudo usermod -aG sudo expense-tracker
```

#### CentOS/RHEL Server

```bash
# Update system
sudo yum update -y

# Install required packages
sudo yum install -y python3.10 postgresql-server postgresql-contrib nginx git

# Initialize PostgreSQL
sudo postgresql-setup initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### 2. Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE expense_tracker;
CREATE USER expense_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE expense_tracker TO expense_user;

# Exit PostgreSQL
\q
```

### 3. Application Deployment

```bash
# Switch to application user
sudo su - expense-tracker

# Clone repository
git clone <repository-url> /home/expense-tracker/app
cd /home/expense-tracker/app

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements/requirements.txt

# Configure environment
cp env.example .env
nano .env
```

**Production environment configuration:**
```bash
DATABASE_URL=postgresql://expense_user:secure_password@localhost:5432/expense_tracker
SECRET_KEY=production-secret-key-very-secure
DEBUG=False
LOG_LEVEL=WARNING
ENABLE_JSON_LOGGING=True
```

### 4. Run Database Migrations

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
alembic upgrade head
```

### 5. Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/expense-tracker.service
```

**Service configuration:**
```ini
[Unit]
Description=Expense Tracker API
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=expense-tracker
Group=expense-tracker
WorkingDirectory=/home/expense-tracker/app
Environment=PATH=/home/expense-tracker/app/venv/bin
ExecStart=/home/expense-tracker/app/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 6. Configure Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/expense-tracker
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/expense-tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 7. Start Services

```bash
# Enable and start application
sudo systemctl enable expense-tracker
sudo systemctl start expense-tracker

# Check status
sudo systemctl status expense-tracker

# Check logs
sudo journalctl -u expense-tracker -f
```

### 8. SSL Configuration (Optional)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

## Cloud Deployment

### AWS Deployment

#### 1. EC2 Instance

```bash
# Launch EC2 instance (Ubuntu 20.04 LTS)
# Instance type: t3.micro or larger
# Security groups: Allow HTTP (80), HTTPS (443), SSH (22)

# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip
```

#### 2. RDS Database

```bash
# Create RDS PostgreSQL instance
# Engine: PostgreSQL 13
# Instance class: db.t3.micro
# Storage: 20 GB
# Security group: Allow inbound from EC2 security group
```

#### 3. Application Deployment

```bash
# Follow production deployment steps
# Update DATABASE_URL to RDS endpoint
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/expense_tracker
```

### Google Cloud Platform

#### 1. Compute Engine

```bash
# Create VM instance
gcloud compute instances create expense-tracker \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --machine-type=e2-micro \
    --zone=us-central1-a
```

#### 2. Cloud SQL

```bash
# Create Cloud SQL instance
gcloud sql instances create expense-tracker-db \
    --database-version=POSTGRES_13 \
    --tier=db-f1-micro \
    --region=us-central1
```

### Heroku Deployment

#### 1. Create Heroku App

```bash
# Install Heroku CLI
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev
```

#### 2. Configure Environment

```bash
# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set LOG_LEVEL=WARNING
```

#### 3. Deploy

```bash
# Add Heroku remote
git remote add heroku https://git.heroku.com/your-app-name.git

# Deploy
git push heroku main

# Run migrations
heroku run alembic upgrade head
```

### DigitalOcean App Platform

#### 1. Create App

```yaml
# .do/app.yaml
name: expense-tracker
services:
- name: api
  source_dir: /
  github:
    repo: your-username/Expense-Tracker
    branch: main
  run_command: uvicorn src.api.main:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DATABASE_URL
    value: ${db.DATABASE_URL}
  - key: SECRET_KEY
    value: your-secret-key
  - key: DEBUG
    value: "False"

databases:
- name: db
  engine: PG
  version: "13"
```

## Monitoring and Logging

### Application Monitoring

#### 1. Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check script
#!/bin/bash
# health-check.sh
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ $response -eq 200 ]; then
    echo "Application is healthy"
    exit 0
else
    echo "Application is unhealthy (HTTP $response)"
    exit 1
fi
```

#### 2. Log Monitoring

```bash
# Monitor application logs
sudo journalctl -u expense-tracker -f

# Monitor Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

#### 3. System Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Monitor system resources
htop
iotop
nethogs
```

### Log Aggregation

#### 1. ELK Stack

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:7.15.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5044:5044"

  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

#### 2. Prometheus and Grafana

```yaml
# docker-compose.monitoring.yml
version: '3.8'
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
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## Backup and Recovery

### Database Backup

#### 1. Automated Backup Script

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/home/expense-tracker/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="expense_tracker_$DATE.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
pg_dump -h localhost -U expense_user -d expense_tracker > $BACKUP_DIR/$BACKUP_FILE

# Compress backup
gzip $BACKUP_DIR/$BACKUP_FILE

# Remove backups older than 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

#### 2. Cron Job for Backups

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /home/expense-tracker/backup.sh
```

### Application Backup

#### 1. Code Backup

```bash
#!/bin/bash
# code-backup.sh
BACKUP_DIR="/home/expense-tracker/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
tar -czf $BACKUP_DIR/code_$DATE.tar.gz /home/expense-tracker/app

# Remove backups older than 30 days
find $BACKUP_DIR -name "code_*.tar.gz" -mtime +30 -delete
```

### Recovery Procedures

#### 1. Database Recovery

```bash
# Restore from backup
gunzip -c expense_tracker_20240101_020000.sql.gz | psql -h localhost -U expense_user -d expense_tracker
```

#### 2. Application Recovery

```bash
# Restore application code
tar -xzf code_20240101_020000.tar.gz -C /
```

## Troubleshooting

### Common Issues

#### 1. Application Won't Start

**Check logs:**
```bash
sudo journalctl -u expense-tracker -f
```

**Common causes:**
- Database connection issues
- Invalid configuration
- Port already in use
- Missing dependencies

#### 2. Database Connection Issues

**Test connection:**
```bash
psql -h localhost -U expense_user -d expense_tracker
```

**Check PostgreSQL status:**
```bash
sudo systemctl status postgresql
```

#### 3. Nginx Issues

**Test configuration:**
```bash
sudo nginx -t
```

**Check logs:**
```bash
sudo tail -f /var/log/nginx/error.log
```

#### 4. Performance Issues

**Monitor resources:**
```bash
htop
iotop
nethogs
```

**Check database performance:**
```sql
-- Check active connections
SELECT * FROM pg_stat_activity;

-- Check slow queries
SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC;
```

### Debug Mode

**Enable debug mode temporarily:**
```bash
# Update environment
echo "DEBUG=True" >> .env

# Restart service
sudo systemctl restart expense-tracker
```

**Check debug logs:**
```bash
sudo journalctl -u expense-tracker -f
```

### Performance Optimization

#### 1. Database Optimization

```sql
-- Create indexes for better performance
CREATE INDEX idx_expenses_user_id ON expenses(user_id);
CREATE INDEX idx_expenses_date ON expenses(expense_date);
CREATE INDEX idx_expenses_category ON expenses(category_id);
```

#### 2. Application Optimization

```bash
# Increase worker processes
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Use Gunicorn for production
pip install gunicorn
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### 3. Nginx Optimization

```nginx
# nginx.conf optimizations
worker_processes auto;
worker_connections 1024;

http {
    # Enable gzip compression
    gzip on;
    gzip_types text/plain application/json application/javascript text/css;

    # Enable caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Security Considerations

### 1. Firewall Configuration

```bash
# Configure UFW
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
```

### 2. SSL/TLS Configuration

```bash
# Use Let's Encrypt for free SSL
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. Database Security

```sql
-- Create read-only user for monitoring
CREATE USER monitor_user WITH PASSWORD 'monitor_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO monitor_user;
```

### 4. Application Security

```bash
# Run application as non-root user
sudo useradd -r -s /bin/false expense-tracker

# Set proper file permissions
sudo chown -R expense-tracker:expense-tracker /home/expense-tracker/app
sudo chmod 755 /home/expense-tracker/app
```

## Maintenance

### 1. Regular Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python dependencies
pip install -r requirements/requirements.txt --upgrade
```

### 2. Log Rotation

```bash
# Configure logrotate
sudo nano /etc/logrotate.d/expense-tracker
```

**Logrotate configuration:**
```
/home/expense-tracker/app/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 expense-tracker expense-tracker
}
```

### 3. Database Maintenance

```sql
-- Vacuum database regularly
VACUUM ANALYZE;

-- Check database size
SELECT pg_size_pretty(pg_database_size('expense_tracker'));
```

## Support

For deployment issues:

1. Check this guide
2. Review application logs
3. Verify configuration
4. Test database connectivity
5. Check system resources
6. Open an issue with deployment details
