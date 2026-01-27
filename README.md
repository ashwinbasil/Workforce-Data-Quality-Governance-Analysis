# Workforce Data Quality & Governance Analysis
**UK Government Workforce Dataset**

## Overview

This repository demonstrates a **SQL-first, end-to-end data quality and governance workflow** using a real UK government workforce dataset.

The objective is not predictive modelling or dashboard aesthetics.  
The focus is on how an analyst or analytics engineer:

- defines enforceable data expectations,
- detects violations using SQL,
- logs failures over time,
- evaluates them against SLAs,
- and translates findings into concrete governance actions.

All SQL and Python code is **public, versioned, and reproducible**.

---

## SQL-First Architecture (Deliberate Design Choice)

All data quality logic is implemented in **SQL**, not Python.

Python is used strictly to:
- orchestrate execution,
- load SLA thresholds,
- persist audit results,
- export BI-ready outputs.

This mirrors real enterprise environments where:
- data quality rules live close to the data,
- SQL logic is auditable and reviewable by governance teams,
- Python acts as a control layer, not a logic layer.

---

## SQL Techniques Demonstrated

The SQL in this repository goes beyond row-level checks and focuses on **analytical governance patterns**:

- Common Table Expressions (CTEs) for modular, auditable rules
- Conditional aggregation for failure metrics
- Cross-field validation (payscale minimum vs maximum)
- Semantic business rules (grade-to-pay alignment)
- Department-level concentration analysis
- Severity classification aligned to governance escalation
- Time-stamped audit logging for trend analysis

---

## Where to Review SQL Work

All data quality and governance logic lives in the `sql/` directory:

- `sql/dq_workforce_checks.sql`  
  Production-style data quality rules with persistent audit logging

- `sql/dq_sla_rules.sql`  
  SLA thresholds and severity mapping

- `sql/exploratory_analysis.sql`  
  Root-cause and impact analysis queries used to understand failure patterns

Python does **not** embed business logic.

---

## Dataset

**Source:** UK Government workforce transparency data (public)  
**Rows:** ~3,000  
**Domain:** Public-sector workforce reporting

Common data quality risks present in the dataset:
- Missing organisational hierarchy
- Implausible Full-Time Equivalent (FTE) values
- Invalid pay ranges
- Structural inconsistencies across grades and roles

Key fields include:
- Parent Department
- Organisation
- Grade
- Generic Job Title
- Payscale Minimum (£)
- Payscale Maximum (£)
- Full-Time Equivalent (FTE)
- Office Region

---

## Repository Structure

```text
Workforce-Data-Quality-Governance-Analysis/
│
├── contracts/
│   └── workforce_data_contract.md
│
├── sql/
│   ├── dq_workforce_checks.sql
│   ├── dq_sla_rules.sql
│   └── exploratory_analysis.sql
│
├── src/
│   ├── run_workforce_dq.py
│   └── generate_portfolio_outputs.py
│
├── data/
│   ├── raw/
│   └── processed/
│       ├── workforce.db
│       ├── dq_audit_log.csv
│       └── dq_sla_evaluation.csv
│
├── outputs/
│   ├── audit_log_snapshot.png
│   ├── sla_bar_chart.png
│   ├── historical_trend.png
│   └── dashboard_portfolio.html
│
├── requirements.txt
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

## Findings 

All findings below are automatically derived from the most recent data quality execution
(`data/processed/dq_latest_findings.csv`).

| Issue | Failed Rows | % of Dataset | SLA Status | Why It Matters |
|------|------------|-------------|------------|---------------|
| Senior roles with low pay bands | 609 | ~20% | FAIL | Understates workforce cost and risks non-compliant compensation for senior positions |
| Unrealistic FTE values | 3,191 | ~100% | FAIL | Breaks headcount calculations and invalidates workforce planning metrics |
| Payscale minimum greater than maximum | 3,191 | ~100% | FAIL | Produces invalid payroll records and corrupts compensation analysis |
| Missing grades | 0 | 0% | PASS | Controlled through validation rules |
| Missing job titles | 0 | 0% | PASS | Controlled through validation rules |
| Missing organisational fields | 0 | 0% | PASS | Controlled through validation rules |

---

## Impact Assessment 

The following issues were evaluated not only by volume, but by
their effect on reporting accuracy, compliance, and decision-making.

| Issue | Failed Rows | Impact Category | Governance Risk |
|-----|------------|----------------|----------------|
| Senior roles with low pay bands | 609 | Financial reporting | Understates senior workforce costs, misleading budget forecasts |
| Unrealistic FTE values | 3,191 | Headcount & planning | Invalidates workforce capacity and staffing metrics |
| Payscale min > max | 3,191 | Payroll integrity | Produces logically invalid compensation records |

---

### Priority Classification

Based on impact and downstream risk:

- **Critical**: Invalid FTE values, pay scale inversions  
  These break statutory reporting and financial controls.

- **High**: Senior role pay inconsistencies  
  These distort cost analysis and may indicate governance breaches.

- **Controlled**: Missing grades, job titles, organisational fields  
  These are currently mitigated by validation rules and did not breach SLAs.
---
## Recommended Remediation Actions

If deployed in a real organisation, the following actions would be taken:

### 1. Source-Level Controls
- Enforce FTE bounds (0 to 1.5) in source HR systems
- Block ingestion of records with inverted pay scales

### 2. Governance Controls
- Require department-level sign-off for senior role pay bands
- Assign data ownership for Parent Department and Organisation fields

### 3. Monitoring & Escalation
- Treat repeated SLA breaches as governance incidents
- Escalate unresolved failures to data governance council
- Track trends over time instead of one-off corrections

---
## Ownership Model

| Issue Type | Primary Owner | Secondary Owner |
|---------|---------------|----------------|
| FTE validity | HR Systems | Workforce Analytics |
| Pay scale integrity | Finance | Data Governance |
| Organisational hierarchy | Department Admin | Central Data Team |

This project treats data quality failures as governance decisions,
not technical inconveniences.

---

## Deep Dive: Unrealistic FTE Values

### Detection Logic


End-to-End Walkthrough: Unrealistic FTE Values

 Problem
FTE values are used directly for workforce headcount, budgeting, and capacity planning.
Values outside realistic bounds invalidate downstream metrics and policy decisions.

 Investigation
An automated SQL rule flagged FTE values less than 0 or greater than 1.5:

```sql
SELECT
    parent_department,
    COUNT(*) AS invalid_rows
FROM workforce
WHERE fte < 0 OR fte > 1.5
GROUP BY parent_department
ORDER BY invalid_rows DESC;
```

### Interpretation

Invalid FTE values are concentrated in a small number of departments,
suggesting upstream system or data entry issues rather than random noise.

Impact

If consumed by downstream BI tools, these records would:

inflate reported headcount,

distort cost-per-employee metrics,

mislead workforce capacity planning.

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


