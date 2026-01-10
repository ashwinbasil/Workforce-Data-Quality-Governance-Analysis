-- SLA thresholds for checks
CREATE TABLE IF NOT EXISTS dq_sla_rules (
    check_name TEXT PRIMARY KEY,
    max_failed_rows INTEGER,
    severity TEXT
);

DELETE FROM dq_sla_rules;

INSERT INTO dq_sla_rules VALUES
('missing_parent_department', 0, 'CRITICAL'),
('missing_organisation', 0, 'CRITICAL'),
('missing_grade', 0, 'HIGH'),
('missing_job_title', 0, 'HIGH'),
('missing_office_region', 0, 'MEDIUM'),
('invalid_fte_negative', 0, 'CRITICAL'),
('invalid_fte_unrealistic', 5, 'HIGH'),
('payscale_min_greater_than_max', 0, 'CRITICAL'),
('missing_payscale', 10, 'HIGH'),
('senior_role_low_pay', 2, 'MEDIUM');
