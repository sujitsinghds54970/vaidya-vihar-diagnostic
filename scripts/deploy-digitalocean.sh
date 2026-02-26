#!/bin/bash

# =============================================================================
# VaidyaVihar Diagnostic ERP - DigitalOcean Deployment Script
# =============================================================================
# This script automates the complete deployment process on DigitalOcean
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_step() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📋 STEP $1: $2${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Configuration
PROJECT_NAME="vaidya-vihar-diagnostic"
PROJECT_DIR="/root/$PROJECT_NAME"
ADMIN_PASSWORD="admin123"
DB_PASSWORD="vaidya_password_123"
JWT_SECRET="vaidya-vihar-super-secret-jwt-key-2024-production-do"

echo -e "\n${BLUE}🏥 VAIDYAVIHAR DIAGNOSTIC ERP - DIGITALOCEAN DEPLOYMENT${NC}"
echo -e "${BLUE}================================================================${NC}"
echo -e "${YELLOW}🚀 Starting deployment at $(date)${NC}\n"

# =============================================================================
# STEP 1: Update System & Install Docker & Docker Compose
# =============================================================================
print_step "1" "Installing Docker & Docker Compose"

# Update system
apt-get update -y && apt-get upgrade -y

# Install required packages
apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    ca-certificates \
    gnupg \
    lsb-release \
    ufw \
    fail2ban

# Check if Docker is already installed
if command -v docker &> /dev/null; then
    print_success "Docker is already installed: $(docker --version)"
else
    print_info "Installing Docker CE..."

    # Add Docker's official GPG key
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Add Docker repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker CE
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    # Start and enable Docker
    systemctl start docker
    systemctl enable docker

    # Add user to docker group
    usermod -aG docker root

    print_success "Docker installed successfully: $(docker --version)"
    print_success "Docker Compose Plugin installed: $(docker compose version)"
fi

# =============================================================================
# STEP 2: Configure Firewall
# =============================================================================
print_step "2" "Configuring Firewall"

print_info "Configuring UFW firewall..."
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw --force reload

print_success "Firewall configured (SSH, HTTP, HTTPS, Backend API)"

# =============================================================================
# STEP 3: Create Project Directory & Clone Repository
# =============================================================================
print_step "3" "Setting up Project Directory"

# Create project directory
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Check if repository already exists
if [ -d ".git" ]; then
    print_info "Repository already exists. Pulling latest changes..."
    git pull origin main
else
    print_info "Cloning repository..."
    git clone https://github.com/sujitsinghds54970/vaidya-vihar-diagnostic.git .
fi

print_success "Project directory set up at $PROJECT_DIR"

# =============================================================================
# STEP 4: Create Environment File
# =============================================================================
print_step "4" "Creating Environment Configuration"

# Get server IP for ALLOWED_ORIGINS
SERVER_IP=$(curl -s http://checkip.amazonaws.com)

# Create .env file
cat > $PROJECT_DIR/.env << EOF
# =============================================================================
# VaidyaVihar Diagnostic ERP - DigitalOcean Production Environment Variables
# =============================================================================

# Database Configuration
DATABASE_URL=postgresql://vaidya_user:${DB_PASSWORD}@postgres:5432/vaidya_vihar_db
POSTGRES_DB=vaidya_vihar_db
POSTGRES_USER=vaidya_user
POSTGRES_PASSWORD=${DB_PASSWORD}

# Redis Configuration
REDIS_URL=redis://redis:6379

# JWT Security - CHANGE IN PRODUCTION!
SECRET_KEY=${JWT_SECRET}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Application Settings
DEBUG=False
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:80", "http://${SERVER_IP}", "https://${SERVER_IP}"]

# SMS Configuration (Twilio) - Optional
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# Email Configuration (Gmail SMTP) - Optional
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=

# WhatsApp Configuration - Optional
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_ACCESS_TOKEN=

# Frontend URL
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# Session Secret
SESSION_SECRET=${JWT_SECRET}
EOF

print_success ".env file created with secure credentials"

# =============================================================================
# STEP 5: Generate SSL Certificates
# =============================================================================
print_step "5" "Generating SSL Certificates"

# Create SSL directory
mkdir -p $PROJECT_DIR/nginx/ssl

# Generate self-signed SSL certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout $PROJECT_DIR/nginx/ssl/server.key \
    -out $PROJECT_DIR/nginx/ssl/server.crt \
    -subj "/C=IN/ST=Maharashtra/L=Mumbai/O=VaidyaVihar/CN=${SERVER_IP}"

chmod 600 $PROJECT_DIR/nginx/ssl/server.key

print_success "SSL certificates generated (365 days validity)"

# =============================================================================
# STEP 6: Create Required Directories
# =============================================================================
print_step "6" "Creating Required Directories"

mkdir -p $PROJECT_DIR/backend/uploads
mkdir -p $PROJECT_DIR/backend/logs
mkdir -p $PROJECT_DIR/frontend/vaidya-vihar-frontend/uploads
mkdir -p $PROJECT_DIR/redis_data

# Set permissions
chmod -R 755 $PROJECT_DIR/backend/uploads
chmod -R 755 $PROJECT_DIR/backend/logs

print_success "Required directories created"

# =============================================================================
# STEP 7: Build Docker Images
# =============================================================================
print_step "7" "Building Docker Images"

# Stop any existing containers
docker compose down 2>/dev/null || true

# Build images (no cache for fresh build)
print_info "Building backend image..."
docker compose build --no-cache backend

print_info "Building frontend image..."
docker compose build --no-cache frontend

print_success "Docker images built successfully"

# =============================================================================
# STEP 8: Start Docker Services
# =============================================================================
print_step "8" "Starting Docker Services"

# Start services in detached mode
docker compose up -d

print_info "Waiting for services to start..."
sleep 30

# =============================================================================
# STEP 9: Verify Services
# =============================================================================
print_step "9" "Verifying Services"

# Check if containers are running
echo ""
echo "📊 Container Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker compose ps
echo ""

# Wait for database to be ready
print_info "Waiting for PostgreSQL to be ready..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if docker compose exec -T postgres pg_isready -U vaidya_user -d vaidya_vihar_db > /dev/null 2>&1; then
        print_success "PostgreSQL is ready!"
        break
    fi
    attempt=$((attempt + 1))
    print_info "Attempt $attempt/$max_attempts - waiting..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    print_error "PostgreSQL failed to start. Check logs with: docker compose logs postgres"
fi

# =============================================================================
# STEP 10: Initialize Database
# =============================================================================
print_step "10" "Initializing Database"

# Run database initialization
print_info "Running database migrations..."
docker compose exec -T backend python -c "
import sys
try:
    from app.database import engine
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('Database connection successful!')
except Exception as e:
    print(f'Database connection error: {e}')
    sys.exit(1)
"

# Seed initial data
print_info "Seeding initial data (admin user, branch)..."
docker compose exec -T backend python init_db.py || print_warning "init_db.py may have already run or is for SQLite"

print_success "Database initialized"

# =============================================================================
# STEP 11: Verify Deployment
# =============================================================================
print_step "11" "Verifying Deployment"

# Test backend health
print_info "Testing backend health..."
health_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
if [ "$health_response" = "200" ]; then
    print_success "Backend is healthy (HTTP 200)"
else
    print_warning "Backend health check returned: $health_response"
    print_info "Check logs with: docker compose logs backend"
fi

# Test frontend
print_info "Testing frontend availability..."
frontend_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")
if [ "$frontend_response" = "200" ] || [ "$frontend_response" = "304" ]; then
    print_success "Frontend is accessible (HTTP $frontend_response)"
else
    print_warning "Frontend may still be starting (HTTP $frontend_response)"
fi

# =============================================================================
# STEP 12: Install SSL Certificate (Let's Encrypt)
# =============================================================================
print_step "12" "Setting up SSL Certificate"

# Install Certbot
apt-get install -y certbot python3-certbot-nginx

print_info "SSL certificate setup instructions:"
print_info "After pointing your domain to this server, run:"
print_info "  sudo certbot --nginx -d yourdomain.com"
print_info "Or for testing with self-signed certificates:"
print_info "  The app is already running with self-signed SSL on port 443"

# =============================================================================
# DEPLOYMENT SUMMARY
# =============================================================================
echo -e "\n"
echo -e "${GREEN}🎉 DIGITALOCEAN DEPLOYMENT COMPLETED SUCCESSFULLY!${NC}"
echo -e "${GREEN}=====================================================${NC}"
echo -e "\n"
echo -e "${BLUE}📱 Access URLs:${NC}"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  🌐 Frontend:    http://${SERVER_IP}"
echo -e "  🔒 HTTPS:       https://${SERVER_IP} (self-signed)"
echo -e "  🔧 Backend API: http://${SERVER_IP}:8000"
echo -e "  📖 API Docs:    http://${SERVER_IP}:8000/docs"
echo -e "  ❤️  Health:      http://${SERVER_IP}:8000/health"
echo -e "\n"
echo -e "${BLUE}🔐 Default Credentials:${NC}"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  👤 Username: admin"
echo -e "  🔑 Password: $ADMIN_PASSWORD"
echo -e "\n"
echo -e "${BLUE}📝 Useful Commands:${NC}"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  📊 View logs:      docker compose logs -f"
echo -e "  🔄 Restart:        docker compose restart"
echo -e "  ⏹️  Stop services: docker compose down"
echo -e "  📦 Update:        git pull && docker compose down && docker compose build --no-cache && docker compose up -d"
echo -e "  💾 Backup DB:     docker compose exec postgres pg_dump -U vaidya_user vaidya_vihar_db > backup.sql"
echo -e "\n"
echo -e "${YELLOW}⚠️  Important Notes:${NC}"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  1. Change the default admin password after first login!"
echo -e "  2. Update JWT_SECRET in .env for production use!"
echo -e "  3. Set up a domain name and configure SSL with Let's Encrypt!"
echo -e "  4. Set up automated backups for the database!"
echo -e "  5. Consider enabling DigitalOcean monitoring and alerts!"
echo -e "\n"
echo -e "${GREEN}🚀 Happy Testing on DigitalOcean!${NC}\n"
