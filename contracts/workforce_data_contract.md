# Workforce Data Contract
UK Government Spending – Workforce Dataset

## 1. Purpose
This dataset represents workforce and pay information for UK government departments and related organisations.
It is used for workforce analysis, pay band monitoring, headcount reporting, and data quality assessment.

This contract defines the minimum expectations for structure, validity, and quality of the data.

---

## 2. Data Source
- Publisher: UK Government Open Data
- Domain: Government Spending / Workforce
- Update Frequency: Periodic (as published by source)
- Format: CSV

---

## 3. Entity Definition
Each row represents an **organisational workforce record** describing job roles, pay scales, and staffing levels within a government entity.

---

## 4. Column Definitions and Rules

### Parent Department
- Description: Top-level government department
- Type: String
- Mandatory: Yes
- Rules:
  - Must not be NULL
  - Must be consistent for the same Organisation

---

### Organisation
- Description: Government body or agency
- Type: String
- Mandatory: Yes
- Rules:
  - Must not be NULL
  - Cannot contain only numeric values

---

### Unit
- Description: Sub-division within the organisation
- Type: String
- Mandatory: No
- Rules:
  - NULL allowed

---

### Reporting Senior Post
- Description: Senior role overseeing the unit
- Type: String
- Mandatory: No

---

### Grade
- Description: Civil service grade or equivalent
- Type: String
- Mandatory: Yes
- Rules:
  - Must follow recognised grade patterns where applicable

---

### Payscale Minimum (£)
- Description: Minimum salary for the grade
- Type: Numeric
- Mandatory: Yes
- Rules:
  - Must be >= 0
  - Must be less than or equal to Payscale Maximum

---

### Payscale Maximum (£)
- Description: Maximum salary for the grade
- Type: Numeric
- Mandatory: Yes
- Rules:
  - Must be >= Payscale Minimum

---

### Generic Job Title
- Description: Standardised job title
- Type: String
- Mandatory: Yes
- Rules:
  - Must not be NULL
  - Length must be greater than 3 characters

---

### Number of Posts in FTE
- Description: Full-time equivalent headcount
- Type: Numeric
- Mandatory: Yes
- Rules:
  - Must be >= 0
  - Decimal values allowed

---

### Professional / Occupational Group
- Description: Occupational classification
- Type: String
- Mandatory: Yes

---

### Office Region
- Description: Geographic region of employment
- Type: String
- Mandatory: Yes
- Rules:
  - Must match known UK regions where possible

---

## 5. Data Quality Expectations

| Dimension     | Expectation |
|--------------|-------------|
| Completeness | Mandatory fields must not be NULL |
| Validity     | Salary ranges must be logical |
| Consistency  | Same grades should have consistent pay bands within organisations |
| Accuracy     | FTE values must be realistic |
| Timeliness   | Data should reflect published reporting period |

---

## 6. Known Data Risks
- Inconsistent grade naming across departments
- Missing Unit values
- Encoding issues in currency symbols
- Regional naming inconsistencies

---

## 7. SLA Thresholds

| Check | Threshold |
|-----|----------|
| Missing mandatory fields | < 1% |
| Invalid pay ranges | 0 rows |
| Negative FTE values | 0 rows |

---

## 8. Change Management
Any structural change to this dataset (columns added, removed, renamed) requires:
- Contract update
- Backward compatibility assessment
- Data quality revalidation

---

## 9. Ownership
- Data Owner: UK Government Department
- Steward: Data Governance Function
- Consumer: Analysts, Policy Teams, Auditors

---

## 10. Approval
This contract is considered accepted when data quality checks align with the defined rules.

