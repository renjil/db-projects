# Super Fund Membership - Metric Views Demo

This demo showcases Databricks **Metric Views** capability using a superannuation (super fund) membership use case. The metric views integrate seamlessly with **AI/BI Genie** to enable natural language querying of fund data.

## Overview

Metric Views provide a semantic layer that defines reusable business metrics (dimensions and measures) that can be consumed by:
- **AI/BI Genie** - Natural language queries
- **AI/BI Dashboards** - Visual analytics
- **SQL queries** - Direct querying via `EVALUATE_METRIC_VIEW()`

## Data Model

The demo includes **7 tables** representing a complete super fund membership system:

| Table | Description |
|-------|-------------|
| `members` | Core member demographics and status |
| `employers` | Sponsoring employer organizations |
| `investment_options` | Available investment choices |
| `member_investments` | Member investment allocations and balances |
| `contributions` | Contribution transactions (employer, personal, etc.) |
| `withdrawals` | Withdrawal and benefit payment transactions |
| `fees` | Fee charges (admin, insurance, investment) |

## Metric Views Created

### 1. `superfund_membership_metrics`
Primary metric view for member and contribution analytics.

**Dimensions:**
- Member State, Member Type, Membership Status
- Contribution Year, Quarter, Month, Type
- Employer Industry, Size, Name
- Age Band, Balance Band, Tenure Band
- Gender, Has Insurance, Payment Method

**Measures:**
- Total/Average Contributions, Contribution Count
- Member Count, Active Member Count
- Total/Average Member Balance
- Concessional vs Non-Concessional Contributions
- Insurance Opt-In Rate, Average Age/Tenure

### 2. `superfund_fee_metrics`
Fee analysis for cost management.

**Key Measures:** Total Fees by type, Average Fee Per Member, Fee to Balance Ratio

### 3. `superfund_withdrawal_metrics`
Withdrawal and benefit payment analysis.

**Key Measures:** Total Withdrawals, Pension Payments, Rollovers Out, Tax Withheld

## Setup Instructions

### Step 1: Create Tables
```sql
-- Set your target catalog and schema
USE CATALOG your_catalog;
USE SCHEMA your_schema;

-- Run the table creation script
-- Execute: 01_create_tables.sql
```

### Step 2: Insert Sample Data
```sql
-- Run the data population script
-- Execute: 02_insert_sample_data.sql
```

### Step 3: Create Metric Views
```sql
-- Run the metric view creation script
-- Execute: 03_create_metric_view.sql
```

### Step 4: Add to Genie Space
1. Navigate to AI/BI Genie in your Databricks workspace
2. Create a new Genie space or open an existing one
3. Add the metric views: `superfund_membership_metrics`, `superfund_fee_metrics`, `superfund_withdrawal_metrics`

---

## Sample Questions for Genie

These questions demonstrate the power of metric views with AI/BI Genie. They range from simple aggregations to complex multi-dimensional analysis.

### Basic Analytics

1. **"What is the total contributions for FY2024?"**
   - Tests basic measure aggregation with dimension filtering

2. **"How many active members do we have?"**
   - Tests simple count with status filter

3. **"What is the average member balance?"**
   - Tests average calculation across members

### Dimensional Analysis

4. **"Show me total contributions by member state"**
   - Tests grouping by a single dimension

5. **"What is the breakdown of contributions by contribution type?"**
   - Tests categorical dimension analysis

6. **"Compare concessional vs non-concessional contributions by financial year"**
   - Tests multiple measures with dimension breakdown

### Multi-Dimensional Queries

7. **"What are the total contributions by employer industry and contribution year?"**
   - Tests two-dimensional grouping

8. **"Show me member count by age band and gender"**
   - Tests demographic segmentation

9. **"What is the average contribution per member by state and member type?"**
   - Tests complex measure with multiple dimensions

### Trend Analysis

10. **"How have contributions changed over time?"**
    - Tests time-series analysis by financial year

11. **"Show me the contribution trend by quarter for FY2024"**
    - Tests quarterly granularity

12. **"What is the month-over-month contribution growth?"**
    - Tests temporal comparison

### Comparative Analysis

13. **"Which employer industry has the highest average contribution per member?"**
    - Tests ranking and comparison

14. **"Compare pension members vs accumulation members by average balance"**
    - Tests segment comparison

15. **"Which state has the highest insurance opt-in rate?"**
    - Tests percentage measure with ranking

### Complex Business Questions

16. **"What percentage of our total contributions come from employer superannuation guarantee?"**
    - Tests ratio calculation

17. **"How does the average balance vary by tenure band?"**
    - Tests relationship between tenure and financial outcomes

18. **"What is the distribution of members across balance bands?"**
    - Tests segmentation analysis

19. **"Show me the top 5 employers by total contribution volume"**
    - Tests ranking with limit

20. **"What is the contribution split between voluntary and employer contributions by year?"**
    - Tests measure categorization over time

### Cross-Metric View Questions (if all views added)

21. **"What is the ratio of total fees to total contributions by financial year?"**
    - Tests cross-metric analysis

22. **"How do pension payments compare to total withdrawals?"**
    - Tests withdrawal type analysis

23. **"What is the net fund flow (contributions minus withdrawals) by quarter?"**
    - Tests computed metrics across views

24. **"Which member segments have the highest rollover out rates?"**
    - Tests churn/retention analysis

### Regulatory & Compliance Questions

25. **"How many members have concessional contributions exceeding $25,000 in FY2024?"**
    - Tests threshold-based filtering (concessional cap)

26. **"What is the gender split of our pension members?"**
    - Tests demographic compliance reporting

27. **"Show me the age distribution of members approaching retirement (55+)"**
    - Tests regulatory-relevant segmentation

### Executive Summary Questions

28. **"Give me a summary of key fund metrics for FY2024"**
    - Tests ability to aggregate multiple measures

29. **"What are the year-over-year changes in member count and average balance?"**
    - Tests comparative period analysis

30. **"Which segments should we focus on for growth?"**
    - Tests insight generation capability

---

## Why Metric Views + Genie?

### Benefits Demonstrated

1. **Semantic Layer**: Business users ask questions in plain English without knowing SQL
2. **Consistency**: Pre-defined measures ensure everyone uses the same calculations
3. **Governance**: Centralized metric definitions under Unity Catalog
4. **Self-Service**: Business analysts can explore data without technical help
5. **AI-Powered**: Genie understands context and intent from natural language

### Key Differentiators

- **No SQL Required**: Users ask "What is the average contribution?" not `SELECT AVG(amount) FROM contributions`
- **Business Context**: Dimensions have meaningful names like "Age Band" not `CASE WHEN age < 25 THEN...`
- **Pre-Computed Logic**: Complex calculations like "Insurance Opt-In Rate" are defined once
- **Unified Semantics**: Same metrics work across Genie, Dashboards, and SQL

## Additional Resources

- [Databricks Metric Views Documentation](https://docs.databricks.com/aws/en/metric-views/create/sql)
- [AI/BI Genie Documentation](https://docs.databricks.com/aws/en/genie/)
- [AI/BI Dashboards](https://docs.databricks.com/aws/en/dashboards/)

