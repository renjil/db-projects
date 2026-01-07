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

See **[GENIE_QUESTIONS.md](GENIE_QUESTIONS.md)** for 30 sample questions organized by category:
- Basic Analytics
- Dimensional Analysis
- Multi-Dimensional Queries
- Trend Analysis
- Comparative Analysis
- Complex Business Questions
- Cross-Metric View Questions
- Regulatory & Compliance Questions
- Executive Summary Questions

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

