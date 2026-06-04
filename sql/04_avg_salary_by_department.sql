-- Average salary (monthly income) by department

SELECT
    department,
    COUNT(*) AS employee_count,
    ROUND(AVG(monthly_income), 2) AS avg_monthly_income,
    MIN(monthly_income) AS min_monthly_income,
    MAX(monthly_income) AS max_monthly_income,
    ROUND(AVG(percent_salary_hike), 2) AS avg_salary_hike_pct
FROM employees
GROUP BY department
ORDER BY avg_monthly_income DESC;
