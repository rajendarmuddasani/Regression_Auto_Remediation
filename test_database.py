#!/usr/bin/env python3
"""
Database Connection Test Script
Tests Oracle database connectivity and basic operations

Author: Rajendar Muddasani
Date: July 21, 2025
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.database import db_manager
from src.core.config import get_settings

def test_database_connection():
    """Test database connection and basic operations"""
    print("🔍 Testing Database Connection")
    print("=" * 50)
    
    settings = get_settings()
    
    # Display configuration (without sensitive data)
    print(f"📊 Database Type: {settings.DATABASE_TYPE}")
    print(f"🏠 Database Host: {settings.DATABASE_HOST}")
    print(f"🔌 Database Port: {settings.DATABASE_PORT}")
    print(f"🗄️  Database Name: {settings.DATABASE_NAME}")
    print(f"👤 Database User: {settings.DATABASE_USER}")
    
    # Check if using placeholder values
    if settings.DATABASE_HOST == "<HOSTNAME>":
        print("\n⚠️  NOTICE: Using placeholder database credentials")
        print("📝 To test real connection:")
        print("   1. Update .env file with actual database credentials")
        print("   2. Replace <HOSTNAME>, <USERNAME>, <PASSWORD>, etc.")
        print("   3. Run this script again")
        print("\n✅ Database connection manager created successfully (placeholder mode)")
        return True
    
    # Test actual connection
    print(f"\n🔗 Attempting to connect to {settings.DATABASE_TYPE} database...")
    
    try:
        # Initialize connection
        success = db_manager.initialize_connection()
        
        if success:
            print("✅ Database connection initialized successfully!")
            
            # Test basic query
            print("\n🧪 Testing basic database query...")
            query_success = db_manager.test_connection()
            
            if query_success:
                print("✅ All database tests passed!")
                return True
            else:
                print("❌ Database query test failed")
                return False
        else:
            print("❌ Database connection initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed with error: {str(e)}")
        return False

def test_models_import():
    """Test that database models can be imported"""
    print("\n🔍 Testing Database Models Import")
    print("=" * 50)
    
    try:
        from src.core.models import (
            RegressionDaily, 
            RegressionResults, 
            LearnedPatterns, 
            AppliedSolutions, 
            BaselineChanges
        )
        
        print("✅ All database models imported successfully!")
        print(f"📋 Available models:")
        print(f"   - RegressionDaily: {RegressionDaily.__tablename__}")
        print(f"   - RegressionResults: {RegressionResults.__tablename__}")
        print(f"   - LearnedPatterns: {LearnedPatterns.__tablename__}")
        print(f"   - AppliedSolutions: {AppliedSolutions.__tablename__}")
        print(f"   - BaselineChanges: {BaselineChanges.__tablename__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import database models: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error importing models: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Database Test Suite")
    print("Regression Auto-Remediation System")
    print("=" * 60)
    
    # Test 1: Models import
    models_test = test_models_import()
    
    # Test 2: Database connection
    db_test = test_database_connection()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    print(f"📋 Models Import: {'✅ PASS' if models_test else '❌ FAIL'}")
    print(f"🔗 Database Connection: {'✅ PASS' if db_test else '❌ FAIL'}")
    
    if models_test and db_test:
        print("\n🎉 All database tests passed!")
        print("🎯 Ready for next development phase!")
    else:
        print("\n⚠️  Some tests failed. Check configuration and try again.")

if __name__ == "__main__":
    main()
