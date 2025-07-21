"""
Configuration management for Regression Auto-Remediation System

Author: Rajendar Muddasani
Date: July 21, 2025
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from ../.env for security
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application Info
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # Database Configuration (Oracle)
    DATABASE_TYPE: str = Field(default="Oracle", env="DBDRIVER")
    DATABASE_NAME: str = Field(default="SxINTDE_Aww3G", env="DBNAME")
    DATABASE_HOST: str = Field(default="sinwxwtde-db.siwwn.xinfineon.com", env="DBHOST")
    DATABASE_USER: str = Field(default="SINTDE_Ayyy3G", env="DBUSER")
    DATABASE_PASSWORD: str = Field(default="<REPLACE_WITH_ACTUAL_PASSWORD>", env="DBPASSWD")
    DATABASE_SID: str = Field(default="7yy", env="SID")
    DATABASE_PORT: int = Field(default=18522, env="PORT")
    
    # ML Model Configuration
    MODELS_DIR: Path = Path(__file__).parent.parent.parent / "models"
    MODEL_CONFIDENCE_THRESHOLD: float = 0.7
    
    # File Processing
    LOG_FILES_DIR: Path = Path("/var/log/regression_auto_remediation")
    TEMP_DIR: Path = Path("/tmp/regression_temp")
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    
    # Email Configuration
    SMTP_SERVER: str = Field(default="<SMTP_SERVER>", env="SMTP_SERVER")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: str = Field(default="<SMTP_USERNAME>", env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field(default="<SMTP_PASSWORD>", env="SMTP_PASSWORD")
    
    class Config:
        env_file = "../.env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables

# Global settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

def get_database_url() -> str:
    """Construct Oracle database connection URL"""
    settings = get_settings()
    return f"oracle+cx_oracle://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/?service_name={settings.DATABASE_NAME}"
