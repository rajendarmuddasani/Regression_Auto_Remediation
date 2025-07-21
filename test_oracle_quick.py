#!/usr/bin/env python3
"""
Quick Oracle Connection Test
Simple script to test Oracle database connectivity

Author: Rajendar Muddasani
Date: July 21, 2025
"""

import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_oracle_quick():
    """Quick Oracle connection test"""
    print("🔍 Quick Oracle Connection Test")
    print("=" * 40)
    
    try:
        from src.core.config import get_settings
        from src.core.database import db_manager
        
        settings = get_settings()
        print(f"🔗 Connecting to: {settings.DATABASE_HOST}:{settings.DATABASE_PORT}")
        print(f"📊 Database: {settings.DATABASE_NAME}")
        print(f"👤 User: {settings.DATABASE_USER}")
        
        # Test connection
        success = db_manager.initialize_connection()
        
        if success:
            print("✅ Oracle connection successful!")
            
            # Test a simple query
            print("🧪 Testing query...")
            if db_manager.test_connection():
                print("✅ Query test successful!")
                
                # Try to check if our tables exist
                print("🔍 Checking for regression tables...")
                try:
                    session = db_manager.get_session()
                    
                    # Check if REGRESSION_DAILY table exists
                    result = session.execute("""
                        SELECT COUNT(*) FROM USER_TABLES 
                        WHERE TABLE_NAME = 'REGRESSION_DAILY'
                    """)
                    table_exists = result.fetchone()[0] > 0
                    
                    if table_exists:
                        print("✅ REGRESSION_DAILY table found!")
                        
                        # Get some sample data
                        result = session.execute("""
                            SELECT COUNT(*) FROM REGRESSION_DAILY 
                            WHERE ROWNUM <= 1
                        """)
                        count = result.fetchone()[0]
                        print(f"📊 Table has data: {count > 0}")
                    else:
                        print("⚠️  REGRESSION_DAILY table not found")
                        print("📝 You may need to create tables or check table names")
                    
                    session.close()
                    
                except Exception as e:
                    print(f"⚠️  Table check failed: {str(e)}")
                
            return True
        else:
            print("❌ Oracle connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Oracle Database Quick Test")
    print("Regression Auto-Remediation System")
    print("=" * 50)
    
    success = test_oracle_quick()
    
    if success:
        print("\n🎉 Oracle database is ready!")
        print("🎯 Next: Create database tables and start development")
    else:
        print("\n📝 To fix:")
        print("1. Edit ../.env file")
        print("2. Replace <REPLACE_WITH_ACTUAL_PASSWORD> with real password")
        print("3. Run this script again")
