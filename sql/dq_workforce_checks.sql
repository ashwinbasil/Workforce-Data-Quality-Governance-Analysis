-- ============================================
-- Data Quality Failure Store (Row-Level)
-- ============================================
DROP TABLE IF EXISTS dq_failures;

CREATE TABLE dq_failures (
    check_name TEXT,
    record_id INTEGER
);

-- ============================================
-- COMPLETENESS CHECKS
-- ============================================

-- Missing Parent Department
INSERT INTO dq_failures (check_name, record_id)
SELECT
    'missing_parent_department',
    rowid
FROM workforce
WHERE "Parent Department" IS NULL
   OR TRIM("Parent Department") = '';

-- Missing Organisation
INSERT INTO dq_failures (check_name, record_id)
SELECT
    'missing_organisation',
    rowid
FROM workforce
WHERE "Organisation" IS NULL
   OR TRIM("Organisation") = '';

-- Missing Grade
INSERT INTO dq_failures (check_name, record_id)
SELECT
    'missing_grade',
    rowid
FROM workforce
WHERE "Grade" IS NULL
   OR TRIM("Grade") = '';

-- Missing Job Title
INSERT INTO dq_failures (check_name, record_id)
SELECT
    'missing_job_title',
    rowid
FROM workforce
WHERE "Generic Job Title" IS NULL
   OR TRIM("Generic Job Title") = '';

-- Missing Office Region
INSERT INTO dq_failures (check_name, record_id)
SELECT
    'missing_office_region',
    rowid
FROM workforce
WHERE "Office Region" IS NULL
   OR TRIM("Office Region") = '';

-- ============================================
-- NUMERICAL VALIDITY CHECKS
-- ============================================

-- Negative FTE values break headcount calculations
INSERT INTO dq_failures (check_name, record_id)
SELECT
    'invalid_fte_negative',
    rowid
FROM workforce
WHERE "Number of Posts in FTE" < 0;

-- Unrealistic FTE values (likely data entry error)
INSERT INTO dq_failures (check_name, record_id)
SELECT
    'invalid_fte_unrealistic',
    rowid
FROM workforce
WHERE "Number of Posts in FTE" > 5;

-- Payscale minimum greater than maximum is invalid compensation data
INSERT INTO dq_failures (check_name, record_id)
SELECT
    'payscale_min_greater_than_max',
    rowid
FROM workforce
WHERE "Payscale Minimum (£)" IS NOT NULL
  AND "Payscale Maximum (£)" IS NOT NULL
  AND "Payscale Minimum (£)" > "Payscale Maximum (£)";

-- ============================================
-- BUSINESS RULE CHECKS
-- ============================================

-- Senior roles with unusually low pay bands distort workforce cost reporting
INSERT INTO dq_failures (check_name, record_id)
SELECT
    'senior_role_low_pay',
    rowid
FROM workforce
WHERE (
        LOWER("Generic Job Title") LIKE '%director%'
     OR LOWER("Generic Job Title") LIKE '%head%'
     OR LOWER("Generic Job Title") LIKE '%chief%'
)
AND "Payscale Maximum (£)" < 40000;

-- ============================================
-- CONSISTENCY CHECKS
-- ============================================

-- Professional group present but job title missing indicates partial ingestion
INSERT INTO dq_failures (check_name, record_id)
SELECT
    'professional_group_without_job_title',
    rowid
FROM workforce
WHERE "Professional/Occupational Group" IS NOT NULL
  AND TRIM("Professional/Occupational Group") <> ''
  AND (
        "Generic Job Title" IS NULL
     OR TRIM("Generic Job Title") = ''
  );

-- ============================================
-- END OF CHECKS
-- ============================================
