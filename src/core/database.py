"""
Database connection manager for Regression Auto-Remediation System

Author: Rajendar Muddasani
Date: July 21, 2025
"""

import os
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from src.core.config import get_settings

# Base class for all database models
Base = declarative_base()

class DatabaseManager:
    """Database connection and session management"""
    
    def __init__(self):
        self.settings = get_settings()
        self.engine: Optional[object] = None
        self.session_local: Optional[sessionmaker] = None
        
    def get_connection_url(self) -> str:
        """Construct database connection URL"""
        if self.settings.DATABASE_TYPE.lower() == "oracle":
            # Oracle connection string
            return f"oracle+cx_oracle://{self.settings.DATABASE_USER}:{self.settings.DATABASE_PASSWORD}@{self.settings.DATABASE_HOST}:{self.settings.DATABASE_PORT}/?service_name={self.settings.DATABASE_NAME}"
        else:
            raise ValueError(f"Unsupported database type: {self.settings.DATABASE_TYPE}")
    
    def initialize_connection(self) -> bool:
        """Initialize database connection"""
        try:
            # Check if we have placeholder values
            if self.settings.DATABASE_PASSWORD == "<REPLACE_WITH_ACTUAL_PASSWORD>":
                print("⚠️  Database password not configured (using placeholder)")
                print("📝 Please update ../.env file with real database password")
                print("   Replace <REPLACE_WITH_ACTUAL_PASSWORD> with actual password")
                return False
            
            connection_url = self.get_connection_url()
            
            # Create engine
            self.engine = create_engine(
                connection_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=self.settings.DEBUG
            )
            
            # Create session factory
            self.session_local = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Test connection
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1 FROM DUAL"))
                result.fetchone()
            
            print("✅ Database connection established successfully!")
            return True
            
        except SQLAlchemyError as e:
            print(f"❌ Database connection failed: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return False
    
    def get_session(self):
        """Get database session"""
        if self.session_local is None:
            raise RuntimeError("Database not initialized. Call initialize_connection() first.")
        
        return self.session_local()
    
    def test_connection(self) -> bool:
        """Test database connectivity"""
        if not self.engine:
            return self.initialize_connection()
        
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT SYSDATE FROM DUAL"))
                current_time = result.fetchone()
                print(f"✅ Database test successful. Server time: {current_time[0]}")
                return True
        except Exception as e:
            print(f"❌ Database test failed: {str(e)}")
            return False

# Global database manager instance
db_manager = DatabaseManager()
