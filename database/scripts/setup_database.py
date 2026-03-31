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
        
        print("📝 Populating with sample data...")
        
        # Populate sample data
        populate_jira_data(cursor, conn)
        populate_servicenow_data(cursor, conn)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Database populated successfully!")
        
        # Show statistics
        show_database_stats()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

def populate_jira_data(cursor, conn):
    """Populate Jira tables with sample data"""
    
    # Sample data
    projects = ["PROJ", "SUPP", "DEV", "OPS", "SEC"]
    users = ["john.doe", "jane.smith", "bob.wilson", "alice.brown", "charlie.davis"]
    statuses = ["Open", "In Progress", "Resolved", "Closed", "Reopened"]
    priorities = ["Highest", "High", "Medium", "Low"]
    issue_types = ["Bug", "Story", "Task", "Epic", "Incident"]
    
    # Insert projects
    for i, project in enumerate(projects):
        cursor.execute("""
            INSERT INTO jira_projects (project_key, name, description, lead)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (project_key) DO NOTHING
        """, (project, f"Project {project}", f"Description for {project}", users[i % len(users)]))
    
    # Insert users
    for user in users:
        cursor.execute("""
            INSERT INTO jira_users (username, display_name, email)
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
            INSERT INTO jira_issues (
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
    """Populate ServiceNow tables with sample data"""
    
    # Sample data
    departments = ["IT", "HR", "Finance", "Operations", "Legal"]
    groups = ["IT Support", "Network Team", "Security Team", "Database Team", "Application Team"]
    states = ["New", "In Progress", "On Hold", "Resolved", "Closed", "Canceled"]
    priorities = ["1", "2", "3", "4", "5"]  # 1=Critical, 5=Low
    categories = ["Hardware", "Software", "Network", "Database", "Security"]
    
    # Insert groups
    for i, group in enumerate(groups):
        cursor.execute("""
            INSERT INTO sn_groups (sys_id, name, description)
            VALUES (%s, %s, %s)
            ON CONFLICT (sys_id) DO NOTHING
        """, (f"group_{i}", group, f"Description for {group}"))
    
    # Insert users
    for i, dept in enumerate(departments):
        for j in range(20):  # 20 users per department
            user_id = f"user_{i*20 + j:03d}"
            cursor.execute("""
                INSERT INTO sn_users (sys_id, user_name, name, email, department)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (sys_id) DO NOTHING
            """, (user_id, f"user{i*20 + j}", f"User {i*20 + j}", f"user{i*20 + j}@company.com", dept))
    
    # Insert 1000 incidents
    for i in range(1000):
        incident_number = f"INC{i+1:06d}"
        opened_at = datetime.now() - timedelta(days=random.randint(1, 365))
        resolved_at = None
        if random.random() > 0.4:  # 60% resolved
            resolved_at = opened_at + timedelta(hours=random.randint(1, 72))
        
        cursor.execute("""
            INSERT INTO sn_incidents (
                number, sys_id, short_description, description, state, priority,
                assignment_group, assigned_to, caller_id, opened_at, resolved_at,
                category, subcategory
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (number) DO NOTHING
        """, (
            incident_number,
            f"inc_{i:03d}",
            f"Incident {i+1}: {random.choice(['Email', 'VPN', 'Login', 'Server', 'Application'])} issue",
            f"Detailed description for incident {i+1}",
            random.choice(states),
            random.choice(priorities),
            f"group_{random.randint(0, len(groups)-1)}",
            f"user_{random.randint(0, 99):03d}",
            f"user_{random.randint(0, 99):03d}",
            opened_at,
            resolved_at,
            random.choice(categories),
            random.choice(["Subcategory A", "Subcategory B", "Subcategory C"])
        ))
    
    print("✅ ServiceNow data populated (1000 incidents)")

def show_database_stats():
    """Show database statistics"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("\n📊 Database Statistics:")
        
        # Jira stats
        cursor.execute("SELECT COUNT(*) FROM jira_projects")
        print(f"Jira Projects: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM jira_users")
        print(f"Jira Users: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM jira_issues")
        print(f"Jira Issues: {cursor.fetchone()[0]}")
        
        # ServiceNow stats
        cursor.execute("SELECT COUNT(*) FROM sn_groups")
        print(f"ServiceNow Groups: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM sn_users")
        print(f"ServiceNow Users: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM sn_incidents")
        print(f"ServiceNow Incidents: {cursor.fetchone()[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error getting stats: {e}")

if __name__ == "__main__":
    setup_database()
