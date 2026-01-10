CREATE TABLE IF NOT EXISTS dq_audit_log (
    check_name TEXT,
    failed_rows INTEGER,
    check_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
