-- DATA QUALITY CHECKS FOR CUSTOMERS TABLE

-- Missing email
SELECT 'missing_email' AS check_name, COUNT(*) AS failed_rows
FROM customers
WHERE email IS NULL;

-- Missing phone
SELECT 'missing_phone' AS check_name, COUNT(*) AS failed_rows
FROM customers
WHERE phone_number IS NULL;

-- Duplicate emails
SELECT 'duplicate_email' AS check_name, COUNT(*) AS failed_rows
FROM (
    SELECT email
    FROM customers
    WHERE email IS NOT NULL
    GROUP BY email
    HAVING COUNT(*) > 1
);

-- Invalid email format
SELECT 'invalid_email_format' AS check_name, COUNT(*) AS failed_rows
FROM customers
WHERE email IS NOT NULL
AND email NOT LIKE '%@%.%';

-- Temporal consistency
SELECT 'last_active_before_signup' AS check_name, COUNT(*) AS failed_rows
FROM customers
WHERE last_active < signup_date;
