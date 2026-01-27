-- Exploratory Analysis: Root Cause Investigation
-- These queries are used to understand WHY checks failed,
-- not just that they failed.

-- 1. Departments contributing most to invalid FTE values
SELECT
    parent_department,
    COUNT(*) AS invalid_fte_rows
FROM workforce
WHERE fte < 0 OR fte > 1.5
GROUP BY parent_department
ORDER BY invalid_fte_rows DESC;

-- 2. Senior roles with lowest maximum pay
SELECT
    grade,
    generic_job_title,
    payscale_min,
    payscale_max
FROM workforce
WHERE grade LIKE '%Senior%'
  AND payscale_max < 40000
ORDER BY payscale_max ASC;

-- 3. Pay scale inversions by organisation
SELECT
    organisation,
    COUNT(*) AS invalid_pay_rows
FROM workforce
WHERE payscale_min > payscale_max
GROUP BY organisation
ORDER BY invalid_pay_rows DESC;
