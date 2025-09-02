# 🚀 Enterprise NL2SQL Service - Production Deployment Guide

## 📋 Overview

The Enterprise NL2SQL Service is a production-ready application that converts natural language questions into SQL queries using Large Language Models (LLMs). This guide provides complete instructions for deploying and managing the service in a production environment.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│    Frontend     │───►│   Nginx Proxy    │───►│   NL2SQL API    │
│   (Optional)    │    │   Load Balancer  │    │   (FastAPI)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                       ┌──────────────────┐    ┌─────────────────┐
                       │   PostgreSQL     │◄───│      Redis      │
                       │   Database       │    │     Cache       │
                       └──────────────────┘    └─────────────────┘
                                │
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Prometheus     │    │    Grafana      │
                       │   Monitoring     │───►│   Dashboard     │
                       └──────────────────┘    └─────────────────┘
```

## 🔧 Prerequisites

### System Requirements
- **Operating System**: Linux (Ubuntu 20.04+ recommended)
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **CPU**: 4+ cores
- **Storage**: 50GB+ SSD
- **Network**: Internet connectivity for LLM API calls

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git
- SSL Certificates (for HTTPS)

### API Keys Required
- **OpenAI API Key** (or other LLM provider)
- **Sentry DSN** (optional, for error tracking)

## 🚀 Quick Start Deployment

### 1. Clone the Repository
```bash
git clone <repository-url>
cd enterprise-nl2sql
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

**Required Environment Variables:**
```bash
# API Configuration
ENVIRONMENT=production
API_KEY=your-secure-api-key-here
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# LLM Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Database
DATABASE_URL=postgresql://nl2sql:nl2sql123@postgres:5432/nl2sql_db

# Cache
REDIS_URL=redis://redis:6379

# Optional Monitoring
SENTRY_DSN=https://your-sentry-dsn-here
```

