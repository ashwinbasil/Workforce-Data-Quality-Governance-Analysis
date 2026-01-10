# Data Contract: Customer Master Dataset

## 1. Purpose

This data contract defines the structure, quality expectations, and governance rules
for the **Customer Master Dataset** used for analytics, reporting, and downstream
business intelligence.

The goal of this contract is to ensure:
- Consistent schema usage
- Explicit data quality guarantees
- Clear ownership and accountability
- Predictable behavior for downstream consumers

This dataset is designed for analytical use, not transactional workloads.

---

## 2. Dataset Overview

**Dataset Name:** customers  
**Storage Format:** CSV (raw), SQLite (analytical layer)  
**Update Frequency:** Batch-generated (synthetic for this project)  
**Primary Use Cases:**
- Customer analytics
- Retention and inactivity analysis
- Data quality monitoring demonstrations
- SQL analytics and governance exercises

---

## 3. Ownership and Responsibility

| Role | Responsibility |
|----|----|
| Data Producer | Generates raw customer data |
| Data Owner | Defines business meaning and quality expectations |
| Data Consumer | Analysts, dashboards, reporting systems |
| Data Steward | Monitors quality metrics and contract compliance |

In this project, all roles are simulated by the same system for demonstration purposes.

---

## 4. Schema Definition

### Table: customers

| Column Name | Data Type | Nullable | Description |
|-----------|---------|----------|------------|
| customer_id | INTEGER | NO | Unique customer identifier |
| name | TEXT | NO | Full customer name |
| email | TEXT | YES | Customer email address |
| phone_number | TEXT | YES | Customer phone number |
| signup_date | DATE | NO | Date customer registered |
| country | TEXT | NO | Country of residence |
| last_active | DATE | NO | Most recent customer activity date |

---

## 5. Primary Key and Uniqueness

- **Primary Key:** `customer_id`
- **Uniqueness Constraint:**  
  - `customer_id` must be unique
  - `email` should be unique when present

Duplicate emails are allowed temporarily but flagged as a data quality violation.

---

## 6. Data Quality Expectations

### 6.1 Completeness Rules

| Column | Rule |
|-----|-----|
| customer_id | Must not be NULL |
| name | Must not be NULL |
| signup_date | Must not be NULL |
| country | Must not be NULL |
| last_active | Must not be NULL |
| email | Nullable, but missing values are tracked |
| phone_number | Nullable, but missing values are tracked |

---

### 6.2 Validity Rules

- Email addresses must contain `@` and `.` characters
- Dates must be valid calendar dates
- `country` must be one of:
  - USA
  - UK
  - Canada
  - Germany
  - India

---

### 6.3 Temporal Consistency Rules

- `last_active` must be greater than or equal to `signup_date`
- No future dates beyond the data generation date

---

### 6.4 Freshness Expectations

- Data reflects customer activity within the last 3 years
- Customers inactive for more than 2 years are classified as inactive but not invalid

---

## 7. Data Quality Monitoring Metrics

The following metrics are tracked for governance:

- Percentage of missing emails
- Percentage of missing phone numbers
- Count of duplicate email addresses
- Count of invalid email formats
- Count of temporal violations (last_active < signup_date)
- Average inactivity duration by country

These metrics are recalculated on every dataset refresh.

---

## 8. Contract Enforcement

This contract is enforced via:
- SQL-based data quality checks
- Automated profiling scripts
- Audit logging of rule violations

Violations do not block ingestion but are recorded for visibility and analysis.

---

## 9. Known Limitations

- Dataset is synthetic and generated for educational purposes
- No real-time enforcement
- No SLA-based alerting
- Single-table scope

These limitations are intentional to keep focus on governance principles.

---

## 10. Change Management

Any change to:
- Schema
- Column definitions
- Quality rules

must be documented and versioned in this file.

Downstream consumers are expected to review changes before relying on updated data.

---

## 11. Disclaimer

This dataset and contract are designed for learning and demonstration purposes only.
They do not represent real customer data and should not be used for production systems.
