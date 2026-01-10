import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create outputs directory if it doesn't exist
os.makedirs("outputs", exist_ok=True)

# ----------------------------
# 1. Audit Log Snapshot
# ----------------------------
conn = sqlite3.connect("data/processed/customers.db")
audit_df = pd.read_sql_query("SELECT * FROM dq_audit_log", conn)
conn.close()

# Save a table snapshot as CSV
audit_df.to_csv("outputs/audit_log_snapshot.csv", index=False)

# Plot audit log snapshot as a horizontal bar chart (failed_rows)
plt.figure(figsize=(8, 5))
sns.barplot(x="failed_rows", y="check_name", data=audit_df, palette="viridis")
plt.title("Audit Log Snapshot - Failed Rows per Check")
plt.xlabel("Failed Rows")
plt.ylabel("Check Name")
plt.tight_layout()
plt.savefig("outputs/audit_log_snapshot.png")
plt.close()

# ----------------------------
# 2. SLA Violation Chart (% failed)
# ----------------------------
# Compute percentage failed per check
audit_df['total_rows'] = 5000  # assuming dataset has 5000 rows, adjust if different
audit_df['pct_failed'] = audit_df['failed_rows'] / audit_df['total_rows'] * 100

plt.figure(figsize=(8, 5))
sns.barplot(x="pct_failed", y="check_name", data=audit_df, palette="magma")
plt.title("SLA Violation Chart (% Failed per Check)")
plt.xlabel("% Failed")
plt.ylabel("Check Name")
plt.tight_layout()
plt.savefig("outputs/sla_bar_chart.png")
plt.close()

# ----------------------------
# 3. Historical Trend
# ----------------------------
hist_df = pd.read_csv("data/processed/dq_audit_log_historical.csv", parse_dates=["check_timestamp"])

# Compute % failed
hist_df['pct_failed'] = hist_df['failed_rows'] / 5000 * 100  # adjust total_rows as needed

plt.figure(figsize=(10, 6))
for check in hist_df["check_name"].unique():
    df_check = hist_df[hist_df["check_name"] == check]
    plt.plot(df_check["check_timestamp"], df_check["pct_failed"], marker='o', label=check)

plt.title("Historical SLA Trends")
plt.xlabel("Timestamp")
plt.ylabel("% Failed")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("outputs/historical_trend.png")
plt.close()

# ----------------------------
# 4. Streamlit Dashboard (Interactive)
# ----------------------------
# Optional: generate screenshot-ready static view
# Save minimal HTML for portfolio (just a table + chart) without running full Streamlit

html_content = f"""
<html>
<head><title>Customer Data Quality Dashboard</title></head>
<body>
<h2>Audit Log Snapshot</h2>
<img src="audit_log_snapshot.png" width="600"><br>
<h2>SLA Violation Chart</h2>
<img src="sla_bar_chart.png" width="600"><br>
<h2>Historical Trend</h2>
<img src="historical_trend.png" width="600"><br>
</body>
</html>
"""

with open("outputs/dashboard_portfolio.html", "w") as f:
    f.write(html_content)

print("Portfolio PNGs and dashboard HTML generated in outputs/")
