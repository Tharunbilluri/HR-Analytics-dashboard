-- Example: load CSV into MySQL employees table (adjust file path)
-- Requires local_infile enabled and CSV column mapping

LOAD DATA LOCAL INFILE '/path/to/WA_Fn-UseC_-HR-Employee-Attrition.csv'
INTO TABLE employees
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@age, @attrition, @business_travel, @daily_rate, @department,
 @distance_from_home, @education, @education_field, @employee_count,
 @employee_number, @environment_satisfaction, @gender, @hourly_rate,
 @job_involvement, @job_level, @job_role, @job_satisfaction,
 @marital_status, @monthly_income, @monthly_rate, @num_companies_worked,
 @over18, @over_time, @percent_salary_hike, @performance_rating,
 @relationship_satisfaction, @standard_hours, @stock_option_level,
 @total_working_years, @training_times_last_year, @work_life_balance,
 @years_at_company, @years_in_current_role, @years_since_last_promotion,
 @years_with_curr_manager)
SET
    age = @age,
    attrition = @attrition,
    business_travel = @business_travel,
    daily_rate = @daily_rate,
    department = @department,
    distance_from_home = @distance_from_home,
    education = @education,
    education_field = @education_field,
    environment_satisfaction = @environment_satisfaction,
    gender = @gender,
    hourly_rate = @hourly_rate,
    job_involvement = @job_involvement,
    job_level = @job_level,
    job_role = @job_role,
    job_satisfaction = @job_satisfaction,
    marital_status = @marital_status,
    monthly_income = @monthly_income,
    monthly_rate = @monthly_rate,
    num_companies_worked = @num_companies_worked,
    over_time = @over_time,
    percent_salary_hike = @percent_salary_hike,
    performance_rating = @performance_rating,
    relationship_satisfaction = @relationship_satisfaction,
    stock_option_level = @stock_option_level,
    total_working_years = @total_working_years,
    training_times_last_year = @training_times_last_year,
    work_life_balance = @work_life_balance,
    years_at_company = @years_at_company,
    years_in_current_role = @years_in_current_role,
    years_since_last_promotion = @years_since_last_promotion,
    years_with_curr_manager = @years_with_curr_manager;
