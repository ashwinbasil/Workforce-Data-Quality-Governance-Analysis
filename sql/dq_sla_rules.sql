-- SLA thresholds per check. check_name values must exactly match
-- the check_name strings produced in dq_workforce_checks.sql --
-- a mismatch here doesn't error, it silently disappears from
-- dq_sla_evaluation.csv because run_workforce_dq.py joins these
-- two tables with an INNER JOIN. That's how 'missing_payscale' went
-- unevaluated for every run before this fix, and it's how a rename
-- (invalid_fte_unrealistic -> invalid_fte_outlier_by_grade) would
-- have silently dropped the FTE check out of SLA reporting if the
-- rename here hadn't been applied to match.
DROP TABLE IF EXISTS dq_sla_rules;
CREATE TABLE dq_sla_rules (
    check_name TEXT PRIMARY KEY,
    max_failed_rows INTEGER,
    severity TEXT
);

INSERT INTO dq_sla_rules (check_name, max_failed_rows, severity) VALUES
    ('missing_parent_department', 0, 'CRITICAL'),
    ('missing_organisation', 0, 'CRITICAL'),
    ('missing_grade', 0, 'HIGH'),
    ('missing_job_title', 0, 'HIGH'),
    ('missing_office_region', 0, 'MEDIUM'),
    ('invalid_fte_negative', 0, 'CRITICAL'),
    ('invalid_fte_outlier_by_grade', 15, 'HIGH'),
    ('payscale_min_greater_than_max', 0, 'CRITICAL'),
    ('missing_payscale', 10, 'HIGH'),
    ('senior_role_low_pay', 2, 'MEDIUM'),
    ('inconsistent_region_casing', 0, 'MEDIUM'),
    ('placeholder_office_region', 50, 'LOW');