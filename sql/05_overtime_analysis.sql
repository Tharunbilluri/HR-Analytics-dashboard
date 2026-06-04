-- Overtime analysis: attrition and compensation patterns

SELECT
    over_time,
    COUNT(*) AS total_employees,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) AS attrition_count,
    ROUND(
        100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS attrition_rate_pct,
    ROUND(AVG(monthly_income), 2) AS avg_monthly_income,
    ROUND(AVG(years_at_company), 2) AS avg_years_at_company
FROM employees
GROUP BY over_time
ORDER BY attrition_rate_pct DESC;

-- Overtime by department
SELECT
    department,
    over_time,
    COUNT(*) AS headcount,
    ROUND(
        100.0 * SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS attrition_rate_pct
FROM employees
GROUP BY department, over_time
ORDER BY department, over_time;
