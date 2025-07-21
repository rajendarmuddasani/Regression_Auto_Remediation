#!/usr/bin/env python3
"""
Regression Auto-Remediation System
Main application entry point

Author: Rajendar Muddasani
Date: July 21, 2025
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.app import create_app
from src.core.config import get_settings

def main():
    """Main application entry point"""
    settings = get_settings()
    app = create_app()
    
    print(f"🚀 Starting Regression Auto-Remediation System v{settings.VERSION}")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🔗 Database: {settings.DATABASE_TYPE}")
    
    # For now, just print that we're starting
    print("✅ System initialized successfully!")
    print("📝 Ready for regression monitoring...")

if __name__ == "__main__":
    main()
