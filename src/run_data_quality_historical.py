import sqlite3
import pandas as pd
from datetime import datetime

# Paths
DB_PATH = "data/processed/customers.db"
CHECKS_SQL = "src/data_quality_checks.sql"

# Total number of customers for pct calculation
TOTAL_CUSTOMERS = 5000  # Adjust if dataset changes

# Connect
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Ensure historical table exists
with open("src/create_historical_audit_table.sql") as f:
    cursor.executescript(f.read())

# Run each data quality check
with open(CHECKS_SQL) as f:
    queries = f.read().split(";")

for query in queries:
    query = query.strip()
    if not query:
        continue

    df = pd.read_sql_query(query, conn)
    check_name = df.iloc[0]["check_name"]
    failed_rows = int(df.iloc[0]["failed_rows"])
    pct_failed = failed_rows / TOTAL_CUSTOMERS

    cursor.execute(
        """
        INSERT INTO dq_audit_log_historical (check_name, failed_rows, total_rows, pct_failed)
        VALUES (?, ?, ?, ?)
        """,
        (check_name, failed_rows, TOTAL_CUSTOMERS, pct_failed)
    )

conn.commit()
conn.close()
print(f"Historical DQ run logged at {datetime.now()}")


conn = sqlite3.connect(DB_PATH)
df_hist = pd.read_sql_query("SELECT * FROM dq_audit_log_historical ORDER BY check_timestamp", conn)
df_hist.to_csv("data/processed/dq_audit_log_historical.csv", index=False)
conn.close()
print("Historical CSV exported: data/processed/dq_audit_log_historical.csv")