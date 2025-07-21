# 🚀 Quick Start Setup Guide

This guide will help you set up the Regression Auto-Remediation System on a new laptop/environment.

## Prerequisites

### Required Software
- **Python 3.9+** (3.10+ recommended)
- **Node.js 16+** (18+ recommended) 
- **Git** for cloning the repository
- **Oracle Client** (if using Oracle database)

### System Dependencies (macOS)
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and Node.js
brew install python@3.10 node@18

# For Oracle connectivity (optional)
brew install oracle-instantclient
```

### System Dependencies (Ubuntu/Debian)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and Node.js
sudo apt install python3.10 python3.10-venv python3-pip nodejs npm -y

# For Oracle connectivity (optional)
sudo apt install oracle-instantclient-basic oracle-instantclient-devel -y
```

## 📥 Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/rajendarmuddasani/Regression_Auto_Remediation.git
cd Regression_Auto_Remediation
```

### 2. Backend Setup (Python/FastAPI)

#### Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

#### Install Python Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# If you encounter Oracle client issues, install cx_Oracle separately:
pip install cx_Oracle==8.3.0
```

### 3. Frontend Setup (React/TypeScript)

#### Navigate to frontend directory and install dependencies
```bash
cd web_dashboard
npm install
```

### 4. Environment Configuration

#### Create Environment File
```bash
# Go back to project root
cd ..

# Create .env file (template below)
cp .env.example .env  # If example exists, or create new:
touch .env
```

#### Configure .env file
```bash
# Edit .env with your settings
vim .env  # or use any text editor
```

**Required .env variables:**
```env
# Database Configuration
DB_HOST=your_oracle_host
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
```

### 5. Database Setup (Optional - if using Oracle)

#### Test Oracle Connection
```bash
# Run database connection test
python test_database.py

# Or run quick Oracle test
python test_oracle_quick.py
```

## 🏃‍♂️ Running the Application

### Start Backend Server
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Start FastAPI server
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Alternative: Use the main script
python main.py
```

### Start Frontend Server
```bash
# In a new terminal, navigate to frontend
cd web_dashboard

# Start React development server
npm run dev

# The frontend will be available at: http://localhost:3000
```

## 🔗 Access URLs

Once both servers are running:

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc

## ✅ Verification Steps

### 1. Backend Health Check
```bash
curl http://localhost:8000/health
# Expected response: {"status": "healthy", "timestamp": "..."}
```

### 2. Frontend Access
- Open browser to http://localhost:3000
- You should see the dashboard with navigation sidebar
- All pages should load without errors

### 3. API Integration Test
```bash
# Run integration tests
python test_integration.py
```

## 🐛 Troubleshooting

### Common Issues

#### Python Virtual Environment
```bash
# If venv activation fails:
which python3
python3 -m venv --clear venv
source venv/bin/activate
```

#### Node.js Dependencies
```bash
# If npm install fails:
cd web_dashboard
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### Oracle Client Issues
```bash
# macOS: Set Oracle environment
export ORACLE_HOME=/opt/oracle/instantclient_21_8
export PATH=$ORACLE_HOME:$PATH
export DYLD_LIBRARY_PATH=$ORACLE_HOME:$DYLD_LIBRARY_PATH

# Test Oracle connectivity
python -c "import cx_Oracle; print('Oracle client works!')"
```

#### Port Conflicts
```bash
# If ports 3000 or 8000 are busy:
lsof -ti:3000  # Check what's using port 3000
lsof -ti:8000  # Check what's using port 8000

# Kill processes if needed:
kill -9 $(lsof -ti:3000)
kill -9 $(lsof -ti:8000)
```

#### Environment Variables
```bash
# Check if .env is loaded:
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('DB_HOST'))"
```

## 📝 Development Commands

### Backend Development
```bash
# Run with auto-reload
uvicorn src.api.main:app --reload

# Run tests
python -m pytest tests/

# Code formatting
black src/
flake8 src/
```

### Frontend Development
```bash
cd web_dashboard

# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🎯 Next Steps

After successful setup:

1. **Configure Database**: Update .env with your Oracle database credentials
2. **Load Test Data**: Run sample data scripts if available
3. **Customize Settings**: Modify configuration in Settings page
4. **Test ML Models**: Upload test files through File Parser page
5. **Monitor System**: Check System Monitoring page for health metrics

---

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review log files in the terminal outputs
3. Ensure all prerequisites are properly installed
4. Verify environment variables are correctly set

**System Status**: After following this guide, you should have a fully operational full-stack application! 🚀
