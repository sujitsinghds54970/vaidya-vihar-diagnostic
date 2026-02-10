#!/bin/bash

# Setup Script for VaidyaVihar Diagnostic ERP - Modern Features
# This script installs and configures all modern features

set -e

echo "=========================================="
echo "VaidyaVihar Diagnostic ERP - Modern Features Setup"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check prerequisites
echo "Checking prerequisites..."

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    print_status "Python found: $PYTHON_VERSION"
else
    print_error "Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check pip
if command -v pip3 &> /dev/null; then
    print_status "pip3 found"
else
    print_error "pip3 not found. Please install pip3"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version 2>&1)
    print_status "Node.js found: $NODE_VERSION"
else
    print_warning "Node.js not found. Frontend features may not work."
fi

echo ""
echo "=========================================="
echo "Step 1: Backend Dependencies"
echo "=========================================="

cd backend

# Upgrade pip
print_status "Upgrading pip..."
pip3 install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
pip3 install -r requirements.txt

print_status "Backend dependencies installed successfully!"

echo ""
echo "=========================================="
echo "Step 2: Frontend Dependencies"
echo "=========================================="

cd ../frontend/vaidya-vihar-frontend

# Install Node dependencies
print_status "Installing Node.js dependencies..."
npm install

print_status "Frontend dependencies installed successfully!"

echo ""
echo "=========================================="
echo "Step 3: Database Setup"
echo "=========================================="

cd ../../backend

# Create Alembic migration
print_status "Creating database migrations..."
python3 -m alembic revision --autogenerate -m "Add modern feature models"

# Run migrations
print_status "Running database migrations..."
python3 -m alembic upgrade head

print_status "Database setup completed!"

echo ""
echo "=========================================="
echo "Step 4: Redis Setup"
echo "=========================================="

# Check if Redis is installed
if command -v redis-server &> /dev/null; then
    print_status "Redis is installed"
    
    # Start Redis in background
    print_status "Starting Redis server..."
    redis-server --daemonize yes
    
    print_status "Redis started successfully!"
else
    print_warning "Redis not found. Installing Redis..."
    
    # Install Redis based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install redis
        brew services start redis
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Ubuntu/Debian
        apt-get update
        apt-get install -y redis-server
        systemctl start redis
    fi
    
    print_status "Redis installed and started!"
fi

echo ""
echo "=========================================="
echo "Step 5: Environment Configuration"
echo "=========================================="

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file..."
    cat > .env << EOF
# Database
DATABASE_URL=postgresql://vaidya_user:vaidya_password_123@localhost:5432/vaidya_vihar_db

# JWT
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_URL=redis://localhost:6379

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890

# WhatsApp Cloud API
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_id

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Push Notifications
VAPID_PUBLIC_KEY=your_vapid_public_key
VAPID_PRIVATE_KEY=your_vapid_private_key

# AWS S3 (Optional)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_BUCKET_NAME=vaidya-vihar-reports
AWS_REGION=us-east-1

# Frontend URL
FRONTEND_URL=http://localhost:3000
EOF
    print_status ".env file created!"
else
    print_warning ".env file already exists. Skipping..."
fi

echo ""
echo "=========================================="
echo "Step 6: Initial Data Seeding"
echo "=========================================="

# Seed initial data
print_status "Seeding initial data..."
python3 init_db.py

print_status "Initial data seeded!"

echo ""
echo "=========================================="
echo "Step 7: SSL Certificates (Optional)"
echo "=========================================="

print_warning "Generating self-signed SSL certificates for development..."
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/server.key \
    -out nginx/ssl/server.crt \
    -subj "/C=IN/ST=Maharashtra/L=Mumbai/O=VaidyaVihar/CN=localhost"

print_status "SSL certificates generated!"

echo ""
echo "=========================================="
echo "Step 8: Docker Services (Optional)"
echo "=========================================="

print_status "Starting Docker services..."
docker-compose up -d postgres redis

print_status "Docker services started!"

echo ""
echo "=========================================="
echo "Step 9: Running Tests"
echo "=========================================="

print_status "Running backend tests..."
python3 -m pytest app/tests/ -v --tb=short

print_status "Tests completed!"

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Modern features added:"
echo "  • Doctor Management System"
echo "  • City-wide Report Distribution"
echo "  • Real-time WebSocket Notifications"
echo "  • SMS Integration (Twilio)"
echo "  • WhatsApp Integration"
echo "  • Redis Caching"
echo "  • QR Code Generation"
echo "  • AI-powered Test Recommendations"
echo "  • Dark Mode UI"
echo ""
echo "To start the services:"
echo ""
echo "  Backend:  cd backend && uvicorn app.main:app --reload"
echo "  Frontend: cd frontend/vaidya-vihar-frontend && npm start"
echo ""
echo "Or use Docker:"
echo "  docker-compose up -d"
echo ""
echo "Access:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""

