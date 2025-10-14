# Docker Documentation

This directory contains comprehensive documentation for deploying and managing the Expense Tracker API using Docker.

## 📁 Documentation Structure

- **[Docker Guide](docker_guide.md)** - Complete Docker setup and usage guide
- **[Troubleshooting](troubleshooting.md)** - Common Docker issues and solutions
- **[Production Deployment](production.md)** - Production-ready Docker deployment
- **[Docker Commands Reference](commands.md)** - Quick reference for Docker commands

## 🚀 Quick Start

```bash
# Clone and navigate to project
cd /path/to/Expense-Tracker

# Start the application with Docker Compose
docker-compose up --build -d

# Check application health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/api/v1/docs
```

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB+ available RAM
- 5GB+ available disk space

## 🔧 What's Included

- **Multi-stage Dockerfile** with security best practices
- **Docker Compose** configuration for development and production
- **PostgreSQL database** container with initialization scripts
- **Health checks** and monitoring
- **Volume management** for data persistence
- **Environment configuration** management

## 📖 Documentation Overview

### Docker Guide
Complete walkthrough of Docker setup, including:
- Container architecture
- Build process explanation
- Environment configuration
- Development workflow

### Troubleshooting
Solutions for common issues:
- Build failures
- Runtime errors
- Database connection issues
- Performance problems

### Production Deployment
Production-ready configurations:
- Security hardening
- Resource optimization
- Monitoring setup
- Backup strategies

### Commands Reference
Quick reference for all Docker commands used in the project.

## 🆘 Getting Help

If you encounter issues not covered in the troubleshooting guide:

1. Check the application logs: `docker-compose logs -f app`
2. Verify container status: `docker ps`
3. Check resource usage: `docker stats`
4. Review the troubleshooting documentation

## 🔗 Related Documentation

- [Deployment Guide](../deployment_guide.md) - General deployment information
- [Configuration Guide](../configuration_guide.md) - Application configuration
- [Architecture](../architecture.md) - System architecture overview
