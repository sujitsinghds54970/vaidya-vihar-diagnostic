#!/bin/bash

# =============================================================================
# VAIDYAVIHAR DIAGNOSTIC ERP - ONE-CLICK DEPLOYMENT
# =============================================================================
# Server: 65.20.71.151
# 
# Copy and paste this entire script on your Vultr Ubuntu server
# =============================================================================

set -e

echo "🏥 VaidyaVihar Diagnostic ERP - Deployment Started"
echo "=================================================="
echo "⏰ Started at: $(date)"
echo ""

# Step 1: Update and Install Docker
echo "📦 Step 1/7: Installing Docker..."
apt-get update -qq
apt-get install -y curl wget git unzip > /dev/null 2>&1

# Docker install
curl -fsSL https://get.docker.com | sh
systemctl start docker > /dev/null 2>&1
systemctl enable docker > /dev/null 2>&1
echo "✅ Docker installed: $(docker --version)"

# Step 2: Clone Repository
echo ""
echo "📥 Step 2/7: Cloning repository..."
cd ~
rm -rf vaidya-vihar-diagnostic 2>/dev/null || true
git clone https://github.com/sujitsinghds54970/vaidya-vihar-diagnostic.git
cd vaidya-vihar-diagnostic
echo "✅ Repository cloned"

# Step 3: Create Environment
echo ""
echo "⚙️ Step 3/7: Creating environment file..."
cat > .env << 'ENVEOF'
DATABASE_URL=postgresql://vaidya_user:vaidya_password_123@postgres:5432/vaidya_vihar_db
SECRET_KEY=vaidya-vihar-secret-key-2024-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REDIS_URL=redis://redis:6379
DEBUG=False
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:80"]
ENVEOF
echo "✅ Environment configured"

# Step 4: Setup SSL
echo ""
echo "🔒 Step 4/7: Generating SSL certificates..."
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/server.key \
    -out nginx/ssl/server.crt \
    -subj "/C=IN/ST=Maharashtra/L=Mumbai/O=VaidyaVihar/CN=localhost" > /dev/null 2>&1
chmod 600 nginx/ssl/server.key
echo "✅ SSL certificates generated"

# Step 5: Create Directories
echo ""
echo "📁 Step 5/7: Creating directories..."
mkdir -p backend/uploads backend/logs redis_data
chmod -R 755 backend/uploads
echo "✅ Directories created"

# Step 6: Build and Start Docker
echo ""
echo "🐳 Step 6/7: Building and starting Docker containers..."
docker compose down > /dev/null 2>&1 || true
docker compose build --no-cache > /dev/null 2>&1
docker compose up -d > /dev/null 2>&1
echo "✅ Containers started"

# Step 7: Wait and Verify
echo ""
echo "⏳ Step 7/7: Waiting for services to start..."
sleep 30

# Check services
echo ""
echo "📊 Service Status:"
docker compose ps
echo ""

# Test endpoints
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
FRONTEND_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || echo "000")

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Access URLs:"
echo "   • Frontend:  http://65.20.71.151"
echo "   • Backend:   http://65.20.71.151:8000"
echo "   • API Docs:  http://65.20.71.151:8000/docs"
echo ""
echo "🔐 Login Credentials:"
echo "   • Username: admin"
echo "   • Password: admin123"
echo ""
echo "📝 Useful Commands:"
echo "   • View logs:    docker compose logs -f"
echo "   • Restart:      docker compose restart"
echo "   • Stop:        docker compose down"
echo "   • Update:      git pull && docker compose down && docker compose build --no-cache && docker compose up -d"
echo ""
echo "⏰ Completed at: $(date)"
echo ""

