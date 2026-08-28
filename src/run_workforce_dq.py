import sqlite3
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("data/processed/workforce.db")
SQL_CHECKS = Path("sql/dq_workforce_checks.sql")
SQL_SLA = Path("sql/dq_sla_rules.sql")

# --- connect ---
conn = sqlite3.connect(DB_PATH)

# --- pre-flight diagnostic: catch a payscale column swap before it
# silently produces a near-100% failure rate again ---
diag = pd.read_sql_query(
    """
    SELECT
        COUNT(*) AS total_rows,
        SUM(CASE WHEN "Payscale Minimum (£)" > "Payscale Maximum (£)" THEN 1 ELSE 0 END) AS min_gt_max_rows
    FROM workforce
    WHERE "Payscale Minimum (£)" IS NOT NULL
      AND "Payscale Maximum (£)" IS NOT NULL
    """,
    conn,
)
total = int(diag["total_rows"].iloc[0])
bad = int(diag["min_gt_max_rows"].iloc[0])
if total > 0 and bad / total > 0.5:
    print(
        f"WARNING: {bad}/{total} rows ({bad/total:.0%}) have "
        f'"Payscale Minimum (£)" > "Payscale Maximum (£)". '
        "This looks like a column swap at ingestion, not a real "
        "finding. Check your CSV-to-DB column mapping before "
        "trusting the payscale_min_greater_than_max check output."
    )

# --- run data quality checks ---
with open(SQL_CHECKS, "r") as f:
    conn.executescript(f.read())

timestamp = datetime.now(timezone.utc).isoformat()

dq_df = pd.read_sql_query(
    """
    SELECT
        check_name,
        COUNT(*) AS failed_rows,
        ? AS check_timestamp
    FROM dq_failures
    GROUP BY check_name
    """,
    conn,
    params=[timestamp],
)
dq_df.to_sql("dq_audit_log", conn, if_exists="append", index=False)
print("DQ checks executed")

# --- load SLA rules ---
with open(SQL_SLA, "r") as f:
    conn.executescript(f.read())
print("SLA rules loaded")

# --- evaluate SLA (latest run only) ---
# dq_audit_log accumulates one batch of rows per script execution.
# Without pinning to the latest check_timestamp, this join pulls in
# every historical run and produces duplicate rows per check_name,
# which silently corrupts the exported CSV once the script has been
# run more than once.
sla_df = pd.read_sql_query(
    """
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
    WHERE a.check_timestamp = (SELECT MAX(check_timestamp) FROM dq_audit_log)
    ORDER BY s.severity DESC
    """,
    conn,
)
sla_df.to_csv("data/processed/dq_sla_evaluation.csv", index=False)
print("SLA evaluation exported")

conn.close()
