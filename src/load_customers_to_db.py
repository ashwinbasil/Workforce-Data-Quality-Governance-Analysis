import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH = "data/processed/customers.db"
CSV_PATH = "data/raw/customers_raw.csv"

# Ensure processed directory exists
Path("data/processed").mkdir(parents=True, exist_ok=True)

# Load CSV
df = pd.read_csv(CSV_PATH, parse_dates=["signup_date", "last_active"])

# Connect to SQLite
conn = sqlite3.connect(DB_PATH)

# Write to database
df.to_sql("customers", conn, if_exists="replace", index=False)

conn.close()

print("Customers table loaded into SQLite database.")
