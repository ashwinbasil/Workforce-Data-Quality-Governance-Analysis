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

-- Negative FTE values are always invalid regardless of row grain
INSERT INTO dq_failures (check_name, record_id)
SELECT
    'invalid_fte_negative',
    rowid
FROM workforce
WHERE "Number of Posts in FTE" < 0;

-- "Number of Posts in FTE" is a row-level aggregate (posts per
-- Department/Organisation/Grade/Job Title grouping), NOT a single
-- employee's FTE fraction. A fixed threshold like ">1.5" or ">5"
-- is wrong for this grain and previously flagged ~100% of rows.
-- Instead, flag statistical outliers relative to other rows sharing
-- the same Grade, using a z-score over a window. This adapts to
-- whatever the real distribution looks like instead of assuming a
-- per-person cap that doesn't apply to aggregated data.
INSERT INTO dq_failures (check_name, record_id)
SELECT rowid, 'invalid_fte_outlier_by_grade' AS check_name
FROM (
    SELECT
        rowid,
        "Number of Posts in FTE" AS fte,
        AVG("Number of Posts in FTE") OVER (PARTITION BY "Grade") AS grade_avg,
        -- sample stdev via window; guard divide-by-zero with NULLIF
        (
            SELECT
                CASE
                    WHEN COUNT(*) > 1 THEN
                        SQRT(SUM((w2."Number of Posts in FTE" - w1.grade_avg) * (w2."Number of Posts in FTE" - w1.grade_avg)) / (COUNT(*) - 1))
                    ELSE NULL
                END
            FROM workforce w2
            WHERE w2."Grade" = w1."Grade"
        ) AS grade_stdev
    FROM workforce w1
) scored
WHERE grade_stdev IS NOT NULL
  AND grade_stdev > 0
  AND ABS(fte - grade_avg) / grade_stdev > 3;

-- NOTE ON THE QUERY ABOVE: the correlated subquery recomputing
-- grade_stdev per row is O(n^2) and fine for a few thousand rows
-- (this dataset), but will not scale to a large table. If this
-- table grows, precompute grade-level stats into a temp table and
-- join instead of correlating per row.

-- Payscale minimum greater than maximum is invalid compensation data
-- IMPORTANT: if this check still flags close to 100% of rows after
-- the FTE fix above, the columns are almost certainly swapped at
-- ingestion (source CSV header order vs DB column mapping), not a
-- genuine finding. Run the diagnostic query below FIRST and read
-- the actual values before trusting this check's output:
--
--   SELECT "Payscale Minimum (£)", "Payscale Maximum (£)"
--   FROM workforce LIMIT 20;
--
-- If "minimum" is consistently larger than "maximum" on believable,
-- non-null, non-zero numbers, fix the column mapping in your
-- ingestion script rather than reporting this as a workforce
-- governance failure.
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
