#!/usr/bin/env python3
"""
Update Jira schema and populate snow_ref field
"""

import psycopg2
import random

# Database connection
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "metrics_db",
    "user": "metrics_user",
    "password": "metrics_password"
}

def update_jira_schema():
    """Add snow_ref field to jira_issues table"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Add snow_ref column if it doesn't exist
        cursor.execute("""
            ALTER TABLE jira_issues 
            ADD COLUMN IF NOT EXISTS snow_ref character varying NULL;
        """)
        
        conn.commit()
        print("✅ Added snow_ref column to jira_issues table")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        raise

def populate_snow_refs():
    """Populate 700 out of 1000 Jira issues with ServiceNow incident numbers"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get all ServiceNow incident numbers
        cursor.execute("SELECT number FROM sn_incidents ORDER BY number")
        snow_incidents = [row[0] for row in cursor.fetchall()]
        
        # Get all Jira issue IDs
        cursor.execute("SELECT issue_id, issue_key FROM jira_issues ORDER BY issue_id")
        jira_issues = cursor.fetchall()
        
        # Clear existing snow_ref values
        cursor.execute("UPDATE jira_issues SET snow_ref = NULL")
        
        # Select 700 random Jira issues to update
        selected_issues = random.sample(jira_issues, 700)
        
        # Assign ServiceNow incident numbers to selected Jira issues
        for i, (issue_id, issue_key) in enumerate(selected_issues):
            snow_ref = snow_incidents[i % len(snow_incidents)]  # Cycle through incidents if needed
            cursor.execute(
                "UPDATE jira_issues SET snow_ref = %s WHERE issue_id = %s",
                (snow_ref, issue_id)
            )
        
        conn.commit()
        
        # Verify results
        cursor.execute("SELECT COUNT(*) FROM jira_issues WHERE snow_ref IS NOT NULL")
        populated_count = cursor.fetchone()[0]
        
        print(f"✅ Populated {populated_count} Jira issues with ServiceNow references")
        
        # Show some examples
        cursor.execute("""
            SELECT issue_key, snow_ref 
            FROM jira_issues 
            WHERE snow_ref IS NOT NULL 
            ORDER BY issue_id 
            LIMIT 5
        """)
        examples = cursor.fetchall()
        print("\n📋 Example mappings:")
        for issue_key, snow_ref in examples:
            print(f"  {issue_key} -> {snow_ref}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error populating snow_ref: {e}")
        raise

if __name__ == "__main__":
    print("🔧 Updating Jira schema and populating snow_ref...")
    update_jira_schema()
    populate_snow_refs()
    print("✅ Update completed!")
