import pandas as pd

# Load SLA evaluation results
df = pd.read_csv("data/processed/dq_sla_evaluation.csv")

# Keep latest run per check
latest = (
    df.sort_values("check_timestamp")
      .groupby("check_name", as_index=False)
      .tail(1)
)

# Save for README + BI usage
latest.to_csv(
    "data/processed/dq_latest_findings.csv",
    index=False
)

print("Latest findings exported:")
print(latest[["check_name", "failed_rows", "sla_status"]])
