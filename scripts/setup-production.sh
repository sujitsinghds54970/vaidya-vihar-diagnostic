#!/bin/bash

# Production Setup Script for VaidyaVihar Diagnostic ERP
# Automates the complete production deployment process

set -e

echo "🚀 VaidyaVihar Diagnostic ERP - Production Setup"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

# Check if Docker is installed
check_docker() {
    print_info "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        echo "Please install Docker from: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed!"
        echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Create environment file
create_env_file() {
    print_info "Creating environment configuration..."
    
    if [ -f "backend/.env" ]; then
        print_warning ".env file already exists. Skipping..."
        return
    fi
    
    cat > backend/.env << EOF
# Database Configuration
DATABASE_URL=postgresql://vaidya_user:vaidya_password_123@postgres:5432/vaidya_vihar_db

# JWT Configuration
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration (Update with your SMTP details)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=noreply@vaidyavihar.com
EMAIL_USE_TLS=True

# Application Configuration
DEBUG=False
APP_NAME=VaidyaVihar Diagnostic ERP
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:80","https://your-domain.com"]

# Redis Configuration
REDIS_URL=redis://redis:6379

# Backup Configuration
BACKUP_ENABLED=True
BACKUP_RETENTION_DAYS=30
BACKUP_SCHEDULE=0 2 * * *

# Security
CORS_ORIGINS=["http://localhost:3000","http://localhost:80"]
EOF
    
    print_success "Environment file created at backend/.env"
    print_warning "Please update EMAIL_* variables with your SMTP credentials"
}

# Create frontend environment file
create_frontend_env() {
    print_info "Creating frontend environment configuration..."
    
    if [ -f "frontend/vaidya-vihar-frontend/.env" ]; then
        print_warning "Frontend .env file already exists. Skipping..."
        return
    fi
    
    cat > frontend/vaidya-vihar-frontend/.env << EOF
REACT_APP_API_URL=http://localhost:8000
REACT_APP_NAME=VaidyaVihar Diagnostic ERP
REACT_APP_VERSION=2.0.0
EOF
    
    print_success "Frontend environment file created"
}

# Initialize database
init_database() {
    print_info "Initializing database..."
    
    # Start PostgreSQL container
    docker-compose up -d postgres
    
    # Wait for PostgreSQL to be ready
    print_info "Waiting for PostgreSQL to be ready..."
    sleep 10
    
    # Run migrations
    print_info "Running database migrations..."
    docker-compose exec -T backend alembic upgrade head || true
    
    # Initialize database with default data
    print_info "Initializing database with default data..."
    docker-compose exec -T backend python init_db.py || true
    
    print_success "Database initialized"
}

# Generate SSL certificates
setup_ssl() {
    print_info "SSL Certificate Setup"
    echo ""
    echo "Do you want to generate SSL certificates?"
    echo "1) Yes - Self-signed (Development)"
    echo "2) Yes - Let's Encrypt (Production)"
    echo "3) No - Skip SSL setup"
    echo ""
    read -p "Enter choice [1-3]: " ssl_choice
    
    case $ssl_choice in
        1)
            bash scripts/generate-ssl-cert.sh
            ;;
        2)
            bash scripts/generate-ssl-cert.sh
            ;;
        3)
            print_warning "Skipping SSL setup. You can run scripts/generate-ssl-cert.sh later."
            ;;
        *)
            print_warning "Invalid choice. Skipping SSL setup."
            ;;
    esac
}

# Build and start services
start_services() {
    print_info "Building and starting all services..."
    
    # Build images
    print_info "Building Docker images..."
    docker-compose build
    
    # Start all services
    print_info "Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    print_info "Waiting for services to start..."
    sleep 15
    
    print_success "All services started"
}

# Check service health
check_health() {
    print_info "Checking service health..."
    
    # Check PostgreSQL
    if docker-compose ps postgres | grep -q "Up"; then
        print_success "PostgreSQL is running"
    else
        print_error "PostgreSQL is not running"
    fi
    
    # Check Redis
    if docker-compose ps redis | grep -q "Up"; then
        print_success "Redis is running"
    else
        print_error "Redis is not running"
    fi
    
    # Check Backend
    if docker-compose ps backend | grep -q "Up"; then
        print_success "Backend is running"
    else
        print_error "Backend is not running"
    fi
    
    # Check Frontend
    if docker-compose ps frontend | grep -q "Up"; then
        print_success "Frontend is running"
    else
        print_error "Frontend is not running"
    fi
    
    # Check Nginx
    if docker-compose ps nginx | grep -q "Up"; then
        print_success "Nginx is running"
    else
        print_error "Nginx is not running"
    fi
}

# Display access information
display_info() {
    echo ""
    echo "================================================"
    echo "🎉 VaidyaVihar Diagnostic ERP Setup Complete!"
    echo "================================================"
    echo ""
    print_success "Application is ready to use!"
    echo ""
    echo "📍 Access URLs:"
    echo "   Frontend:     http://localhost:3000"
    echo "   Backend API:  http://localhost:8000"
    echo "   API Docs:     http://localhost:8000/docs"
    echo "   Nginx Proxy:  http://localhost:80"
    echo ""
    echo "🔐 Default Credentials:"
    echo "   Username: admin"
    echo "   Password: admin123"
    echo ""
    print_warning "IMPORTANT: Change the default password after first login!"
    echo ""
    echo "📋 Useful Commands:"
    echo "   View logs:        docker-compose logs -f"
    echo "   Stop services:    docker-compose down"
    echo "   Restart services: docker-compose restart"
    echo "   View status:      docker-compose ps"
    echo ""
    echo "📚 Documentation:"
    echo "   README.md"
    echo "   PRODUCTION_IMPLEMENTATION_PLAN.md"
    echo ""
    echo "🆘 Support:"
    echo "   Check logs if you encounter issues"
    echo "   Ensure all ports (80, 443, 3000, 5432, 6379, 8000) are available"
    echo ""
}

# Main execution
main() {
    echo "Starting production setup..."
    echo ""
    
    # Step 1: Check prerequisites
    check_docker
    
    # Step 2: Create environment files
    create_env_file
    create_frontend_env
    
    # Step 3: Setup SSL (optional)
    setup_ssl
    
    # Step 4: Build and start services
    start_services
    
    # Step 5: Initialize database
    init_database
    
    # Step 6: Check health
    check_health
    
    # Step 7: Display information
    display_info
}

# Run main function
main
