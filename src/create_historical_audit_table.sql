CREATE TABLE IF NOT EXISTS dq_audit_log_historical (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    check_name TEXT,
    failed_rows INTEGER,
    total_rows INTEGER,
    pct_failed REAL,
    check_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
