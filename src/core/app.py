"""
Main application factory for Regression Auto-Remediation System

Author: Rajendar Muddasani
Date: July 21, 2025
"""

from fastapi import FastAPI
from src.core.config import get_settings

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title="Regression Auto-Remediation System",
        description="AI-powered automated testing & issue resolution platform for V93K test programs",
        version=settings.VERSION,
        debug=settings.DEBUG
    )
    
    # Add startup event
    @app.on_event("startup")
    async def startup_event():
        print("🔧 Initializing Regression Auto-Remediation System...")
        print(f"📊 Environment: {settings.ENVIRONMENT}")
        print(f"🔗 Database Type: {settings.DATABASE_TYPE}")
        print("✅ Startup complete!")
    
    # Add shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        print("🛑 Shutting down Regression Auto-Remediation System...")
        print("✅ Shutdown complete!")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT
        }
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Regression Auto-Remediation System API",
            "version": settings.VERSION,
            "docs": "/docs"
        }
    
    return app
