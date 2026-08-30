import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create outputs directory if it doesn't exist
os.makedirs("outputs", exist_ok=True)

DB_PATH = "data/processed/workforce.db"

conn = sqlite3.connect(DB_PATH)

# ----------------------------
# Total row count, computed live, never hardcoded.
# The previous version of this file hardcoded total_rows = 5000 with
# a comment admitting it was a guess ("adjust if different"). Every
# percentage it ever produced was wrong because of that one line.
# ----------------------------
total_rows = pd.read_sql_query("SELECT COUNT(*) AS n FROM workforce", conn)["n"].iloc[0]

# ----------------------------
# 1. Audit Log Snapshot (most recent run only)
# ----------------------------
audit_df = pd.read_sql_query(
    """
    SELECT check_name, failed_rows, check_timestamp
    FROM dq_audit_log
    WHERE check_timestamp = (SELECT MAX(check_timestamp) FROM dq_audit_log)
    ORDER BY failed_rows DESC
    """,
    conn,
)

audit_df.to_csv("outputs/audit_log_snapshot.csv", index=False)

plt.figure(figsize=(8, 5))
sns.barplot(x="failed_rows", y="check_name", data=audit_df, palette="viridis")
plt.title(f"Audit Log Snapshot — Failed Rows per Check (n={total_rows})")
plt.xlabel("Failed Rows")
plt.ylabel("Check Name")
plt.tight_layout()
plt.savefig("outputs/audit_log_snapshot.png")
plt.close()

# ----------------------------
# 2. SLA Violation Chart (% failed, using the REAL total_rows)
# ----------------------------
audit_df["pct_failed"] = audit_df["failed_rows"] / total_rows * 100

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
# Reads directly from dq_audit_log (all runs, not a separate CSV that
# can drift out of sync with the live audit table). If you want to
# seed this with the pre-fix runs for a "before vs after" story, point
# this at data/processed/archive_pre_fix/ explicitly and merge, don't
# silently read a stale historical file that isn't documented anywhere.
# ----------------------------
hist_df = pd.read_sql_query(
    "SELECT check_name, failed_rows, check_timestamp FROM dq_audit_log ORDER BY check_timestamp",
    conn,
)
hist_df["check_timestamp"] = pd.to_datetime(hist_df["check_timestamp"], format="mixed", utc=True)
hist_df["pct_failed"] = hist_df["failed_rows"] / total_rows * 100

plt.figure(figsize=(10, 6))
for check in hist_df["check_name"].unique():
    df_check = hist_df[hist_df["check_name"] == check]
    plt.plot(df_check["check_timestamp"], df_check["pct_failed"], marker="o", label=check)
plt.title("Historical SLA Trends")
plt.xlabel("Timestamp")
plt.ylabel("% Failed")
plt.legend(fontsize=7)
plt.grid(True)
plt.tight_layout()
plt.savefig("outputs/historical_trend.png")
plt.close()

# ----------------------------
# 4. Static HTML dashboard for the portfolio
# ----------------------------
html_content = f"""
<html>
<head><title>Workforce Data Quality Dashboard</title></head>
<body>
<h2>Audit Log Snapshot ({total_rows} total records)</h2>
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

conn.close()
print(f"Portfolio PNGs and dashboard HTML generated in outputs/ (total_rows={total_rows})")
