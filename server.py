#!/usr/bin/env python3
"""
FastAPI Server Launcher for Regression Auto-Remediation System

Author: Rajendar Muddasani
Date: July 21, 2025
"""

import sys
from pathlib import Path
import uvicorn

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.app import create_app
from src.core.config import get_settings

def start_server():
    """Start the FastAPI server"""
    settings = get_settings()
    app = create_app()
    
    print(f"🚀 Starting Regression Auto-Remediation API Server")
    print(f"🌐 Server: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"📖 Docs: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )

if __name__ == "__main__":
    start_server()
