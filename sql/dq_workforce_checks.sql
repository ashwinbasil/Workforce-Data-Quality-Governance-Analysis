DROP TABLE IF EXISTS dq_failures;

CREATE TABLE dq_failures (
    check_name TEXT,
    record_id INTEGER
);

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
