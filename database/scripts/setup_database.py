#!/usr/bin/env python3
"""
PostgreSQL database setup script - Create tables and populate with 1000 rows each
"""

import psycopg2
import random
from datetime import datetime, timedelta

# Database connection
DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "metrics_db",
    "user": "metrics_user",
    "password": "metrics_password"
}

def setup_database():
    """Create database and populate with sample data"""
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🔧 Connected to PostgreSQL")
        
        # Create schemas
        create_schemas(cursor, conn)
        
        print("📝 Populating with sample data...")
        
        # Populate sample data
        populate_jira_data(cursor, conn)
        populate_servicenow_data(cursor, conn)
        
        # Populate ServiceNow references for Jira issues
        populate_snow_references(cursor, conn)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Database populated successfully!")
        
        # Show statistics
        show_database_stats()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

def create_schemas(cursor, conn):
    """Create schemas for different domains"""
    
    # Create schemas
    schemas = ['jira', 'servicenow']
    for schema in schemas:
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    
    print("✅ Created schemas: jira, servicenow")

def populate_snow_references(cursor, conn):
    """Populate snow_ref field for 700 out of 1000 Jira issues"""
    
    # Get all ServiceNow incident IDs
    cursor.execute("SELECT incident_id FROM servicenow.sn_incidents ORDER BY incident_id")
    snow_incidents = [row[0] for row in cursor.fetchall()]
    
    # Get all Jira issue IDs
    cursor.execute("SELECT issue_id, issue_key FROM jira.jira_issues ORDER BY issue_id")
    jira_issues = cursor.fetchall()
    
    # Select 700 random Jira issues to update
    selected_issues = random.sample(jira_issues, 700)
    
    # Assign ServiceNow incident numbers to selected Jira issues
    for i, (issue_id, issue_key) in enumerate(selected_issues):
        snow_ref = snow_incidents[i % len(snow_incidents)]  # Cycle through incidents if needed
        cursor.execute(
            "UPDATE jira.jira_issues SET snow_ref = %s WHERE issue_id = %s",
            (snow_ref, issue_id)
        )
    
    print("✅ ServiceNow references populated (700 Jira issues linked)")

