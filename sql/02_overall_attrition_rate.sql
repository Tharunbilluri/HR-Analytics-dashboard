-- Overall attrition rate (percentage of employees who left)

-- MySQL / PostgreSQL
SELECT
    COUNT(*) AS total_employees,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) AS attrition_count,
    SUM(CASE WHEN attrition = 'No' THEN 1 ELSE 0 END) AS retained_count,
    ROUND(
        100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS attrition_rate_pct
FROM employees;
