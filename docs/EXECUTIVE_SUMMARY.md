# HR Attrition — Executive Summary

## Executive Summary
- **Attrition Rate:** 16.1% (237 employees exited)
- **Estimated Attrition Cost:** $1.70M
- **Highest Risk Department:** Sales (20.6% attrition)
- **Overtime** increases attrition by 20.1 percentage points
- **39** employees identified for immediate retention intervention

## Expected Business Impact
If overtime-related attrition is reduced by 5 percentage points and the at-risk cohort is retained, the organization could prevent approximately 60 avoidable exits annually and reduce replacement costs by an estimated $430,838 (proxy based on 1.5× monthly salary per exit).

## Top Priorities
1. Reduce overtime exposure in high-risk teams
2. Execute Sales retention initiative
3. Complete stay interviews for all 39 at-risk employees within 14 days

## Department attrition
- Sales: 20.6%
- Human Resources: 19.0%
- Research & Development: 13.8%

## Model note
Production model: Random Forest — best accuracy (82.7%) for workforce screening. Logistic Regression — higher recall on leavers (76.6%) when catching flight risk matters more than avoiding false alarms. Use RF for prioritization lists; consider LR when missing leavers is costly.

*IBM HR Attrition dataset — synthetic data for portfolio demonstration.*