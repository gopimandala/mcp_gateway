#!/usr/bin/env python3
"""
Simple test script to verify database setup
"""

import psycopg2

# Database connection
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "metrics_db",
    "user": "metrics_user",
    "password": "metrics_password"
}

def test_database():
    """Test database connectivity and data"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Print table schemas
        print("📋 Database Schemas:")
        
        # Jira tables schema
        print("\n🔷 Jira Tables Schema:")
        jira_tables = ['jira_issues', 'jira_projects', 'jira_users']
        for table in jira_tables:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """, (table,))
            columns = cursor.fetchall()
            print(f"\n  {table}:")
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                default = f" DEFAULT {col[3]}" if col[3] else ""
                print(f"    - {col[0]}: {col[1]} {nullable}{default}")
        
        # ServiceNow tables schema
        print("\n❄️ ServiceNow Tables Schema:")
        snow_tables = ['sn_incidents', 'sn_groups', 'sn_users']
        for table in snow_tables:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """, (table,))
            columns = cursor.fetchall()
            print(f"\n  {table}:")
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                default = f" DEFAULT {col[3]}" if col[3] else ""
                print(f"    - {col[0]}: {col[1]} {nullable}{default}")
        
        # Test data counts
        print("\n🎯 Database Test Results:")
        
        # Test Jira data
        cursor.execute("SELECT COUNT(*) FROM jira_issues")
        jira_count = cursor.fetchone()[0]
        
        # Test ServiceNow data
        cursor.execute("SELECT COUNT(*) FROM sn_incidents")
        snow_count = cursor.fetchone()[0]
        
        # Test basic queries
        cursor.execute("SELECT COUNT(*) FROM jira_projects")
        jira_projects = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sn_groups")
        snow_groups = cursor.fetchone()[0]
        
        print(f"  Jira Issues: {jira_count}")
        print(f"  ServiceNow Incidents: {snow_count}")
        print(f"  Jira Projects: {jira_projects}")
        print(f"  ServiceNow Groups: {snow_groups}")
        
        # Verify expected counts
        if jira_count == 1000 and snow_count == 1000:
            print("✅ Database setup verification PASSED!")
        else:
            print("❌ Database setup verification FAILED!")
            print(f"Expected: 1000 Jira issues, 1000 ServiceNow incidents")
            print(f"Got: {jira_count} Jira issues, {snow_count} ServiceNow incidents")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")

if __name__ == "__main__":
    test_database()
