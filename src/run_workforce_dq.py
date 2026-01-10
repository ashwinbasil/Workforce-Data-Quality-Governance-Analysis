import sqlite3
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("data/processed/workforce.db")
SQL_CHECKS = Path("sql/dq_workforce_checks.sql")
SQL_SLA = Path("sql/dq_sla_rules.sql")

# --- connect ---
conn = sqlite3.connect(DB_PATH)

# --- run data quality checks ---
with open(SQL_CHECKS, "r") as f:
    conn.executescript(f.read())

timestamp = datetime.now(timezone.utc).isoformat()

dq_df = pd.read_sql_query("""
SELECT
    check_name,
    COUNT(*) AS failed_rows,
    ? AS check_timestamp
FROM dq_failures
GROUP BY check_name
""", conn, params=[timestamp])

dq_df.to_sql("dq_audit_log", conn, if_exists="append", index=False)

print("DQ checks executed")

# --- load SLA rules ---
with open(SQL_SLA, "r") as f:
    conn.executescript(f.read())

print("SLA rules loaded")

# --- evaluate SLA ---
sla_df = pd.read_sql_query("""
SELECT 
    a.check_name,
    a.failed_rows,
    s.max_failed_rows,
    s.severity,
    CASE 
        WHEN a.failed_rows > s.max_failed_rows THEN 'FAIL'
        ELSE 'PASS'
    END AS sla_status,
    a.check_timestamp
FROM dq_audit_log a
JOIN dq_sla_rules s USING (check_name)
ORDER BY s.severity DESC
""", conn)

sla_df.to_csv("data/processed/dq_sla_evaluation.csv", index=False)

print("SLA evaluation exported")

conn.close()
