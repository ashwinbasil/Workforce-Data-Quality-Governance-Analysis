# Customer Data Quality & Governance Project

A full-stack, portfolio-ready project demonstrating **data governance, SQL analytics, Python automation, BI integration, and historical monitoring** on a synthetic customer dataset.  

This project is designed for **data analyst, data engineer, or BI-focused roles** to showcase advanced SQL, Python, and dashboarding skills.

---

## Project Overview

The project is organized into **4 phases**:

1. **Data Governance Foundations**  
   - Defined in [data_contract.md](src/data_contract.md)  
   - Establishes rules, standards, and assumptions for customer data quality.  

2. **Automated Data Quality Checks (SQL + Python)**  
   - Missing values, duplicate detection, invalid formats, temporal consistency  
   - Audit logs stored in `dq_audit_log`  

3. **Interactive Governance Dashboard (Streamlit)**  
   - Visualizes SLA violations, failed percentages, and audit summaries  
   - Optional filtering by country or rule  

4. **Historical Logging & BI Integration**  
   - Maintains historical data quality results in `dq_audit_log_historical`  
   - Exports CSV for Power BI / Tableau  
   - Supports trend visualization and SLA compliance over time  

---

## Tech Stack

- **SQL**: Advanced queries for governance and quality checks  
- **Python**: Automation, logging, CSV exports, plotting  
- **Streamlit**: Interactive dashboard  
- **Matplotlib / Seaborn**: Visualizations  
- **SQLite**: Lightweight relational database for logs  
- **BI Tools**: Power BI / Tableau (via CSV export)  

---

## Repository Structure

```text
customer-data-quality/
├── data/
│   ├── raw/                 # Generated synthetic datasets
│   └── processed/           # Cleaned datasets & CSV outputs
├── outputs/                 # Plots and screenshots for portfolio
├── src/
│   ├── generate_data.py     # Phase 0: Synthetic dataset generator
│   ├── check_data.py        # Quick checks & missing value exploration
│   ├── sql_profiling.py     # Advanced SQL profiling
│   ├── advanced_sql_dashboard.py  # Phase 3 alternative dashboard
│   ├── dashboard_interactive.py   # Phase 3 Streamlit dashboard
│   ├── dq_thresholds.py     # SLA thresholds
│   ├── create_audit_table.sql
│   ├── create_historical_audit_table.sql
│   ├── data_quality_checks.sql
│   ├── run_data_quality_checks.py
│   ├── run_data_quality_historical.py
│   └── data_contract.md     # Phase 1 governance document
├── main.py                  # Orchestrates all phases
├── requirements.txt
└── README.md
```
---

## Getting Started

- Install Dependencies 

    pip install -r requirements.txt

- Ensure Streamlit is installed

   pip install streamlit

- Run the pipeline
   
   python main.py

This executes:

- Data generation

- Data quality checks

- Historical logging & CSV export

Outputs:

- Audit logs: dq_audit_log, dq_audit_log_historical

- CSV for BI: data/processed/dq_audit_log_historical.csv

- Plots: outputs/

Launch Interactive Dashboard (Phase 3)
  
  streamlit run src/dashboard_interactive.py

View SLA violations and failed percentages

Optional: filter by rule or country

Historical trends can be displayed from dq_audit_log_historical.csv

---

## Sample Output

### Audit Log Snapshot
![Audit Log](outputs/audit_log_snapshot.png)

### SLA Violation Chart
![SLA Chart](outputs/sla_bar_chart.png)

### Historical Trend
![Trend Plot](outputs/historical_trend.png)

### Streamlit Dashboard
![Dashboard](outputs/dashboard_portfolio.html)

---

## Project Highlights

**Advanced SQL**: Multiple checks, duplicates, temporal consistency, percentage calculations

**Python Automation**: End-to-end pipeline orchestrated via main.py

**Data Governance**: Formal data contract, SLA enforcement, traceable audit logs

**BI-Ready Outputs**: Historical CSV for Power BI / Tableau dashboards

**Portfolio**-Ready: Screenshots, clean repo, reproducible steps

---

## Limitations

- Synthetic dataset only

- Single-table analysis (customers)

- No real-time streaming data

- SLA thresholds are configurable but simplistic

This project is meant for educational and portfolio purposes.


