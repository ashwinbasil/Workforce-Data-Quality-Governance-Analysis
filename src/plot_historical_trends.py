import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/dq_audit_log_historical.csv", parse_dates=["check_timestamp"])

# Plot pct_failed over time for each rule
for check in df["check_name"].unique():
    df_check = df[df["check_name"] == check]
    plt.plot(df_check["check_timestamp"], df_check["pct_failed"], label=check)

plt.axhline(0.05, color='red', linestyle='--', label='SLA Threshold (5%)')
plt.legend()
plt.xticks(rotation=45)
plt.ylabel("Pct Failed")
plt.title("Data Quality Trend Over Time")
plt.tight_layout()
plt.show()
