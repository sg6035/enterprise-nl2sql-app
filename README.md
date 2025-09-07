# 🚀 Enterprise NL2SQL Service - Local Ollama Integration

## 📋 Overview

The Enterprise NL2SQL Service is a production-ready application that converts natural language questions into SQL queries using **local Ollama LLMs**. This guide provides complete instructions for deploying and managing the service with **Phi-3 3.8B model** running locally, eliminating cloud API dependencies and costs.

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
                                │                        │
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Prometheus     │    │  Local Ollama   │
                       │   Monitoring     │───►│   Phi-3 3.8B    │
                       └──────────────────┘    └─────────────────┘
                                │
                       ┌──────────────────┐
                       │    Grafana       │
                       │   Dashboard      │
                       └──────────────────┘
```

## 🔧 Prerequisites

### System Requirements
- **Operating System**: Linux/macOS (Ubuntu 20.04+ recommended for Linux)
- **Memory**: Minimum 8GB RAM (16GB recommended for local LLM)
- **CPU**: 4+ cores (Phi-3 3.8B model ~20 second inference time)
- **Storage**: 50GB+ SSD (includes 2.2GB for Phi-3 model)
- **Network**: No internet required for inference (local Ollama)

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git
- **Ollama** (for local LLM inference)
- SSL Certificates (for HTTPS)

### Local LLM Setup
- **Ollama installation** (see Quick Start section)
- **Phi-3 3.8B model** (automatic download: 2.2GB)
- **No API keys required** for inference

## 🚀 Quick Start Deployment

### 1. Install Ollama and Download Phi-3 Model
```bash
# Install Ollama (macOS)
curl -fsSL https://ollama.com/install.sh | sh

# For Linux
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve

# Download Phi-3 3.8B model (in another terminal)
ollama pull phi3:3.8b

# Verify model is available
ollama list
```

### 2. Clone the Repository
```bash
git clone <repository-url>
cd enterprise-nl2sql
```

### 3. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

**Required Environment Variables for Local Ollama:**
```bash
# API Configuration
ENVIRONMENT=production
API_KEY=test-api-key
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Local Ollama Configuration
OLLAMA_BASE_URL=http://host.docker.internal:11434
LLM_MODEL=phi3:3.8b
OLLAMA_MODEL=phi3:3.8b

# Database
DATABASE_URL=postgresql://nl2sql:nl2sql123@postgres:5432/nl2sql_db

# Cache
REDIS_URL=redis://redis:6379

# Optional Monitoring
SENTRY_DSN=https://your-sentry-dsn-here
```

### 4. Deploy with Docker Compose
```bash
# Ensure Ollama is running and accessible
curl http://localhost:11434/api/tags

# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f nl2sql-api
```

### 5. Verify Deployment
```bash
# Health check
curl http://localhost:8000/health

# Test NL2SQL with local Ollama
curl -X POST "http://localhost:8000/api/v1/query/public/execute" \
  -H "Authorization: Bearer test-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many users are there?",
    "database_url": "postgresql://nl2sql:nl2sql123@postgres:5432/nl2sql_db"
  }'

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
# For local development, use the test API key
API_KEY=test-api-key

# For production, generate secure API keys
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

### Local Ollama Configuration
```python
# In .env file
OLLAMA_BASE_URL=http://host.docker.internal:11434  # Docker to host connection
LLM_MODEL=phi3:3.8b                                # Phi-3 3.8B model (2.2GB)
OLLAMA_MODEL=phi3:3.8b                             # Model for Ollama service
LLM_TEMPERATURE=0.0                                # Deterministic responses
MAX_TOKENS=2000                                    # Maximum response length
LLM_TIMEOUT=60                                     # Request timeout (20s typical)
```

### Alternative Models
```bash
# Larger model (better accuracy, slower inference)
ollama pull llama3.1:8b      # 4.7GB model, ~45 second inference

# Smaller model (faster inference, lower accuracy)  
ollama pull phi3:mini        # 2.3GB model, ~15 second inference

# Update .env file accordingly
LLM_MODEL=llama3.1:8b        # or phi3:mini
OLLAMA_MODEL=llama3.1:8b     # or phi3:mini
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

# Basic load test with local Ollama
ab -n 10 -c 2 -H "Authorization: Bearer test-api-key" \
   -T "application/json" \
   -p test-query.json \
   http://localhost:8000/api/v1/query/public/execute

# Note: Use lower concurrency (-c 2) due to local LLM processing time
```

**test-query.json:**
```json
{
  "question": "How many users are there?",
  "database_url": "postgresql://nl2sql:nl2sql123@postgres:5432/nl2sql_db",
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

4. **Local Ollama Connection Issues**
   ```bash
   # Test Ollama connectivity from container
   docker-compose exec nl2sql-api curl http://host.docker.internal:11434/api/tags
   
   # Check Ollama service status
   curl http://localhost:11434/api/tags
   
   # Verify Phi-3 model is loaded
   curl http://localhost:11434/api/show -d '{"name": "phi3:3.8b"}'
   ```

5. **Slow Response Times**
   ```bash
   # Phi-3 3.8B typical response time: ~20 seconds
   # Monitor inference time in logs
   docker-compose logs -f nl2sql-api | grep "inference_time"
   
   # Consider upgrading to faster hardware or larger model
   # Check system resources during inference
   docker stats
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

### Ollama Model Management
```bash
# List available models
ollama list

# Pull different models
ollama pull codellama:7b       # For code generation
ollama pull mistral:7b         # Alternative general model

# Remove models to save space
ollama rm phi3:3.8b

# Update model
ollama pull phi3:3.8b  # Re-downloads latest version
```

### Custom Prompt Templates for Phi-3
```python
# Optimized for Phi-3 3.8B in app/services/nl2sql_service.py
phi3_template = PromptTemplate(
    system_prompt="You are a SQL expert. Generate only valid SQL.",
    user_prompt="""Examples:
Question: How many users?
SQL: SELECT COUNT(*) FROM users;

Tables: {tables}
Question: {question}
SQL:""",
    temperature=0.0  # Deterministic for Phi-3
)
```

### Local Model Performance Optimization
```python
# Environment variables for better performance
OLLAMA_NUM_PARALLEL=1          # Single request processing
OLLAMA_NUM_THREAD=8            # CPU threads for inference
OLLAMA_HOST=0.0.0.0           # Bind to all interfaces
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
