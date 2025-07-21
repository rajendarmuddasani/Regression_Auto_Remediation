#!/bin/bash
"""
Setup Script for Oracle Database Environment
Creates ../.env file with Oracle database configuration

Usage: ./setup_oracle_env.sh
"""

echo "🔧 Setting up Oracle Database Environment"
echo "=========================================="

# Check if ../.env already exists
if [ -f "../.env" ]; then
    echo "⚠️  ../.env file already exists!"
    echo "📝 Current content:"
    cat ../.env
    echo ""
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled. Keeping existing ../.env file."
        exit 1
    fi
fi

# Create ../.env file
echo "📝 Creating ../.env file with Oracle database configuration..."

cat > ../.env << 'EOF'
# Regression Auto-Remediation System Environment Variables
# Oracle Database Configuration

# Application Settings
ENVIRONMENT=development
DEBUG=true

# Oracle Database Configuration
DBDRIVER=Oracle
DBNAME=SxINTDE_Aww3G
DBHOST=sinwxwtde-db.siwwn.xinfineon.com
DBUSER=SINTDE_Ayyy3G
DBPASSWD=<REPLACE_WITH_ACTUAL_PASSWORD>
SID=7yy
PORT=18522

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Email Configuration (optional)
SMTP_SERVER=<SMTP_SERVER>
SMTP_PORT=587
SMTP_USERNAME=<SMTP_USERNAME>
SMTP_PASSWORD=<SMTP_PASSWORD>
EOF

echo "✅ ../.env file created successfully!"
echo ""
echo "🔐 IMPORTANT: Replace <REPLACE_WITH_ACTUAL_PASSWORD> with the real Oracle password"
echo "📝 Edit ../.env file and update the DBPASSWD value"
echo ""
echo "🧪 After updating the password, test the connection with:"
echo "   python test_database.py"
