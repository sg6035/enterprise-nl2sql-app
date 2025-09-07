# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation updates for Ollama integration
- Performance monitoring for local LLM inference
- Model management utilities and troubleshooting guides

## [1.1.0] - 2024-01-21

### Added
- **Local Ollama Integration**: Complete replacement of OpenAI API with local Phi-3 3.8B model
- **Phi-3 Model Support**: Optimized prompts and post-processing for Microsoft Phi-3 3.8B
- **Docker Host Connectivity**: Configured Docker networking for Ollama communication
- **SQL Cleaning Logic**: Custom post-processing to handle Phi-3 output formatting
- **Model Performance Monitoring**: Tracking inference times (~20 seconds typical)
- **Alternative Model Support**: Easy switching between phi3:3.8b, phi3:mini, llama3.1:8b
- **Cost Elimination**: Zero cloud API costs with local inference
- **Privacy Enhancement**: All processing happens locally, no data sent to external APIs

### Changed
- **Authentication System**: Fixed JWT library compatibility (InvalidTokenError vs JWTError)
- **Prompt Engineering**: Simplified prompts for better Phi-3 performance
- **Environment Configuration**: Updated Docker Compose for Ollama connectivity
- **API Response Format**: Enhanced with inference timing and model metadata
- **Documentation**: Comprehensive rewrite for local deployment workflow

### Fixed
- **JWT Import Issues**: Resolved PyJWT library compatibility in security module
- **SQL Generation**: Fixed Phi-3 output parsing with custom cleaning logic
- **Docker Networking**: Configured host.docker.internal for container-to-host communication
- **Authentication Flow**: Working API key validation with test-api-key for development
- **Model Loading**: Proper Ollama model initialization and health checks

### Security
- **Local Processing**: Enhanced data privacy with no external API calls
- **Authentication Hardening**: Fixed JWT token validation and error handling
- **SQL Injection Prevention**: Maintained comprehensive security validation
- **Rate Limiting**: Adjusted for local processing characteristics

### Performance
- **Response Time**: ~20 second inference with Phi-3 3.8B (predictable, local)
- **Memory Optimization**: Efficient Ollama model loading and management
- **Caching Strategy**: Enhanced caching for repeated queries to avoid re-inference
- **Resource Management**: Optimized Docker resource allocation

### Infrastructure
- **Ollama Service**: Integrated local LLM service with health monitoring
- **Model Management**: Automated model downloading and version management
- **Development Workflow**: Simplified setup with working test credentials
- **Monitoring Integration**: Extended Grafana dashboards for local LLM metrics

## [1.0.0] - 2024-01-20

### Added
- **FastAPI Application**: Complete web framework with async support
- **Advanced NL2SQL Service**: ML-based schema linking with GPT-4 integration
- **Authentication System**: JWT-based auth with role-based access control
- **Database Integration**: PostgreSQL with SQLAlchemy ORM and connection pooling
- **Caching Layer**: Redis integration for query and schema caching
- **Security Features**: 
  - SQL injection prevention
  - Input validation and sanitization
  - Rate limiting and API key management
  - Audit logging for all operations
- **Monitoring Stack**: 
  - Prometheus metrics collection
  - Grafana dashboards
  - Structured logging with Sentry integration
- **Docker Infrastructure**: 
  - Multi-stage Dockerfile
  - Docker Compose orchestration
  - Nginx reverse proxy
- **API Features**:
  - Query execution with natural language
  - Bulk query processing
  - Query history and analytics
  - Administrative endpoints
  - Health checks and system status
- **ML Capabilities**:
  - Semantic similarity matching for schema linking
  - Intelligent prompt engineering
  - Query result caching and optimization
- **Documentation**: 
  - Comprehensive README with setup instructions
  - API documentation
  - Deployment guides
  - Usage examples and best practices
- **Development Tools**:
  - Git workflow and branching strategy
  - CI/CD pipeline with GitHub Actions
  - Security scanning and testing
  - Code quality checks

### Security
- Implemented comprehensive security validation
- Added SQL injection prevention mechanisms
- Configured secure headers and CORS policies
- Integrated audit logging for compliance

### Infrastructure
- Production-ready Docker deployment
- Load balancing with Nginx
- Database migration scripts
- Environment configuration management
- SSL/TLS certificate support

### Performance
- Query result caching
- Database connection pooling
- Async request processing
- Rate limiting and throttling
- Schema caching for improved response times

---

## Migration Guide: OpenAI → Ollama

### For Existing Deployments

1. **Install Ollama**:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ollama serve &
   ollama pull phi3:3.8b
   ```

2. **Update Environment Variables**:
   ```bash
   # Remove OpenAI configuration
   # OPENAI_API_KEY=sk-... 

   # Add Ollama configuration
   OLLAMA_BASE_URL=http://host.docker.internal:11434
   LLM_MODEL=phi3:3.8b
   OLLAMA_MODEL=phi3:3.8b
   ```

3. **Rebuild Services**:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

### Benefits of Migration

- ✅ **Zero API Costs**: No more OpenAI charges
- ✅ **Data Privacy**: All processing stays local
- ✅ **Predictable Performance**: ~20s response time
- ✅ **Offline Capable**: No internet required for inference
- ✅ **Full Control**: Model versioning and management

---

## Version History Format

### Types of Changes
- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` for vulnerability fixes

### Example Entry Format
```
## [1.2.0] - 2024-02-01

### Added
- New local model integration (e.g., CodeLlama support)

### Changed
- Updated prompt templates for new model

### Fixed
- Performance optimization for model switching

### Security
- Enhanced local model security validation
```
