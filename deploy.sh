#!/bin/bash

# Enterprise NL2SQL Deployment Script
# This script automates the deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root for security reasons"
fi

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running. Please start Docker service."
    fi
    
    log "Prerequisites check passed!"
}

# Function to setup environment
setup_environment() {
    log "Setting up environment..."
    
    if [ ! -f .env ]; then
        log "Creating .env file from template..."
        cp .env.example .env
        
        # Generate secure keys
        API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
        
        # Update .env file
        sed -i "s/your-secure-api-key-here/$API_KEY/" .env
        sed -i "s/your-super-secret-key-here/$SECRET_KEY/" .env
        sed -i "s/your-jwt-secret-key-here/$JWT_SECRET_KEY/" .env
        
        warn "Please edit .env file and add your OpenAI API key and other required configurations"
        warn "Run: nano .env"
        
        read -p "Press Enter after updating .env file..."
    fi
    
    # Validate required environment variables
    source .env
    
    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key" ]; then
        error "OPENAI_API_KEY is not set in .env file"
    fi
    
    log "Environment setup completed!"
}

# Function to create necessary directories
setup_directories() {
    log "Creating necessary directories..."
    
    mkdir -p logs/nginx
    mkdir -p nginx/ssl
    mkdir -p monitoring/prometheus
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    mkdir -p scripts
    mkdir -p data/postgres
    mkdir -p data/redis
    
    # Set proper permissions
    chmod 755 logs nginx monitoring scripts data
    chmod 644 .env
    
    log "Directories created successfully!"
}

# Function to setup monitoring configuration
setup_monitoring() {
    log "Setting up monitoring configuration..."
    
    # Create Prometheus configuration
    cat > monitoring/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  external_labels:
    monitor: 'nl2sql-monitor'

scrape_configs:
  - job_name: 'nl2sql-api'
    static_configs:
      - targets: ['nl2sql-api:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF

    # Create Grafana datasource configuration
    cat > monitoring/grafana/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

    log "Monitoring configuration completed!"
}

# Function to setup nginx configuration
setup_nginx() {
    log "Setting up Nginx configuration..."
    
    mkdir -p nginx
    
    cat > nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                    '\$status \$body_bytes_sent "\$http_referer" '
                    '"\$http_user_agent" "\$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api_limit:10m rate=10r/s;

    upstream nl2sql_backend {
        server nl2sql-api:8000;
    }

    server {
        listen 80;
        server_name localhost;

        # Rate limiting
        limit_req zone=api_limit burst=20 nodelay;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        location / {
            proxy_pass http://nl2sql_backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        location /health {
            proxy_pass http://nl2sql_backend/health;
            access_log off;
        }
    }
}
EOF

    log "Nginx configuration completed!"
}

# Function to build and start services
deploy_services() {
    log "Building and starting services..."
    
    # Pull latest images
    docker-compose pull
    
    # Build custom images
    docker-compose build --no-cache
    
    # Start services
    docker-compose up -d
    
    log "Services started successfully!"
}

# Function to wait for services to be ready
wait_for_services() {
    log "Waiting for services to be ready..."
    
    # Wait for database
    log "Waiting for database..."
    while ! docker-compose exec -T postgres pg_isready -U nl2sql -d nl2sql_db; do
        sleep 2
    done
    
    # Wait for Redis
    log "Waiting for Redis..."
    while ! docker-compose exec -T redis redis-cli ping; do
        sleep 2
    done
    
    # Wait for API
    log "Waiting for API..."
    while ! curl -f -s http://localhost:8000/health > /dev/null; do
        sleep 5
    done
    
    log "All services are ready!"
}

# Function to run post-deployment checks
post_deployment_checks() {
    log "Running post-deployment checks..."
    
    # Check service status
    docker-compose ps
    
    # Test API endpoints
    log "Testing API endpoints..."
    
    # Health check
    if curl -f -s http://localhost:8000/health > /dev/null; then
        log "✓ Health endpoint is working"
    else
        error "✗ Health endpoint is not working"
    fi
    
    # API documentation
    if curl -f -s http://localhost:8000/docs > /dev/null; then
        log "✓ API documentation is accessible"
    else
        warn "✗ API documentation is not accessible"
    fi
    
    log "Post-deployment checks completed!"
}

# Function to display deployment summary
show_deployment_summary() {
    log "🎉 Deployment completed successfully!"
    
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}    NL2SQL Service Deployed     ${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    echo -e "${GREEN}🌐 Service URLs:${NC}"
    echo "   API Service:       http://localhost:8000"
    echo "   API Documentation: http://localhost:8000/docs"
    echo "   Grafana Dashboard: http://localhost:3000 (admin/admin123)"
    echo "   Prometheus:        http://localhost:9090"
    echo ""
    echo -e "${GREEN}🔑 Test Credentials:${NC}"
    echo "   Admin User:  admin@nl2sql.com / admin123"
    echo "   Demo User:   demo@nl2sql.com / user123"
    echo ""
    echo -e "${GREEN}🛠️  Useful Commands:${NC}"
    echo "   View logs:         docker-compose logs -f"
    echo "   Stop services:     docker-compose down"
    echo "   Restart:           docker-compose restart"
    echo "   Update:            ./deploy.sh --update"
    echo ""
    echo -e "${YELLOW}⚠️  Next Steps:${NC}"
    echo "   1. Configure SSL certificates for HTTPS"
    echo "   2. Set up domain name and DNS"
    echo "   3. Configure monitoring alerts"
    echo "   4. Review security settings"
    echo "   5. Set up automated backups"
    echo ""
}

# Function to handle updates
update_deployment() {
    log "Updating deployment..."
    
    # Pull latest changes
    git pull
    
    # Pull new images
    docker-compose pull
    
    # Rebuild and restart
    docker-compose up -d --build
    
    wait_for_services
    post_deployment_checks
    
    log "Update completed successfully!"
}

# Function to clean up
cleanup() {
    log "Cleaning up..."
    
    # Remove stopped containers
    docker container prune -f
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes (be careful with this)
    read -p "Do you want to remove unused Docker volumes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker volume prune -f
    fi
    
    log "Cleanup completed!"
}

# Main deployment function
main() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Enterprise NL2SQL Deployment  ${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    
    # Parse command line arguments
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            setup_environment
            setup_directories
            setup_monitoring
            setup_nginx
            deploy_services
            wait_for_services
            post_deployment_checks
            show_deployment_summary
            ;;
        "update" | "--update")
            update_deployment
            ;;
        "cleanup" | "--cleanup")
            cleanup
            ;;
        "status" | "--status")
            docker-compose ps
            ;;
        "logs" | "--logs")
            docker-compose logs -f
            ;;
        "help" | "--help")
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  deploy    - Full deployment (default)"
            echo "  update    - Update existing deployment"
            echo "  cleanup   - Clean up Docker resources"
            echo "  status    - Show service status"
            echo "  logs      - Show service logs"
            echo "  help      - Show this help message"
            ;;
        *)
            error "Unknown command: $1. Use '$0 help' for usage information."
            ;;
    esac
}

# Run main function
main "$@"
