#!/bin/bash

# VaidyaVihar Diagnostic ERP - Quick Setup Script
# This script sets up the development environment for VaidyaVihar Diagnostic ERP

set -e

echo "🏥 VaidyaVihar Diagnostic ERP - Quick Setup"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Make sure you're in vaidya-vihar-diagnostic/ directory"
    exit 1
fi

# Check Python installation
echo "🐍 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Node.js installation
echo "📦 Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Python and Node.js are installed"

# Setup Backend
echo ""
echo "🔧 Setting up Backend..."
cd backend

# Create virtual environment
echo "📁 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment file..."
    cp .env.example .env || echo "⚠️  Please manually create .env file with your configuration"
fi

echo "✅ Backend setup complete"

# Setup Frontend
echo ""
echo "⚛️ Setting up Frontend..."
cd ../frontend/vaidya-vihar-frontend

# Install dependencies
echo "📦 Installing Node dependencies..."
npm install

echo "✅ Frontend setup complete"

# Return to root directory
cd ../..

# Create necessary directories
echo ""
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p logs

# Set permissions
chmod +x setup.sh

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next Steps:"
echo "1. Configure your environment variables in backend/.env"
echo "2. Start the backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "3. Start the frontend: cd frontend/vaidya-vihar-frontend && npm start"
echo ""
echo "Or use Docker:"
echo "docker-compose up -d"
echo ""
echo "Default URLs:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- API Documentation: http://localhost:8000/docs"
echo ""
echo "Default Login Credentials:"
echo "- Username: admin"
echo "- Password: admin123"
echo ""
echo "📖 For detailed instructions, see README.md"
echo "🐛 For issues, please check the documentation"
