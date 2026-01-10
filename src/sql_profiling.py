import sqlite3
import pandas as pd

# Connect to SQLite (in-memory DB)
conn = sqlite3.connect(':memory:')
cur = conn.cursor()

# Load CSV into SQLite
df = pd.read_csv('../data/raw/customers_raw.csv')
df.to_sql('customers', conn, index=False, if_exists='replace')

# 1. Count missing values per column
print("Missing values per column:")
for col in df.columns:
    cur.execute(f"SELECT COUNT(*) FROM customers WHERE {col} IS NULL")
    count = cur.fetchone()[0]
    print(f"{col}: {count}")

# 2. Detect duplicate emails
cur.execute("""
SELECT email, COUNT(*) AS cnt
FROM customers
WHERE email IS NOT NULL
GROUP BY email
HAVING cnt > 1
""")
duplicates = cur.fetchall()
print("\nDuplicate emails:")
print(duplicates[:5])  # Show first 5 duplicates

# 3. Invalid emails
cur.execute("""
SELECT email
FROM customers
WHERE email NOT LIKE '%_@_%._%'
""")
invalid_emails = cur.fetchall()
print("\nInvalid emails:")
print(invalid_emails[:5])

# 4. Recent activity by country
cur.execute("""
SELECT country, COUNT(*) AS total_customers,
       AVG(julianday('now') - julianday(last_active)) AS avg_days_since_active
FROM customers
GROUP BY country
""")
recent_activity = cur.fetchall()
print("\nAverage days since last active by country:")
for row in recent_activity:
    print(row)

conn.close()
