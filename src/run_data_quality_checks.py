import sqlite3
import pandas as pd

DB_PATH = "data/processed/customers.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create audit table
with open("src/create_audit_table.sql") as f:
    cursor.executescript(f.read())

# Run quality checks
with open("src/data_quality_checks.sql") as f:
    queries = f.read().split(";")

for query in queries:
    query = query.strip()
    if not query:
        continue

    df = pd.read_sql_query(query, conn)

    check_name = df.iloc[0]["check_name"]
    failed_rows = int(df.iloc[0]["failed_rows"])

    cursor.execute(
        """
        INSERT INTO dq_audit_log (check_name, failed_rows)
        VALUES (?, ?)
        """,
        (check_name, failed_rows)
    )

conn.commit()
conn.close()

print("Data quality checks executed and logged.")