### 3. Deploy with Docker Compose
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f nl2sql-api
```

### 4. Verify Deployment
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

## 🔐 Security Configuration

### SSL/TLS Setup
1. **Obtain SSL Certificates**:
   ```bash
   # Using Let's Encrypt (recommended)
   sudo apt install certbot
   sudo certbot certonly --standalone -d your-domain.com
   ```

2. **Configure Nginx**:
   ```bash
   # Copy SSL certificates
   mkdir -p nginx/ssl
   cp /etc/letsencrypt/live/your-domain.com/* nginx/ssl/
   ```

### API Key Management
```bash
# Generate secure API keys
python -c "import secrets; print('API_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

### Database Security
- Use strong passwords
- Enable SSL connections
- Regular backups
- Network isolation

## 📊 Monitoring & Observability

### Prometheus Metrics
Access at: `http://localhost:9090`

**Key Metrics:**
- Request rate and latency
- Error rates
- Database performance
- Cache hit rates
- Memory and CPU usage

### Grafana Dashboard
Access at: `http://localhost:3000`
- Username: `admin`
- Password: `admin123`

**Pre-configured Dashboards:**
- API Performance
- Database Metrics
- Error Analysis
- User Activity

### Logging
```bash
# View application logs
docker-compose logs -f nl2sql-api

# View all logs
docker-compose logs -f

# Log files location
tail -f logs/app.log
tail -f logs/nginx/access.log
```

## 🔧 Configuration Options

### LLM Configuration
```python
# In .env file
LLM_MODEL=gpt-4                    # OpenAI model
LLM_TEMPERATURE=0.0               # Response consistency
MAX_TOKENS=2000                   # Maximum response length
LLM_TIMEOUT=60                    # Request timeout
```

### Performance Tuning
```python
# Database connections
DATABASE_POOL_SIZE=10             # Connection pool size
DATABASE_MAX_OVERFLOW=20          # Max overflow connections
DATABASE_POOL_TIMEOUT=30          # Connection timeout

# Cache settings
CACHE_TTL=3600                    # Cache TTL in seconds
SCHEMA_CACHE_TTL=86400           # Schema cache TTL

# Query limits
MAX_QUERY_TIME=30                 # SQL execution timeout
MAX_RESULTS_DEFAULT=100           # Default result limit
MAX_RESULTS_LIMIT=1000           # Maximum result limit
```

### Rate Limiting
```python
RATE_LIMIT_REQUESTS=100           # Requests per window
RATE_LIMIT_WINDOW=3600           # Window in seconds
```

## 🧪 Testing

### Health Checks
```bash
# API health check
curl -f http://localhost:8000/health

# Database connectivity
docker-compose exec postgres pg_isready -U nl2sql

# Redis connectivity
docker-compose exec redis redis-cli ping
```

### Load Testing
```bash
# Install Apache Bench
sudo apt install apache2-utils

# Basic load test
ab -n 1000 -c 10 -H "Authorization: Bearer your-api-key" \
   -T "application/json" \
   -p test-query.json \
   http://localhost:8000/api/v1/query/public/execute
```

**test-query.json:**
```json
{
  "question": "How many users are there?",
  "database_url": "sqlite:///test.db",
  "max_results": 10
}
```

## 🔄 Backup & Recovery

### Database Backup
```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U nl2sql nl2sql_db > backup_${DATE}.sql

# Restore from backup
cat backup_20240115_120000.sql | docker-compose exec -T postgres psql -U nl2sql -d nl2sql_db
```

### Configuration Backup
```bash
# Backup configuration
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env docker-compose.yml nginx/
```

## 📈 Scaling

### Horizontal Scaling
```yaml
# docker-compose.override.yml
version: '3.8'
services:
  nl2sql-api:
    deploy:
      replicas: 3
    environment:
      - WORKERS=4
  
  nginx:
    depends_on:
      - nl2sql-api
```

### Database Scaling
- Read replicas for query distribution
- Connection pooling optimization
- Database partitioning for large datasets

### Cache Optimization
- Redis cluster for high availability
- Cache warming strategies
- TTL optimization

## 🐛 Troubleshooting

### Common Issues

1. **Service Won't Start**
   ```bash
   # Check logs
   docker-compose logs nl2sql-api
   
   # Check environment variables
   docker-compose config
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connection
   docker-compose exec nl2sql-api python -c "
   from app.config import settings
   print(f'Database URL: {settings.DATABASE_URL}')
   "
   ```

3. **High Memory Usage**
   ```bash
   # Monitor memory usage
   docker stats
   
   # Optimize model loading
   # Consider using smaller models or model quantization
   ```

4. **LLM API Errors**
   ```bash
   # Check API key
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   
   # Monitor rate limits
   tail -f logs/app.log | grep -i "rate limit"
   ```

### Log Analysis
```bash
# Error patterns
grep -i error logs/app.log | tail -20

# Performance issues
grep -i "slow query" logs/app.log

# Security alerts
grep -i "security" logs/app.log
```

## 🔒 Security Best Practices

### Application Security
- Regular dependency updates
- Security scanning
- Input validation
- SQL injection prevention
- Rate limiting
- Authentication/authorization

### Infrastructure Security
- Network segmentation
- Firewall configuration
- Regular security patches
- SSL/TLS encryption
- Secrets management

### Data Protection
- Data encryption at rest
- Secure API key storage
- PII data handling
- GDPR compliance
- Audit logging

## 📋 Maintenance

### Regular Tasks
```bash
# Weekly maintenance script
#!/bin/bash

# Update containers
docker-compose pull
docker-compose up -d

# Clean up old images
docker image prune -f

# Backup database
./scripts/backup.sh

# Check disk space
df -h

# Check logs for errors
grep -i error logs/app.log | tail -50
```

### Performance Monitoring
- Monitor response times
- Check error rates
- Analyze cache hit rates
- Review resource utilization
- Database performance tuning

## 🚀 Advanced Features

### Custom Prompt Templates
```python
# Add custom templates in app/services/nl2sql_service.py
custom_template = PromptTemplate(
    system_prompt="Your custom system prompt",
    user_prompt="Your custom user prompt with {variables}",
    temperature=0.1
)
```

### Multi-LLM Support
```python
# Configure multiple LLM providers
LLM_PROVIDERS = {
    'openai': 'gpt-4',
    'anthropic': 'claude-3',
    'azure': 'gpt-4-32k'
}
```

### Custom Security Rules
```python
# Add custom security validation
def custom_security_check(sql_query: str) -> bool:
    # Your custom security logic
    return True
```

## 📞 Support

### Monitoring Alerts
Set up alerts for:
- High error rates (>5%)
- Slow response times (>5s)
- High memory usage (>80%)
- Database connection issues
- Cache failures

### Health Endpoints
- `/health` - Basic health check
- `/health/detailed` - Detailed component status
- `/metrics` - Prometheus metrics

### Documentation
- API Documentation: `http://localhost:8000/docs`
- Admin Dashboard: Custom admin interface
- Monitoring: Grafana dashboards

---

## 📄 License

This enterprise NL2SQL service is designed for production use with comprehensive security, monitoring, and scalability features.

For additional support or custom enterprise features, please contact the development team.
