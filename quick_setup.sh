#!/bin/bash

# 🚀 Quick Start Script for Regression Auto-Remediation System
# Run this script on a new laptop to set up the entire application

set -e  # Exit on any error

echo "🚀 Starting Regression Auto-Remediation System Setup..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "requirements.txt" ] || [ ! -d "web_dashboard" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Step 1: Check Prerequisites
print_status "Checking prerequisites..."

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python found: $PYTHON_VERSION"
else
    print_error "Python 3 is required but not found. Please install Python 3.9+"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_success "Node.js found: $NODE_VERSION"
else
    print_error "Node.js is required but not found. Please install Node.js 16+"
    exit 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    print_success "npm found: $NPM_VERSION"
else
    print_error "npm is required but not found. Please install npm"
    exit 1
fi

# Step 2: Backend Setup
print_status "Setting up Python backend..."

# Create virtual environment
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt
print_success "Python dependencies installed"

# Step 3: Frontend Setup
print_status "Setting up React frontend..."

# Navigate to frontend directory
cd web_dashboard

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
npm install
print_success "Node.js dependencies installed"

# Go back to project root
cd ..

# Step 4: Environment Configuration
print_status "Setting up environment configuration..."

if [ ! -f ".env" ]; then
    print_status "Creating .env file..."
    cat > .env << EOL
# Database Configuration (Update with your Oracle DB details)
DB_HOST=localhost
DB_PORT=1521
DB_SERVICE=your_service_name
DB_USER=your_username
DB_PASSWORD=your_password

# API Configuration
API_HOST=localhost
API_PORT=8000
DEBUG=true

# Frontend Configuration
VITE_API_BASE_URL=http://localhost:8000

# Oracle Client Configuration (if needed)
ORACLE_HOME=/opt/oracle/instantclient_21_8
EOL
    print_success ".env file created - PLEASE UPDATE WITH YOUR DATABASE CREDENTIALS"
else
    print_warning ".env file already exists"
fi

# Step 5: Create startup scripts
print_status "Creating startup scripts..."

# Backend startup script
cat > start_backend.sh << 'EOL'
#!/bin/bash
echo "🐍 Starting Python Backend Server..."
source venv/bin/activate
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
EOL
chmod +x start_backend.sh

# Frontend startup script
cat > start_frontend.sh << 'EOL'
#!/bin/bash
echo "⚛️ Starting React Frontend Server..."
cd web_dashboard
npm run dev
EOL
chmod +x start_frontend.sh

# Combined startup script
cat > start_app.sh << 'EOL'
#!/bin/bash
echo "🚀 Starting Full-Stack Application..."
echo "Opening backend and frontend in separate terminal tabs..."

# Start backend in background
echo "Starting backend server..."
./start_backend.sh &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "Starting frontend server..."
./start_frontend.sh &
FRONTEND_PID=$!

echo "=================================================="
echo "✅ Application started successfully!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "=================================================="
echo "Press Ctrl+C to stop all servers"

# Wait for Ctrl+C
trap 'kill $BACKEND_PID $FRONTEND_PID; exit' INT
wait
EOL
chmod +x start_app.sh

print_success "Startup scripts created"

# Step 6: Test Installation
print_status "Testing installation..."

# Test Python imports
print_status "Testing Python dependencies..."
python3 -c "
import fastapi
import uvicorn
import pandas
import numpy
print('✅ Core Python dependencies working')
"

# Test Oracle client (optional)
if python3 -c "import cx_Oracle" 2>/dev/null; then
    print_success "Oracle client available"
else
    print_warning "Oracle client not available - install if needed for database connectivity"
fi

# Step 7: Final Instructions
echo ""
echo "=================================================="
print_success "🎉 Setup completed successfully!"
echo "=================================================="
echo ""
echo "📝 IMPORTANT NEXT STEPS:"
echo ""
echo "1. 📊 UPDATE DATABASE CONFIGURATION:"
echo "   Edit .env file with your Oracle database credentials"
echo ""
echo "2. 🚀 START THE APPLICATION:"
echo "   Option A (Recommended): ./start_app.sh"
echo "   Option B (Manual):"
echo "     Terminal 1: ./start_backend.sh"
echo "     Terminal 2: ./start_frontend.sh"
echo ""
echo "3. 🌐 ACCESS THE APPLICATION:"
echo "   Frontend Dashboard: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "4. ✅ VERIFY SETUP:"
echo "   curl http://localhost:8000/health"
echo ""
echo "📖 For detailed setup instructions, see: SETUP_GUIDE.md"
echo "🐛 For troubleshooting, check the troubleshooting section in SETUP_GUIDE.md"
echo ""
print_success "Ready to launch! 🚀"
