import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Customer Data Quality Dashboard", layout="wide")
st.title("Customer Data Quality Dashboard")

# Load processed CSVs
missing = pd.read_csv('../data/processed/missing_values_pct.csv')
duplicates = pd.read_csv('../data/processed/duplicate_emails.csv')
inactive = pd.read_csv('../data/processed/inactive_customers.csv')
cohort = pd.read_csv('../data/processed/cohort_analysis.csv')

# --- Missing Values ---
st.header("Missing Values")
st.dataframe(missing)
fig, ax = plt.subplots()
sns.barplot(x=missing.columns, y=missing.iloc[0].values, ax=ax)
ax.set_ylabel('% Missing')
st.pyplot(fig)

# --- Duplicate Emails ---
st.header("Duplicate Emails (Top 10)")
st.dataframe(duplicates.head(10))

# --- Inactive Customers ---
st.header("Inactive Customers (>1 year)")
st.dataframe(inactive.head(10))

# --- Cohort Analysis ---
st.header("Cohort Analysis by Signup Month and Country")
st.dataframe(cohort.head(20))

st.success("Dashboard loaded successfully!")
