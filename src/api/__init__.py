"""
FastAPI REST API for Regression Auto-Remediation System

Provides REST endpoints for:
- File parsing and processing
- Issue classification
- Solution recommendation
- Automated remediation
- System monitoring and management
"""

from .main import app
from .endpoints import parser, classifier, recommender, system, monitoring

__all__ = ['app']
