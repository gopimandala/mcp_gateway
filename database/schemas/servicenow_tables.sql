-- ServiceNow Database Schema (PostgreSQL)
CREATE TABLE sn_users (
    sys_id VARCHAR(32) PRIMARY KEY,
    user_name VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    department VARCHAR(100),
    active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sn_groups (
    sys_id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sn_incidents (
    number VARCHAR(50) PRIMARY KEY,
    sys_id VARCHAR(32) UNIQUE NOT NULL,
    short_description TEXT NOT NULL,
    description TEXT,
    state VARCHAR(20) NOT NULL,
    priority VARCHAR(10),
    urgency VARCHAR(10),
    impact VARCHAR(10),
    assignment_group VARCHAR(32) REFERENCES sn_groups(sys_id),
    assigned_to VARCHAR(32) REFERENCES sn_users(sys_id),
    caller_id VARCHAR(32) REFERENCES sn_users(sys_id),
    opened_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    due_date TIMESTAMP,
    category VARCHAR(100),
    subcategory VARCHAR(100)
);

-- Indexes for performance
CREATE INDEX idx_sn_incidents_state ON sn_incidents(state);
CREATE INDEX idx_sn_incidents_priority ON sn_incidents(priority);
CREATE INDEX idx_sn_incidents_assignment_group ON sn_incidents(assignment_group);
CREATE INDEX idx_sn_incidents_opened_at ON sn_incidents(opened_at);
CREATE INDEX idx_sn_incidents_category ON sn_incidents(category);
