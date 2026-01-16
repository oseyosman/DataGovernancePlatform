-- Data Governance Platform Database Schema
-- Author: Osman Yildiz
-- Walsh College MSIT Capstone Project

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'compliance_officer', 'data_steward', 'viewer')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Data Quality Metrics Table (Phase 2)
CREATE TABLE IF NOT EXISTS data_quality_metrics (
    id SERIAL PRIMARY KEY,
    dataset_name VARCHAR(100) NOT NULL,
    completeness_score DECIMAL(5,2),
    accuracy_score DECIMAL(5,2),
    consistency_score DECIMAL(5,2),
    timeliness_score DECIMAL(5,2),
    overall_score DECIMAL(5,2),
    checked_by INTEGER REFERENCES users(id),
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Access Controls Table (Phase 2)
CREATE TABLE IF NOT EXISTS access_controls (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    resource_name VARCHAR(100) NOT NULL,
    access_level VARCHAR(20) NOT NULL,
    granted_by INTEGER REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_reviewed TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active'
);

-- Compliance Requirements Table (Phase 2)
CREATE TABLE IF NOT EXISTS compliance_requirements (
    id SERIAL PRIMARY KEY,
    standard_name VARCHAR(50) NOT NULL,
    control_id VARCHAR(50) NOT NULL,
    control_description TEXT,
    status VARCHAR(20) NOT NULL CHECK (status IN ('compliant', 'non_compliant', 'in_progress', 'not_applicable')),
    last_assessed TIMESTAMP,
    assessed_by INTEGER REFERENCES users(id),
    evidence_link VARCHAR(255),
    notes TEXT
);

-- Alerts Table (Phase 2)
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    message TEXT NOT NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolved_by INTEGER REFERENCES users(id)
);

-- Audit Log Table (Phase 2)
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(50),
    record_id INTEGER,
    old_value TEXT,
    new_value TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample admin user (password: Admin123!)
-- Note: This is for development only. In production, create admin through application.
INSERT INTO users (username, email, password_hash, role)
VALUES ('admin', 'admin@datagovernance.local', '$2b$12$KIXxLZwC8q8yv5rN5xY3mOVxPJlJzJ5xYxYxYxYxYxYxYxYxYxYxY', 'admin')
ON CONFLICT (username) DO NOTHING;

-- Comments for documentation
COMMENT ON TABLE users IS 'User accounts with role-based access control';
COMMENT ON TABLE data_quality_metrics IS 'Data quality assessment scores and history';
COMMENT ON TABLE access_controls IS 'User access permissions and review tracking';
COMMENT ON TABLE compliance_requirements IS 'ISO 27001/27017 compliance controls tracking';
COMMENT ON TABLE alerts IS 'System alerts and notifications';
COMMENT ON TABLE audit_log IS 'Complete audit trail of all system activities';
