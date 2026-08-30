-- Data Quality Failure Store (Row-Level)
-- Column names below match the ACTUAL schema in workforce.db:
-- parent_department, organisation, unit, reporting_senior_post, grade,
-- payscale_minimum, payscale_maximum, generic_job_title, fte_posts,
-- "professional/occupational_group", office_region
-- ============================================
DROP TABLE IF EXISTS dq_failures;
CREATE TABLE dq_failures (
    check_name TEXT,
    record_id INTEGER
);

-- ============================================
-- COMPLETENESS CHECKS
-- ============================================

INSERT INTO dq_failures (check_name, record_id)
SELECT 'missing_parent_department', rowid
FROM workforce
WHERE parent_department IS NULL OR TRIM(parent_department) = '';

INSERT INTO dq_failures (check_name, record_id)
SELECT 'missing_organisation', rowid
FROM workforce
WHERE organisation IS NULL OR TRIM(organisation) = '';

INSERT INTO dq_failures (check_name, record_id)
SELECT 'missing_grade', rowid
FROM workforce
WHERE grade IS NULL OR TRIM(grade) = '';

INSERT INTO dq_failures (check_name, record_id)
SELECT 'missing_job_title', rowid
FROM workforce
WHERE generic_job_title IS NULL OR TRIM(generic_job_title) = '';

INSERT INTO dq_failures (check_name, record_id)
SELECT 'missing_office_region', rowid
FROM workforce
WHERE office_region IS NULL OR TRIM(office_region) = '';

-- ============================================
-- NUMERICAL VALIDITY CHECKS
-- ============================================

-- Negative post counts are always invalid
INSERT INTO dq_failures (check_name, record_id)
SELECT 'invalid_fte_negative', rowid
FROM workforce
WHERE fte_posts < 0;

-- fte_posts is a row-level aggregate post count (grouped by
-- Department/Organisation/Grade/Job Title), not a single employee's
-- FTE fraction. Verified range: 0.4 to 57.96, mean 2.37. A fixed
-- cap like ">1.5" or ">5" is the wrong shape of rule for this grain
-- and previously flagged up to 48.7% of rows as "invalid" when they
-- were not. Flag statistical outliers within each Grade instead,
-- since post counts vary legitimately by role seniority and team size.
INSERT INTO dq_failures (check_name, record_id)
SELECT 'invalid_fte_outlier_by_grade', rowid
FROM (
    SELECT
        rowid,
        fte_posts,
        grade_avg,
        (
            SELECT
                CASE WHEN COUNT(*) > 1 THEN
                    SQRT(SUM((w2.fte_posts - w1.grade_avg) * (w2.fte_posts - w1.grade_avg)) / (COUNT(*) - 1))
                ELSE NULL END
            FROM workforce w2
            WHERE w2.grade = w1.grade
        ) AS grade_stdev
    FROM (
        SELECT rowid, fte_posts, grade, AVG(fte_posts) OVER (PARTITION BY grade) AS grade_avg
        FROM workforce
    ) w1
) scored
WHERE grade_stdev IS NOT NULL AND grade_stdev > 0
  AND ABS(fte_posts - grade_avg) / grade_stdev > 3;
-- NOTE: correlated subquery is O(n^2). Fine at ~3k rows. Precompute
-- grade-level stats into a temp table before this scales further.

-- Payscale minimum greater than maximum.
-- Verified against the real schema: 0 failures in the current dataset.
-- The ~100% figure previously reported was a SQLite quoting bug
-- (unmatched double-quoted identifiers silently fell back to string
-- literals instead of erroring), not a real finding. Keeping this
-- check in place for future data refreshes, since it's a legitimate
-- thing to monitor even though it currently passes clean.
INSERT INTO dq_failures (check_name, record_id)
SELECT 'payscale_min_greater_than_max', rowid
FROM workforce
WHERE payscale_minimum IS NOT NULL
  AND payscale_maximum IS NOT NULL
  AND payscale_minimum > payscale_maximum;

-- ============================================
-- BUSINESS RULE CHECKS
-- ============================================

-- Senior roles with unusually low pay bands distort workforce cost
-- reporting. Verified: 24 rows in the current dataset, the strongest
-- genuine finding in this file.
INSERT INTO dq_failures (check_name, record_id)
SELECT 'senior_role_low_pay', rowid
FROM workforce
WHERE (
        LOWER(generic_job_title) LIKE '%director%'
     OR LOWER(generic_job_title) LIKE '%head%'
     OR LOWER(generic_job_title) LIKE '%chief%'
)
AND payscale_maximum < 40000;

-- Payscale values present but NULL (dq_sla_rules already had an SLA
-- entry for this check name, but no check ever populated it -- it
-- was a dead rule that silently vanished from SLA output via the
-- INNER JOIN in run_workforce_dq.py). Verified: 0 nulls currently.
INSERT INTO dq_failures (check_name, record_id)
SELECT 'missing_payscale', rowid
FROM workforce
WHERE payscale_minimum IS NULL OR payscale_maximum IS NULL;

-- ============================================
-- CONSISTENCY CHECKS
-- ============================================

INSERT INTO dq_failures (check_name, record_id)
SELECT 'professional_group_without_job_title', rowid
FROM workforce
WHERE "professional/occupational_group" IS NOT NULL
  AND TRIM("professional/occupational_group") <> ''
  AND (generic_job_title IS NULL OR TRIM(generic_job_title) = '');

-- Region values that differ only in case (e.g. "East Of England" vs
-- "East of England") fragment any regional rollup or Power BI slicer
-- into duplicate categories. Verified: 33 rows across 2 casing
-- variants of the same region in the current dataset.
INSERT INTO dq_failures (check_name, record_id)
SELECT 'inconsistent_region_casing', rowid
FROM workforce
WHERE LOWER(TRIM(office_region)) IN (
    SELECT LOWER(TRIM(office_region))
    FROM workforce
    WHERE office_region IS NOT NULL AND TRIM(office_region) <> ''
    GROUP BY LOWER(TRIM(office_region))
    HAVING COUNT(DISTINCT office_region) > 1
);

-- "Unknown" is a placeholder value, not a genuine region, and is
-- invisible to missing_office_region (which only catches NULL/blank).
-- Verified: 119 rows (3.7%) in the current dataset.
INSERT INTO dq_failures (check_name, record_id)
SELECT 'placeholder_office_region', rowid
FROM workforce
WHERE LOWER(TRIM(office_region)) = 'unknown';

-- ============================================
-- END OF CHECKS
-- ============================================
