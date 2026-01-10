import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3

st.set_page_config(page_title="Customer Data Governance Dashboard", layout="wide")
st.title("Customer Data Governance Dashboard")

# ----------------------------
# --- Phase 2 Audit Log ------
# ----------------------------
DB_PATH = "data/processed/customers.db"
conn = sqlite3.connect(DB_PATH)
audit_df = pd.read_sql_query("SELECT * FROM dq_audit_log ORDER BY check_timestamp DESC", conn)
conn.close()

# Define thresholds (SLA)
DQ_THRESHOLDS = {
    "missing_email": 0.05,
    "missing_phone": 0.1,
    "duplicate_email": 0,
    "invalid_email_format": 0,
    "last_active_before_signup": 0
}

# Convert failed_rows to percentages
total_customers = 5000  # adjust to your synthetic dataset size
audit_df["pct_failed"] = audit_df["failed_rows"] / total_customers
audit_df["sla_status"] = audit_df.apply(
    lambda row: "PASS" if row["pct_failed"] <= DQ_THRESHOLDS.get(row["check_name"], 0) else "FAIL",
    axis=1
)

st.header("Data Quality Audit Log")
st.dataframe(audit_df)

st.header("SLA Violations")
violations = audit_df[audit_df["sla_status"] == "FAIL"]
st.dataframe(violations)

# Plot failed percentage by rule
st.header("Failed Rows % by Rule")
fig, ax = plt.subplots(figsize=(8,4))
sns.barplot(x="check_name", y="pct_failed", data=audit_df, palette="Set2", ax=ax)
for i, row in audit_df.iterrows():
    ax.text(i, row["pct_failed"] + 0.005, f"{row['pct_failed']*100:.1f}%", ha='center')
ax.axhline(y=0.05, color='red', linestyle='--', label='SLA Threshold (5%)')
ax.set_ylabel("Failed %")
ax.set_xlabel("Rule")
ax.set_title("Data Quality SLA Dashboard")
ax.legend()
st.pyplot(fig)

# ----------------------------
# --- Phase 1 CSV-based metrics (existing dashboard) ---
# ----------------------------
missing = pd.read_csv('../data/processed/missing_values_pct.csv')
duplicates = pd.read_csv('../data/processed/duplicate_emails.csv')
inactive = pd.read_csv('../data/processed/inactive_customers.csv')
cohort = pd.read_csv('../data/processed/cohort_analysis.csv')
recency_rank = pd.read_csv('../data/processed/recency_ranking.csv')

# --- Sidebar Filters ---
st.sidebar.header("Filters")
country_filter = st.sidebar.multiselect(
    "Select Country",
    options=inactive['country'].unique(),
    default=inactive['country'].unique()
)

days_inactive_filter = st.sidebar.slider(
    "Minimum Days Inactive",
    min_value=int(inactive['days_inactive'].min()),
    max_value=int(inactive['days_inactive'].max()),
    value=int(inactive['days_inactive'].min())
)

# Apply filters
inactive_filtered = inactive[
    (inactive['country'].isin(country_filter)) &
    (inactive['days_inactive'] >= days_inactive_filter)
]
cohort_filtered = cohort[cohort['country'].isin(country_filter)]
recency_filtered = recency_rank[recency_rank['country'].isin(country_filter)]

# --- Missing Values Section ---
st.header("Missing Values")
st.dataframe(missing)
fig_mv, ax_mv = plt.subplots()
sns.barplot(x=missing.columns, y=missing.iloc[0].values, ax=ax_mv)
ax_mv.set_ylabel('% Missing')
st.pyplot(fig_mv)

# --- Duplicate Emails Section ---
st.header("Duplicate Emails")
st.dataframe(duplicates.head(20))
fig_dup, ax_dup = plt.subplots()
sns.histplot(duplicates['freq'], bins=range(2, duplicates['freq'].max()+2), ax=ax_dup)
ax_dup.set_xlabel('Frequency')
ax_dup.set_ylabel('Number of Emails')
ax_dup.set_title('Duplicate Email Frequencies')
st.pyplot(fig_dup)

# --- Inactive Customers Section ---
st.header("Inactive Customers")
st.dataframe(inactive_filtered.sort_values(by='days_inactive', ascending=False).reset_index(drop=True))

fig_inact, ax_inact = plt.subplots()
avg_inactive = inactive_filtered.groupby('country')['days_inactive'].mean().reset_index()
sns.barplot(x='country', y='days_inactive', data=avg_inactive, ax=ax_inact)
ax_inact.set_ylabel('Average Days Inactive')
ax_inact.set_title('Average Days Inactive by Country')
st.pyplot(fig_inact)

# --- Cohort Analysis Section ---
st.header("Cohort Analysis by Signup Month")
cohort_pivot = cohort_filtered.pivot(index='signup_month', columns='country', values='total_customers').fillna(0)
st.line_chart(cohort_pivot)

# --- Recency Ranking Section ---
st.header("Recency Ranking by Country")
st.dataframe(recency_filtered.sort_values(['country','rank_recent']).reset_index(drop=True))

st.success("Dashboard loaded successfully! Use the sidebar filters and scroll to see governance SLAs.")

# Historical view
hist_df = pd.read_csv("data/processed/dq_audit_log_historical.csv", parse_dates=["check_timestamp"])
st.subheader("Historical SLA Trends")
for check in hist_df["check_name"].unique():
    df_check = hist_df[hist_df["check_name"] == check]
    st.line_chart(df_check.set_index("check_timestamp")["pct_failed"])
