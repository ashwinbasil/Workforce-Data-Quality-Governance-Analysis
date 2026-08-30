import sqlite3
import sys
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("data/processed/workforce.db")
SQL_CHECKS = Path("sql/dq_workforce_checks.sql")
SQL_SLA = Path("sql/dq_sla_rules.sql")

# Every column the checks SQL file expects to exist. If the schema
# ever drifts (a rename, a re-export, a new ingestion script), this
# catches it with a hard error BEFORE running checks, instead of
# letting SQLite silently reinterpret unmatched quoted identifiers
# as string literals (which is what caused a ~100% false failure
# rate on the payscale check previously: "Payscale Minimum (£)"
# didn't match any real column, so SQLite treated it as a constant
# string and compared two literals instead of two columns).
EXPECTED_COLUMNS = {
    "parent_department",
    "organisation",
    "unit",
    "reporting_senior_post",
    "grade",
    "payscale_minimum",
    "payscale_maximum",
    "generic_job_title",
    "fte_posts",
    "professional/occupational_group",
    "office_region",
}


def assert_schema(conn: sqlite3.Connection) -> None:
    actual = {row[1] for row in conn.execute("PRAGMA table_info(workforce)")}
    missing = EXPECTED_COLUMNS - actual
    if missing:
        sys.exit(
            "SCHEMA MISMATCH: the following columns are expected by "
            f"{SQL_CHECKS} but do not exist in workforce.db: {sorted(missing)}\n"
            f"Actual columns in workforce table: {sorted(actual)}\n"
            "Refusing to run checks. Update EXPECTED_COLUMNS and the SQL "
            "file to match the real schema before proceeding."
        )


conn = sqlite3.connect(DB_PATH)
assert_schema(conn)

# --- pre-flight diagnostic: catch a payscale column swap in future
# data refreshes before it silently reads as a real DQ failure ---
diag = pd.read_sql_query(
    """
    SELECT
        COUNT(*) AS total_rows,
        SUM(CASE WHEN payscale_minimum > payscale_maximum THEN 1 ELSE 0 END) AS min_gt_max_rows
    FROM workforce
    WHERE payscale_minimum IS NOT NULL AND payscale_maximum IS NOT NULL
    """,
    conn,
)
total = int(diag["total_rows"].iloc[0])
bad = int(diag["min_gt_max_rows"].iloc[0])
if total > 0 and bad / total > 0.5:
    print(
        f"WARNING: {bad}/{total} rows ({bad/total:.0%}) have "
        "payscale_minimum > payscale_maximum. This looks like a "
        "column swap at ingestion, not a real finding. Check the "
        "CSV-to-DB column mapping before trusting this check."
    )

# --- run data quality checks ---
with open(SQL_CHECKS, "r") as f:
    conn.executescript(f.read())

timestamp = datetime.now(timezone.utc).isoformat()

dq_df = pd.read_sql_query(
    """
    SELECT check_name, COUNT(*) AS failed_rows, ? AS check_timestamp
    FROM dq_failures
    GROUP BY check_name
    """,
    conn,
    params=[timestamp],
)
dq_df.to_sql("dq_audit_log", conn, if_exists="append", index=False)
print("DQ checks executed")
print(dq_df.to_string(index=False))

# --- load SLA rules ---
with open(SQL_SLA, "r") as f:
    conn.executescript(f.read())
print("SLA rules loaded")

# --- evaluate SLA (latest run only, not full history) ---
sla_df = pd.read_sql_query(
    """
    SELECT
        a.check_name,
        a.failed_rows,
        s.max_failed_rows,
        s.severity,
        CASE WHEN a.failed_rows > s.max_failed_rows THEN 'FAIL' ELSE 'PASS' END AS sla_status,
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
