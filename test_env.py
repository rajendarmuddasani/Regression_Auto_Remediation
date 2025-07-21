#!/usr/bin/env python3
"""
Simple test script to verify Python environment setup

Author: Rajendar Muddasani
Date: July 21, 2025
"""

import sys
import os
from pathlib import Path

def test_environment():
    """Test the Python environment setup"""
    print("🔍 Testing Python Environment Setup")
    print("=" * 50)
    
    # Python version
    print(f"🐍 Python Version: {sys.version}")
    print(f"📍 Python Executable: {sys.executable}")
    
    # Current working directory
    print(f"📂 Working Directory: {os.getcwd()}")
    
    # Check if we can import basic packages
    try:
        import pandas
        print(f"✅ Pandas: {pandas.__version__}")
    except ImportError:
        print("❌ Pandas: Not installed")
    
    try:
        import numpy
        print(f"✅ NumPy: {numpy.__version__}")
    except ImportError:
        print("❌ NumPy: Not installed")
    
    try:
        import sqlalchemy
        print(f"✅ SQLAlchemy: {sqlalchemy.__version__}")
    except ImportError:
        print("❌ SQLAlchemy: Not installed")
    
    # Check directory structure
    print("\n📁 Project Directory Structure:")
    for root, dirs, files in os.walk(".", topdown=True):
        # Skip venv and .git directories
        dirs[:] = [d for d in dirs if d not in ['.git', 'venv', '__pycache__']]
        level = root.replace('.', '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}📂 {os.path.basename(root)}/")
        sub_indent = ' ' * 2 * (level + 1)
        for file in files[:5]:  # Show first 5 files
            if not file.startswith('.') and not file.endswith('.pyc'):
                print(f"{sub_indent}📄 {file}")
        if len(files) > 5:
            print(f"{sub_indent}... and {len(files) - 5} more files")
    
    print("\n✅ Environment test completed!")

if __name__ == "__main__":
    test_environment()
