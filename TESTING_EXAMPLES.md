# Enterprise NL2SQL Testing Examples - Ollama Phi-3 Integration

## Prerequisites
Ensure Ollama is running with Phi-3 model loaded:
```bash
# Start Ollama
ollama serve &

# Verify Phi-3 model is available
ollama list | grep phi3:3.8b

# If not available, download it
ollama pull phi3:3.8b

# Test Ollama connectivity
curl http://localhost:11434/api/tags
```

## Authentication
```bash
# For development/testing, use the test API key
API_KEY="test-api-key"

# For JWT authentication (if needed)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'

# Store the token (replace with actual token from response)
JWT_TOKEN="your_jwt_token_here"
```

## Health Check
```bash
# API health check
curl -X GET "http://localhost:8000/health"

# Ollama health check
curl -X GET "http://localhost:11434/api/tags"

# Verify Phi-3 model status
curl -X POST "http://localhost:11434/api/show" \
  -H "Content-Type: application/json" \
  -d '{"name": "phi3:3.8b"}'
```

## NL2SQL Query Execution with Phi-3
```bash
# Simple count query (expect ~20 second response time)
curl -X POST "http://localhost:8000/api/v1/query/public/execute" \
  -H "Authorization: Bearer test-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many users are there?",
    "database_url": "postgresql://nl2sql:nl2sql123@postgres:5432/nl2sql_db",
    "include_explanation": true,
    "max_results": 100
  }'

# Expected response:
# {
#   "sql_query": "SELECT COUNT(*) FROM users;",
#   "results": [{"count": 2}],
#   "execution_time": 19.8,
#   "row_count": 1,
#   "inference_time": 18.5
# }

# Complex analytical query
curl -X POST "http://localhost:8000/api/v1/query/public/execute" \
  -H "Authorization: Bearer test-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me the users with their email domains",
    "database_url": "postgresql://nl2sql:nl2sql123@postgres:5432/nl2sql_db",
    "include_explanation": true,
    "max_results": 100
  }'

# Time-based query testing Phi-3 understanding
curl -X POST "http://localhost:8000/api/v1/query/public/execute" \
  -H "Authorization: Bearer test-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "List all users",
    "database_url": "postgresql://nl2sql:nl2sql123@postgres:5432/nl2sql_db",
    "include_explanation": true,
    "max_results": 10
  }'
```

## SQL Validation
```bash
curl -X POST "http://localhost:8000/api/v1/query/validate" \
  -H "Authorization: Bearer test-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "sql_query": "SELECT COUNT(*) FROM users;",
    "database_url": "postgresql://nl2sql:nl2sql123@postgres:5432/nl2sql_db"
  }'
```

## Ollama Direct Testing
```bash
# Test Phi-3 model directly
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi3:3.8b",
    "prompt": "Generate SQL to count users: SELECT",
    "stream": false
  }'

# Chat-style interaction
curl -X POST http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi3:3.8b",
    "messages": [
      {"role": "user", "content": "Write SQL to count all users in a table called users"}
    ],
    "stream": false
  }'
```

## Performance Testing
```bash
# Test inference timing
time curl -X POST "http://localhost:8000/api/v1/query/public/execute" \
  -H "Authorization: Bearer test-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many users are there?",
    "database_url": "postgresql://nl2sql:nl2sql123@postgres:5432/nl2sql_db"
  }'

# Expected timing: ~20 seconds total (18s inference + 2s processing)
```

## Admin Operations
```bash
# List all users (admin only - requires JWT)
curl -X GET "http://localhost:8000/api/v1/admin/users" \
  -H "Authorization: Bearer $JWT_TOKEN"

# Get query metrics
curl -X GET "http://localhost:8000/api/v1/admin/metrics" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

## Database Operations
```bash
# Connect to database directly
docker-compose exec postgres psql -U nl2sql -d nl2sql_db

# View sample data
\dt                              # List tables
SELECT * FROM users LIMIT 5;    # View user data (should show 2 test users)
```

## Monitoring & Metrics
```bash
# Prometheus metrics
curl http://localhost:9090/api/v1/query?query=up

# API metrics endpoint
curl http://localhost:8000/metrics

# Ollama metrics (if available)
curl http://localhost:11434/metrics
```

## Expected Responses

### Successful Query Response (Phi-3):
```json
{
  "sql_query": "SELECT COUNT(*) FROM users;",
  "results": [{"count": 2}],
  "explanation": "This query counts the total number of users in the database using Phi-3 3.8B model",
  "execution_time": 1.2,
  "inference_time": 18.5,
  "row_count": 1,
  "error": null,
  "metadata": {
    "model": "phi3:3.8b",
    "template_type": "minimal",
    "relevant_tables": ["users"],
    "schema_tables_count": 1,
    "cleaned_sql": true
  },
  "query_id": "abc123...",
  "cache_hit": false
}
```

### Error Response:
```json
{
  "sql_query": "",
  "results": [],
  "explanation": "",
  "execution_time": 0.05,
  "inference_time": 0.0,
  "row_count": 0,
  "error": "Ollama connection failed: Connection refused",
  "metadata": {
    "model": "phi3:3.8b",
    "error_type": "connection_error"
  },
  "query_id": "def456...",
  "cache_hit": false
}
```

### Ollama Model Response:
```json
{
  "model": "phi3:3.8b",
  "created_at": "2024-01-21T10:30:00Z",
  "response": "SELECT COUNT(*) FROM users;",
  "done": true,
  "total_duration": 18500000000,
  "load_duration": 500000000,
  "prompt_eval_count": 15,
  "prompt_eval_duration": 2000000000,
  "eval_count": 8,
  "eval_duration": 16000000000
}
```

## Notes

1. **Local Ollama Setup**: Ensure Ollama is running with `ollama serve` before testing
2. **Phi-3 Model**: The 3.8B model provides excellent SQL generation with ~20 second response time
3. **Test API Key**: Use `test-api-key` for development and testing
4. **Database URL**: Use `postgres:5432` for internal Docker network, `localhost:5433` for external
5. **Model Performance**: Phi-3 3.8B delivers consistent results with minimal prompts
6. **Caching**: Query results are cached in Redis for improved performance on repeated queries
7. **Security**: All dangerous SQL operations (DROP, DELETE, etc.) are blocked by validation
8. **Inference Time**: ~18-20 seconds is normal for Phi-3 3.8B on standard hardware
9. **Alternative Models**: Switch to `phi3:mini` for faster inference or `llama3.1:8b` for higher accuracy
10. **Offline Capability**: System works completely offline once models are downloaded

## Model Comparison

| Model | Size | Inference Time | Accuracy | Use Case |
|-------|------|----------------|----------|----------|
| phi3:mini | 2.3GB | ~15s | Good | Development/Testing |
| phi3:3.8b | 2.2GB | ~20s | Excellent | Production |
| llama3.1:8b | 4.7GB | ~45s | Superior | Complex Queries |
| codellama:7b | 3.8GB | ~35s | Code-focused | SQL-specific tasks |

## Troubleshooting Commands

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama service
pkill ollama && ollama serve &

# Verify model is loaded
ollama ps

# Check Docker connectivity to Ollama
docker-compose exec nl2sql-api curl http://host.docker.internal:11434/api/tags

# Monitor logs for inference timing
docker-compose logs -f nl2sql-api | grep -E "(inference_time|Generating SQL)"

# Check system resources during inference
top  # or htop
docker stats
```