def populate_jira_data(cursor, conn):
    """Populate Jira tables with sample data"""
    
    # Create Jira tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jira.jira_projects (
            project_key VARCHAR(10) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            lead VARCHAR(100)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jira.jira_users (
            username VARCHAR(100) PRIMARY KEY,
            display_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jira.jira_issues (
            issue_id SERIAL PRIMARY KEY,
            issue_key VARCHAR(20) UNIQUE NOT NULL,
            summary VARCHAR(500) NOT NULL,
            status VARCHAR(50) NOT NULL,
            priority VARCHAR(20) NOT NULL,
            issue_type VARCHAR(50) NOT NULL,
            project_key VARCHAR(10) REFERENCES jira.jira_projects(project_key),
            assignee VARCHAR(100) REFERENCES jira.jira_users(username),
            reporter VARCHAR(100) REFERENCES jira.jira_users(username),
            created_date TIMESTAMP NOT NULL,
            resolved_date TIMESTAMP,
            original_estimate_hours INTEGER,
            time_spent_seconds INTEGER,
            snow_ref VARCHAR(20)
        )
    """)
    
    # Sample data
    projects = ["PROJ", "SUPP", "DEV", "OPS", "SEC"]
    users = ["john.doe", "jane.smith", "bob.wilson", "alice.brown", "charlie.davis"]
    statuses = ["Open", "In Progress", "Resolved", "Closed", "Reopened"]
    priorities = ["Highest", "High", "Medium", "Low"]
    issue_types = ["Bug", "Story", "Task", "Epic", "Incident"]
    
    # Insert projects
    for i, project in enumerate(projects):
        cursor.execute("""
            INSERT INTO jira.jira_projects (project_key, name, description, lead)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (project_key) DO NOTHING
        """, (project, f"Project {project}", f"Description for {project}", users[i % len(users)]))
    
    # Insert users
    for user in users:
        cursor.execute("""
            INSERT INTO jira.jira_users (username, display_name, email)
            VALUES (%s, %s, %s)
            ON CONFLICT (username) DO NOTHING
        """, (user, user.replace(".", " ").title(), f"{user}@company.com"))
    
    # Insert 1000 issues
    for i in range(1000):
        issue_key = f"{random.choice(projects)}-{i+1:04d}"
        created_date = datetime.now() - timedelta(days=random.randint(1, 365))
        resolved_date = None
        if random.random() > 0.3:  # 70% resolved
            resolved_date = created_date + timedelta(days=random.randint(1, 30))
        
        cursor.execute("""
            INSERT INTO jira.jira_issues (
                issue_key, summary, status, priority, issue_type,
                project_key, assignee, reporter, created_date, resolved_date,
                original_estimate_hours, time_spent_seconds
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (issue_key) DO NOTHING
        """, (
            issue_key,
            f"Issue {i+1}: {random.choice(['Login', 'Database', 'UI', 'API', 'Performance'])} issue",
            random.choice(statuses),
            random.choice(priorities),
            random.choice(issue_types),
            random.choice(projects),
            random.choice(users),
            random.choice(users),
            created_date,
            resolved_date,
            random.randint(1, 40),
            random.randint(3600, 28800)  # 1-8 hours in seconds
        ))
    
    print("✅ Jira data populated (1000 issues)")

def populate_servicenow_data(cursor, conn):
    """Populate ServiceNow table with sample data"""
    
    # Drop existing table to recreate with correct schema
    cursor.execute("DROP TABLE IF EXISTS servicenow.sn_incidents")
    
    # Create ServiceNow table
    cursor.execute("""
        CREATE TABLE servicenow.sn_incidents (
            incident_id VARCHAR(20) PRIMARY KEY,
            summary VARCHAR(500) NOT NULL,
            description TEXT,
            status VARCHAR(50) NOT NULL,
            priority VARCHAR(10) NOT NULL,
            impact VARCHAR(20) NOT NULL,
            assigned_group VARCHAR(100) NOT NULL,
            opened_at TIMESTAMP NOT NULL,
            resolved_at TIMESTAMP,
            due_date TIMESTAMP
        )
    """)
    
    # Sample data
    groups = ["IT Support", "Network Team", "Security Team", "Database Team", "Application Team"]
    states = ["New", "In Progress", "On Hold", "Resolved", "Closed", "Canceled"]
    priorities = ["1", "2", "3", "4", "5"]  # 1=Critical, 5=Low
    impacts = ["High", "Medium", "Low"]
    
    # Insert 1000 incidents
    for i in range(1000):
        incident_id = f"INC{i+1:06d}"
        opened_at = datetime.now() - timedelta(days=random.randint(1, 365))
        resolved_at = None
        if random.random() > 0.4:  # 60% resolved
            resolved_at = opened_at + timedelta(hours=random.randint(1, 72))
        
        cursor.execute("""
            INSERT INTO servicenow.sn_incidents (
                incident_id, summary, description, status, priority, impact,
                assigned_group, opened_at, resolved_at, due_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            incident_id,
            f"Incident {i+1}: {random.choice(['Email', 'VPN', 'Login', 'Server', 'Application'])} issue",
            f"Detailed description for incident {i+1}",
            random.choice(states),
            random.choice(priorities),
            random.choice(impacts),
            random.choice(groups),  # Direct group name!
            opened_at,
            resolved_at,
            opened_at + timedelta(days=random.randint(1, 30)) if random.random() > 0.5 else None
        ))
    
    print("✅ ServiceNow data populated (1000 incidents)")

def show_database_stats():
    """Show database statistics"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("\n📊 Database Statistics:")
        
        # Jira stats
        cursor.execute("SELECT COUNT(*) FROM jira.jira_projects")
        print(f"Jira Projects: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM jira.jira_users")
        print(f"Jira Users: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM jira.jira_issues")
        jira_count = cursor.fetchone()[0]
        print(f"Jira Issues: {jira_count}")
        
        cursor.execute("SELECT COUNT(*) FROM jira.jira_issues WHERE snow_ref IS NOT NULL")
        snow_ref_count = cursor.fetchone()[0]
        print(f"Jira Issues with ServiceNow refs: {snow_ref_count}")
        
        # ServiceNow stats
        cursor.execute("SELECT COUNT(*) FROM servicenow.sn_incidents")
        print(f"ServiceNow Incidents: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT assigned_group, COUNT(*) FROM servicenow.sn_incidents GROUP BY assigned_group")
        print("ServiceNow Incidents by group:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error getting stats: {e}")

if __name__ == "__main__":
    setup_database()
