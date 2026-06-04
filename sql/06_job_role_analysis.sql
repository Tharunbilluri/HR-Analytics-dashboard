-- Job role analysis: headcount, attrition, and satisfaction

SELECT
    job_role,
    department,
    COUNT(*) AS total_employees,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) AS attrition_count,
    ROUND(
        100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS attrition_rate_pct,
    ROUND(AVG(monthly_income), 2) AS avg_monthly_income,
    ROUND(AVG(job_satisfaction), 2) AS avg_job_satisfaction,
    ROUND(AVG(years_at_company), 2) AS avg_tenure_years
FROM employees
GROUP BY job_role, department
ORDER BY attrition_rate_pct DESC, total_employees DESC;

-- Top roles at highest risk
SELECT
    job_role,
    COUNT(*) AS total,
    ROUND(
        100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS attrition_rate_pct
FROM employees
GROUP BY job_role
HAVING COUNT(*) >= 20
ORDER BY attrition_rate_pct DESC
LIMIT 10;
