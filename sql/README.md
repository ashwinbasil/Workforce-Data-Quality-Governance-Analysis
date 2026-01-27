# Data Quality SQL Rules

This directory contains all **production-style SQL logic** used to enforce data quality
and governance rules on the workforce dataset.

These are not exploratory queries. Each rule:
- Encodes a business expectation
- Produces a measurable outcome
- Feeds automated audit logs and SLA evaluation

---

## dq_workforce_checks.sql

Implements deterministic data quality rules including:
- Missing organisational hierarchy fields
- Invalid or unrealistic FTE values
- Inconsistent pay ranges
- Senior roles mapped to implausible pay bands

Each rule outputs:
- check_name
- failed_rows
- execution timestamp

---

## dq_sla_rules.sql

Defines Service Level Agreement (SLA) thresholds per rule.

Purpose:
- Convert raw data errors into governance signals
- Classify checks as PASS or FAIL by severity
- Enable trend monitoring over time

---

## exploratory_analysis.sql

Contains analyst-style investigation queries used to:
- Trace failures back to departments or grades
- Identify systemic vs isolated issues
- Support root-cause analysis before remediation

This separation mirrors real-world analytics and governance workflows.
