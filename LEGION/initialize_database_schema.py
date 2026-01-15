#!/usr/bin/env python3
"""
Database Schema Initialization Script
Initialize Phase 6 Database Schema Extensions for Enterprise Dashboard
"""

import os
import sys
from datetime import datetime
from enterprise_database_service import EnterpriseDatabase

def main():
    """Initialize the complete database schema."""
    print("🚀 Enterprise Database Schema Initialization")
    print("=" * 50)
    
    # Initialize database service
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'data', 'enterprise_operations.db')
    
    print(f"📂 Database Path: {db_path}")
    
    # Check if data directory exists
    data_dir = os.path.dirname(db_path)
    if not os.path.exists(data_dir):
        print(f"📁 Creating data directory: {data_dir}")
        os.makedirs(data_dir, exist_ok=True)
    
    # Initialize database
    db = EnterpriseDatabase(db_path)
    
    if not db.connect():
        print("❌ Failed to connect to database")
        sys.exit(1)
    
    print(f"✅ Database connection established")
    
    # Initialize complete schema
    if db.initialize_complete_schema():
        print("\n🎉 SUCCESS: Database schema initialization completed!")
        print("\n📊 Phase 6 Database Schema Extensions Summary:")
        print("   ✅ Task 20.1: Dashboard Configuration Tables")
        print("   ✅ Task 20.2: System Metrics Logging Tables")
        print("   ✅ Task 20.3: User Preferences and Settings Tables")
        print("   ✅ Task 20.4: Dashboard Usage Analytics Tables")
        print("   ✅ Task 20.5: System Health Monitoring Tables")
        print("   ✅ Task 20.6: Alert and Notification History Tables")
        print("   ✅ Task 20.7: Optimization Metrics Tracking Tables")
        print("   ✅ Task 20.8: Audit Trail and Change Tracking Tables")
        
        # Get table count
        tables = db.execute_query("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        
        print(f"\n📈 Total Database Tables: {len(tables)}")
        print("📋 Table List:")
        for table in tables:
            print(f"   • {table['name']}")
        
        print(f"\n⏰ Schema initialized at: {datetime.now().isoformat()}")
        print("🔗 Ready for enterprise dashboard integration!")
        
    else:
        print("❌ FAILED: Database schema initialization failed")
        sys.exit(1)
    
    # Cleanup
    db.disconnect()
    print("\n✅ Database connection closed")

if __name__ == "__main__":
    main()
