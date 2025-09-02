# 🚀 Enterprise NL2SQL Service - Quick Start Guide

## 📖 What You Have

You now have a **complete enterprise-grade NL2SQL service** with the following features:

### ✅ Core Features
- **Natural Language to SQL conversion** using OpenAI GPT-4
- **Multiple database support** (PostgreSQL, MySQL, SQLite, etc.)
- **Intelligent schema linking** with ML-based relevance scoring
- **Advanced prompt engineering** with few-shot learning
- **Comprehensive security validation** 
- **Caching system** with Redis for performance
- **User authentication** and authorization
- **Admin dashboard** and monitoring
- **Rate limiting** and quota management
- **Audit logging** and error tracking

### 🏗️ Architecture Components
- **FastAPI Application** - Main NL2SQL service
- **PostgreSQL Database** - User data and query history
- **Redis Cache** - Schema and query caching
- **Nginx Reverse Proxy** - Load balancing and SSL termination
- **Prometheus + Grafana** - Monitoring and visualization
- **Docker Compose** - Complete containerized deployment

## 🚀 Quick Deployment

### 1. Prerequisites
```bash
# Install Docker and Docker Compose
sudo apt update
sudo apt install docker.io docker-compose git
sudo usermod -aG docker $USER
# Log out and back in for group changes
```

### 2. Deploy the Service
```bash
# Clone and navigate to the project
cd /Users/theseus/allai/nl2sql/enterprise-nl2sql

# Run the automated deployment
./deploy.sh

# Follow the prompts to configure your environment
```

### 3. Configure Environment
Edit the `.env` file with your settings:
```bash
# Essential configurations
OPENAI_API_KEY=sk-your-openai-api-key-here
API_KEY=your-secure-api-key
ENVIRONMENT=production

# Optional but recommended
SENTRY_DSN=your-sentry-dsn-for-error-tracking
```

## 🔧 API Usage Examples

### Authentication
```bash
# Login to get access token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@nl2sql.com",
    "password": "admin123"
  }'
```

### Basic Query Execution
```bash
# Execute a natural language query
curl -X POST "http://localhost:8000/api/v1/query/execute" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many customers do we have?",
    "database_url": "postgresql://user:pass@localhost:5432/your_db",
    "include_explanation": true,
    "max_results": 100
  }'
```

### Public API (API Key Authentication)
```bash
# For external integrations
curl -X POST "http://localhost:8000/api/v1/query/public/execute" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me top 10 products by sales",
    "database_url": "postgresql://user:pass@localhost:5432/your_db",
    "max_results": 10
  }'
```

### Bulk Query Processing
```bash
# Process multiple questions at once
curl -X POST "http://localhost:8000/api/v1/query/bulk" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "questions": [
      "How many customers do we have?",
      "What is our total revenue this month?",
      "Which products are selling best?"
    ],
    "database_url": "postgresql://user:pass@localhost:5432/your_db",
    "include_explanation": true
  }'
```

### SQL Validation
```bash
# Validate SQL for security and syntax
curl -X POST "http://localhost:8000/api/v1/query/validate" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d "SELECT COUNT(*) FROM users WHERE created_at > '2024-01-01'"
```

## 📊 Monitoring & Admin

### Access Points
- **API Documentation**: http://localhost:8000/docs
- **Grafana Dashboard**: http://localhost:3000 (admin/admin123)
- **Prometheus Metrics**: http://localhost:9090
- **Admin Endpoints**: http://localhost:8000/api/v1/admin/*

### Admin Operations
```bash
# Get system statistics
curl -X GET "http://localhost:8000/api/v1/admin/stats" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"

# View recent queries
curl -X GET "http://localhost:8000/api/v1/admin/queries/recent?limit=50" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"

# Manage users
curl -X POST "http://localhost:8000/api/v1/admin/users/manage" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "action": "activate",
    "reason": "Account verified"
  }'
```

## 🔒 Security Features

### Built-in Security
- **SQL Injection Prevention** - Comprehensive validation
- **Rate Limiting** - Configurable per user/API key
- **Authentication** - JWT tokens and API keys
- **Authorization** - Role-based permissions
- **Audit Logging** - All actions tracked
- **Input Sanitization** - All inputs validated

