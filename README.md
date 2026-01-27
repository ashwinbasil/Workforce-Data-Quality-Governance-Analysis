# Workforce Data Quality & Governance Analysis
UK Government Workforce Dataset

## Overview

This project demonstrates an end-to-end data quality and governance workflow using a real UK government workforce dataset.

The objective is not predictive modelling or dashboard aesthetics. The focus is on how a data analyst or analytics engineer designs enforceable data quality rules, detects violations using SQL, tracks them over time, evaluates them against SLAs, and translates findings into concrete governance actions.

All SQL and Python code in this repository is public, versioned, and fully reproducible.

---

## Dataset

Source: UK Government workforce transparency data (public)
Rows: ~3,000
Domain: Public-sector workforce reporting

Common data quality risks in the dataset include:
- Missing organisational hierarchy
- Implausible Full-Time Equivalent (FTE) values
- Invalid pay ranges
- Structural inconsistencies across grades and roles

Key fields:
- Parent Department
- Organisation
- Grade
- Generic Job Title
- Payscale Minimum (£)
- Payscale Maximum (£)
- Full-Time Equivalent (FTE)
- Office Region

---

## Repository Structure (All Code Public)

```text
Workforce-Data-Quality-Governance-Analysis/
│
├── contracts/
│ └── workforce_data_contract.md
│
├── sql/
│ ├── dq_workforce_checks.sql
│ └── dq_sla_rules.sql
│
├── src/
│ ├── run_workforce_dq.py
│ └── generate_portfolio_outputs.py
│
├── data/
│ ├── raw/
│ └── processed/
│ ├── workforce.db
│ ├── dq_audit_log.csv
│ └── dq_sla_evaluation.csv
│
├── outputs/
│ ├── audit_log_snapshot.png
│ ├── sla_bar_chart.png
│ ├── historical_trend.png
│ └── dashboard_portfolio.html
│
└── README.md

```

---

## Data Governance Foundation

Before any validation is executed, a formal data contract defines the expected structure and semantics of the dataset.

File:
contracts/workforce_data_contract.md

The contract specifies:
- Mandatory fields
- Acceptable numeric ranges
- Semantic rules linking grade seniority to pay bands
- Ownership and governance assumptions

This mirrors how modern data teams enforce quality upstream rather than react downstream.

---

## End-to-End Walkthrough

### Problem

Government workforce data feeds:
- headcount reporting
- cost forecasting
- workforce planning
- public accountability and audit processes

Incorrect FTE values or invalid pay bands directly distort reported workforce size and cost, leading to inaccurate decision-making and potential compliance risk.

---

## Investigation

Data quality rules are implemented in SQL and executed against a SQLite database.

File:
sql/dq_workforce_checks.sql

Checks include:
- Missing organisational hierarchy fields
- Missing grades or job titles
- Negative or unrealistic FTE values
- Payscale minimum greater than maximum
- Senior roles mapped to implausibly low pay bands

Each rule writes results to a persistent audit table containing:
- check_name
- failed_rows
- check_timestamp

Failures are logged historically rather than overwritten, enabling trend analysis.

---

## Findings (Latest Run)

| Issue | Failed Rows | Why It Matters |
|-----|------------|----------------|
| Senior roles with low pay bands | 609 | Understates workforce cost and risks non-compliant compensation reporting |
| Unrealistic FTE values | 3,191 | Invalidates headcount metrics and workforce planning outputs |
| Payscale minimum greater than maximum | 3,191 | Corrupts payroll logic and compensation analysis |
| Missing grades | 0 | Controlled through upstream validation |
| Missing job titles | 0 | Controlled through upstream validation |
| Missing organisational fields | 0 | Controlled through upstream validation |

---

## Deep Dive: Unrealistic FTE Values

### Detection Logic

```sql
INSERT INTO dq_audit_log (check_name, failed_rows, check_timestamp)
SELECT
    'invalid_fte_unrealistic',
    COUNT(*),
    CURRENT_TIMESTAMP
FROM workforce
WHERE fte < 0 OR fte > 1.5;

```
---
Impact

Over 3,000 records violate realistic FTE constraints. If consumed by downstream BI tools, these records would:

- inflate reported headcount
- distort cost-per-employee metrics
- mislead workforce capacity planning

Root Cause Hypothesis

Likely causes include:
- data entry errors during aggregation
- inconsistent interpretation of FTE across departments
- lack of enforced validation at source systems

---

## SLA Evaluation

Each data quality rule is evaluated against predefined thresholds and severities.

File:
sql/dq_sla_rules.sql

Output:
data/processed/dq_sla_evaluation.csv

This converts raw failures into governance signals:
PASS or FAIL by severity, enabling prioritisation rather than alert fatigue.

---

## Resolution Strategy 

If deployed in a real organisation, remediation would include:

- Blocking ingestion of records with invalid FTE values

- Enforcing grade-to-pay-band constraints at source systems

- Requiring departmental data owner sign-off for overrides

- Creating exception workflows rather than silent acceptance

- Monitoring SLA breach trends to measure governance maturity over time

This shifts the organisation from reactive fixes to preventive controls.

---

##  Outputs & Evidence

Outputs & Evidence

All referenced outputs are generated by code in this repository.

- Audit log snapshot: outputs/audit_log_snapshot.png

- SLA violation chart: outputs/sla_bar_chart.png

- Historical trend analysis: outputs/historical_trend.png

- Interactive dashboard: outputs/dashboard_portfolio.html

---

## How to Run

pip install -r requirements.txt

python src/run_workforce_dq.py

python src/generate_portfolio_outputs.py

---

## Skills Demonstrated

- SQL-based data quality validation with business logic

- Data contracts and governance design

- Audit logging and SLA enforcement

- Analytical interpretation of public-sector data

- Python-based reporting and visualisation

- BI-ready, stakeholder-facing outputs

---

## Limitations

- SQLite used for simplicity

- Single dataset

- No CI/CD

- No automated remediation workflows


