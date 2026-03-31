-- Jira Database Schema (PostgreSQL)
CREATE TABLE jira_projects (
    project_key VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    lead VARCHAR(255),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE jira_users (
    username VARCHAR(255) PRIMARY KEY,
    display_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE jira_issues (
    issue_id SERIAL PRIMARY KEY,
    issue_key VARCHAR(50) UNIQUE NOT NULL,
    summary TEXT NOT NULL,
    status VARCHAR(50) NOT NULL,
    priority VARCHAR(20),
    issue_type VARCHAR(50),
    project_key VARCHAR(50) REFERENCES jira_projects(project_key),
    assignee VARCHAR(255) REFERENCES jira_users(username),
    reporter VARCHAR(255) REFERENCES jira_users(username),
    created_date TIMESTAMP NOT NULL,
    resolved_date TIMESTAMP,
    due_date TIMESTAMP,
    original_estimate_hours INTEGER,
    remaining_estimate_hours INTEGER,
    time_spent_seconds INTEGER
);

-- Indexes for performance
CREATE INDEX idx_jira_issues_project ON jira_issues(project_key);
CREATE INDEX idx_jira_issues_status ON jira_issues(status);
CREATE INDEX idx_jira_issues_assignee ON jira_issues(assignee);
CREATE INDEX idx_jira_issues_created_date ON jira_issues(created_date);
CREATE INDEX idx_jira_issues_priority ON jira_issues(priority);