### Security Configuration
```python
# In .env file
API_KEY=your-secure-32-char-api-key
JWT_SECRET_KEY=your-jwt-secret-key
RATE_LIMIT_REQUESTS=100  # per hour
MAX_QUERY_TIME=30        # seconds
```

## 📈 Performance Optimization

### Caching Strategy
- **Schema Caching** - Database schemas cached for 24 hours
- **Query Results** - Frequently asked questions cached
- **User Sessions** - Authentication tokens cached
- **ML Embeddings** - Table embeddings cached for fast retrieval

### Database Optimization
- **Connection Pooling** - Efficient database connections
- **Query Timeouts** - Prevent long-running queries
- **Index Optimization** - Proper indexing on key tables
- **Result Limiting** - Configurable result set limits

## 🛠️ Management Commands

### Service Management
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f nl2sql-api

# Restart services
docker-compose restart

# Update deployment
./deploy.sh --update

# Clean up resources
./deploy.sh --cleanup
```

### Database Management
```bash
# Backup database
docker-compose exec postgres pg_dump -U nl2sql nl2sql_db > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U nl2sql -d nl2sql_db

# Access database directly
docker-compose exec postgres psql -U nl2sql -d nl2sql_db
```

## 🔧 Customization

### Adding Custom Prompt Templates
```python
# In app/services/nl2sql_service.py
custom_template = PromptTemplate(
    system_prompt="You are a domain-specific SQL expert for retail analytics.",
    user_prompt="""
    Database Schema: {schema_info}
    Business Context: {business_context}
    Question: {question}
    
    Generate SQL optimized for retail analytics:
    <sql>
    """,
    temperature=0.1
)
```

### Custom Business Rules
```python
# Add to prompt builder
business_rules = """
- Revenue calculations must exclude refunds
- Customer lifetime value includes all purchases
- Seasonal adjustments apply to Q4 data
- Regional sales include tax adjustments
"""
```

### Adding New Database Types
```python
# In app/models/schemas.py
class DatabaseType(str, Enum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SNOWFLAKE = "snowflake"  # Add new types
    BIGQUERY = "bigquery"
```

## 🚨 Troubleshooting

### Common Issues
1. **OpenAI API Key Issues**
   ```bash
   # Verify API key
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connectivity
   docker-compose exec nl2sql-api python -c "
   from sqlalchemy import create_engine
   engine = create_engine('$DATABASE_URL')
   print('Connection successful!')
   "
   ```

3. **Redis Cache Issues**
   ```bash
   # Test Redis connection
   docker-compose exec redis redis-cli ping
   ```

### Performance Issues
- Monitor memory usage: `docker stats`
- Check slow queries in logs
- Optimize database queries
- Adjust cache TTL settings

## 📞 Production Checklist

### Before Going Live
- [ ] Configure SSL certificates
- [ ] Set up domain name and DNS
- [ ] Configure firewall rules
- [ ] Set up monitoring alerts
- [ ] Configure automated backups
- [ ] Review security settings
- [ ] Load test the API
- [ ] Set up log rotation
- [ ] Configure rate limiting
- [ ] Test disaster recovery

### Environment Variables for Production
```bash
ENVIRONMENT=production
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=postgresql://secure_user:strong_password@db_host:5432/nl2sql_prod
REDIS_URL=redis://redis_host:6379
OPENAI_API_KEY=sk-your-production-api-key
SENTRY_DSN=https://your-sentry-dsn
LOG_LEVEL=INFO
CORS_ORIGINS=["https://yourdomain.com"]
```

## 🎯 Next Steps

1. **Test the API** with your own database
2. **Customize prompts** for your domain
3. **Set up monitoring** alerts
4. **Configure SSL** for HTTPS
5. **Add custom authentication** if needed
6. **Scale horizontally** if required
7. **Integrate with your applications**

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Grafana Dashboards**: Pre-configured monitoring
- **Example Queries**: Check the test files
- **Custom Integration**: Extend the service for your needs

---

**🎉 You now have a production-ready enterprise NL2SQL service!**

The service is designed to handle enterprise workloads with proper security, monitoring, and scalability features. All components are containerized and ready for deployment in any environment.
