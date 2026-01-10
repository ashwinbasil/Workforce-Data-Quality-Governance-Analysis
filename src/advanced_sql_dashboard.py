import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- Setup ---
# Connect to SQLite in memory
conn = sqlite3.connect(':memory:')

# Load CSV into SQLite
df = pd.read_csv('../data/raw/customers_raw.csv')
df.to_sql('customers', conn, index=False, if_exists='replace')

# Ensure output folders exist
os.makedirs('../data/processed', exist_ok=True)
os.makedirs('../outputs/dashboard_plots', exist_ok=True)

# --- 1. Missing Values Percentage ---
missing_pct_query = """
SELECT
    ROUND(100.0 * SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) / COUNT(*),2) AS email_missing_pct,
    ROUND(100.0 * SUM(CASE WHEN phone_number IS NULL THEN 1 ELSE 0 END) / COUNT(*),2) AS phone_missing_pct
FROM customers;
"""
missing_pct = pd.read_sql_query(missing_pct_query, conn)
missing_pct.to_csv('../data/processed/missing_values_pct.csv', index=False)
print("Missing values percentage:\n", missing_pct)

# --- 2. Duplicate Emails ---
duplicate_query = """
SELECT email, COUNT(*) AS freq
FROM customers
WHERE email IS NOT NULL
GROUP BY email
HAVING freq > 1
ORDER BY freq DESC;
"""
duplicates = pd.read_sql_query(duplicate_query, conn)
duplicates.to_csv('../data/processed/duplicate_emails.csv', index=False)
print("\nDuplicate emails (top 5):\n", duplicates.head())

# --- 3. Inactive Customers (>1 year) ---
inactive_query = """
SELECT customer_id, name, country, last_active,
       ROUND(julianday('now') - julianday(last_active)) AS days_inactive
FROM customers
WHERE ROUND(julianday('now') - julianday(last_active)) > 365
ORDER BY days_inactive DESC;
"""
inactive = pd.read_sql_query(inactive_query, conn)
inactive.to_csv('../data/processed/inactive_customers.csv', index=False)
print("\nInactive customers (top 5):\n", inactive.head())

# --- 4. Cohort Analysis by Signup Month & Country ---
cohort_query = """
SELECT strftime('%Y-%m', signup_date) AS signup_month,
       country,
       COUNT(*) AS total_customers
FROM customers
GROUP BY signup_month, country
ORDER BY signup_month, country;
"""
cohort = pd.read_sql_query(cohort_query, conn)
cohort.to_csv('../data/processed/cohort_analysis.csv', index=False)
print("\nCohort analysis (top 5 rows):\n", cohort.head())

# --- 5. Recency Ranking using Window Function ---
window_query = """
SELECT customer_id, name, country, last_active,
       RANK() OVER(PARTITION BY country ORDER BY last_active DESC) AS rank_recent
FROM customers;
"""
recency_rank = pd.read_sql_query(window_query, conn)
recency_rank.to_csv('../data/processed/recency_ranking.csv', index=False)
print("\nRecency ranking (top 5 rows):\n", recency_rank.head())

# --- 6. Visualizations ---
sns.set(style="whitegrid")

# Missing values bar chart
plt.figure(figsize=(6,4))
sns.barplot(x=missing_pct.columns, y=missing_pct.iloc[0].values)
plt.ylabel('% Missing')
plt.title('Missing Values Percentage')
plt.savefig('../outputs/dashboard_plots/missing_values_pct.png')
plt.close()

# Duplicate emails frequency plot
plt.figure(figsize=(6,4))
sns.histplot(duplicates['freq'], bins=range(2, duplicates['freq'].max()+2), discrete=True)
plt.title('Duplicate Email Frequencies')
plt.xlabel('Frequency')
plt.ylabel('Number of Emails')
plt.savefig('../outputs/dashboard_plots/duplicate_email_freq.png')
plt.close()

# Average inactivity by country
inactive_avg = inactive.groupby('country')['days_inactive'].mean().reset_index()
plt.figure(figsize=(6,4))
sns.barplot(x='country', y='days_inactive', data=inactive_avg)
plt.title('Average Days Inactive by Country')
plt.ylabel('Days')
plt.savefig('../outputs/dashboard_plots/avg_days_inactive.png')
plt.close()

print("\nAdvanced SQL profiling and visualizations complete! Outputs saved in data/processed and outputs/dashboard_plots.")

# Close connection
conn.close()
