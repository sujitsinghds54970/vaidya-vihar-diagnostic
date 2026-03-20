#!/bin/bash

# VaidyaVihar Diagnostic ERP - Quick Start Script
# This script starts the entire project (backend + frontend + database)

echo "🏥 Starting VaidyaVihar Diagnostic ERP..."
echo "========================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Navigate to project directory
cd "$(dirname "$0")"

echo -e "${BLUE}📦 Starting Docker containers...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "${BLUE}⏳ Waiting for services to start...${NC}"
sleep 5

# Check if database needs initialization
if [ ! -f "backend/vaidya_vihar.db" ]; then
    echo -e "${BLUE}🔨 Initializing database...${NC}"
    docker-compose exec backend python3 init_database.py
fi

echo ""
echo -e "${GREEN}✅ VaidyaVihar ERP is now running!${NC}"
echo ""
echo "📍 Access Points:"
echo "   - Frontend:  http://localhost:3000"
echo "   - Backend:   http://localhost:8000"
echo "   - API Docs:  http://localhost:8000/docs"
echo ""
echo "🔐 Default Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📊 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
