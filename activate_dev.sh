#!/bin/bash
"""
Development Environment Activation Script
Regression Auto-Remediation System

Usage: source activate_dev.sh
"""

# Activate virtual environment
echo "🔧 Activating Regression Auto-Remediation development environment..."
source venv/bin/activate

# Verify activation
echo "✅ Virtual environment activated!"
echo "🐍 Python: $(which python)"
echo "📦 Pip: $(which pip)"

# Display available commands
echo ""
echo "🚀 Available commands:"
echo "  python main.py      - Run main application"
echo "  python server.py    - Start FastAPI server"
echo "  python test_env.py  - Test environment"
echo "  pip install <pkg>   - Install new packages"
echo ""
echo "📖 FastAPI docs will be at: http://localhost:8000/docs"
echo "🎯 Ready for development!"
