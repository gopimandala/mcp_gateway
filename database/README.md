# PostgreSQL Database Setup

## 🐳 Quick Start

### 1. Start PostgreSQL Container
```bash
cd database
docker-compose up -d
```

### 2. Install psycopg2 (if needed)
```bash
pip install psycopg2-binary
```

### 3. Populate with Sample Data
```bash
cd scripts
python setup_database.py
```

## 📊 What You Get

- **5 Jira projects** with different teams
- **5 Jira users** (developers, support staff)
- **1000 Jira issues** with realistic data
- **5 ServiceNow groups** (IT, Network, Security, etc.)
- **100 ServiceNow users** across 5 departments
- **1000 ServiceNow incidents** with various priorities

## 🔍 Database Structure

### Jira Tables
- `jira_projects` - Project information
- `jira_users` - User accounts
- `jira_issues` - Main issue data (1000 rows)

### ServiceNow Tables
- `sn_groups` - Support groups
- `sn_users` - User accounts (100 users)
- `sn_incidents` - Incident records (1000 rows)

## 🧪 Test Connection

```bash
# Connect to database
docker exec -it metrics-postgres psql -U metrics_user -d metrics_db

# Run test queries
SELECT COUNT(*) FROM jira_issues;
SELECT COUNT(*) FROM sn_incidents;
```

## 📈 Sample Queries

```sql
-- Jira metrics
SELECT status, COUNT(*) FROM jira_issues GROUP BY status;

-- ServiceNow metrics  
SELECT priority, COUNT(*) FROM sn_incidents GROUP BY priority;

-- Combined view
SELECT 'Jira' as source, COUNT(*) as tickets FROM jira_issues
UNION ALL
SELECT 'ServiceNow' as source, COUNT(*) as tickets FROM sn_incidents;
```
