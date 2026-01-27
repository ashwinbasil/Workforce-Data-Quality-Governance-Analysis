-- Exploratory analysis of workforce data quality failures
-- This file supports root cause analysis and remediation prioritisation

-- 1. Departments driving unrealistic FTE values
WITH invalid_fte AS (
    SELECT
        parent_department,
        organisation,
        fte
    FROM workforce
    WHERE fte < 0 OR fte > 1.5
)
SELECT
    parent_department,
    COUNT(*) AS invalid_records,
    ROUND(
        100.0 * COUNT(*) / (SELECT COUNT(*) FROM workforce),
        2
    ) AS pct_of_total_workforce
FROM invalid_fte
GROUP BY parent_department
ORDER BY invalid_records DESC;

-- 2. Senior roles mapped to implausibly low pay bands
SELECT
    grade,
    generic_job_title,
    payscale_min,
    payscale_max,
    COUNT(*) AS affected_rows
FROM workforce
WHERE
    grade LIKE '%Senior%'
    AND payscale_max < 40000
GROUP BY
    grade,
    generic_job_title,
    payscale_min,
    payscale_max
ORDER BY affected_rows DESC;

-- 3. Organisations with inverted pay scales (min > max)
SELECT
    organisation,
    COUNT(*) AS inverted_payscale_rows
FROM workforce
WHERE payscale_min > payscale_max
GROUP BY organisation
ORDER BY inverted_payscale_rows DESC;
