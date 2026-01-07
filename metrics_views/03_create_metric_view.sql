USE CATALOG renjiharold_demo;
USE SCHEMA superfund_membership;
-- =============================================================================
-- Super Fund Membership - Metric View Definition
-- =============================================================================
-- This script creates a comprehensive metric view for super fund analytics.
-- The metric view provides pre-defined dimensions and measures that can be
-- used with AI/BI Genie and AI/BI Dashboards.
--
-- Prerequisites:
-- - Tables created and populated using 01_create_tables.sql and 02_insert_sample_data.sql
-- - Databricks Runtime 17.2 or above
-- - CREATE TABLE and USE SCHEMA privileges
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Main Metric View: Super Fund Membership Analytics
-- -----------------------------------------------------------------------------
-- This metric view uses a SQL query as source to join relevant tables and
-- provide a comprehensive view of member contributions, balances, and demographics.

CREATE OR REPLACE VIEW membership_metrics
WITH METRICS
LANGUAGE YAML
AS $$
  version: 1.1
  comment: "Super Fund Membership KPIs for financial analysis, member engagement, and regulatory reporting"
  
  # Source is a SQL query joining members, contributions, and related tables
  source: |
    SELECT 
      m.member_id,
      m.first_name,
      m.last_name,
      m.date_of_birth,
      m.gender,
      m.state,
      m.postcode,
      m.member_type,
      m.membership_status,
      m.join_date,
      m.insurance_opted_in,
      e.employer_id,
      e.employer_name,
      e.industry,
      e.employer_size,
      e.state as employer_state,
      c.contribution_id,
      c.contribution_type,
      c.contribution_date,
      c.financial_year,
      c.amount as contribution_amount,
      c.is_concessional,
      c.payment_method,
      COALESCE(mb.total_balance, 0) as member_balance,
      FLOOR(DATEDIFF(CURRENT_DATE(), m.date_of_birth) / 365.25) as member_age,
      FLOOR(DATEDIFF(CURRENT_DATE(), m.join_date) / 365.25) as membership_years
    FROM members m
    LEFT JOIN employers e ON m.employer_id = e.employer_id
    LEFT JOIN contributions c ON m.member_id = c.member_id AND c.status = 'Processed'
    LEFT JOIN (
      SELECT member_id, SUM(current_balance) as total_balance 
      FROM member_investments 
      GROUP BY member_id
    ) mb ON m.member_id = mb.member_id
  
  # Filter to focus on meaningful data
  filter: contribution_date >= '2021-01-01' OR contribution_date IS NULL
  
  dimensions:
    - name: Member State
      expr: state
      comment: "Australian state/territory where the member resides"
    
    - name: Member Type
      expr: member_type
      comment: "Type of membership: Accumulation, Pension, or Transition to Retirement"
    
    - name: Membership Status
      expr: membership_status
      comment: "Current status of the membership: Active, Inactive, or Closed"
    
    - name: Contribution Year
      expr: financial_year
      comment: "Australian financial year of the contribution (July to June)"
    
    - name: Contribution Quarter
      expr: |
        CASE 
          WHEN MONTH(contribution_date) IN (7, 8, 9) THEN 'Q1'
          WHEN MONTH(contribution_date) IN (10, 11, 12) THEN 'Q2'
          WHEN MONTH(contribution_date) IN (1, 2, 3) THEN 'Q3'
          ELSE 'Q4'
        END
      comment: "Quarter within the financial year"
    
    - name: Contribution Month
      expr: DATE_TRUNC('MONTH', contribution_date)
      comment: "Month of the contribution"
    
    - name: Contribution Type
      expr: |
        CASE 
          WHEN contribution_type = 'Employer SG' THEN 'Employer Superannuation Guarantee'
          WHEN contribution_type = 'Salary Sacrifice' THEN 'Salary Sacrifice'
          WHEN contribution_type = 'Personal' THEN 'Personal Contribution'
          WHEN contribution_type = 'Spouse' THEN 'Spouse Contribution'
          WHEN contribution_type = 'Government Co-contribution' THEN 'Government Co-contribution'
          WHEN contribution_type = 'Rollover In' THEN 'Rollover In'
          ELSE contribution_type
        END
      comment: "Type of contribution made to the super fund"
    
    - name: Is Concessional
      expr: CASE WHEN is_concessional THEN 'Yes' ELSE 'No' END
      comment: "Whether the contribution is concessional (pre-tax) or non-concessional (post-tax)"
    
    - name: Employer Industry
      expr: industry
      comment: "Industry sector of the member's employer"
    
    - name: Employer Size
      expr: employer_size
      comment: "Size category of the employer: Small, Medium, Large, or Enterprise"
    
    - name: Employer Name
      expr: employer_name
      comment: "Name of the sponsoring employer"
    
    - name: Gender
      expr: gender
      comment: "Member's gender"
    
    - name: Age Band
      expr: |
        CASE 
          WHEN member_age < 25 THEN 'Under 25'
          WHEN member_age BETWEEN 25 AND 34 THEN '25-34'
          WHEN member_age BETWEEN 35 AND 44 THEN '35-44'
          WHEN member_age BETWEEN 45 AND 54 THEN '45-54'
          WHEN member_age BETWEEN 55 AND 64 THEN '55-64'
          ELSE '65 and over'
        END
      comment: "Age band of the member for demographic analysis"
    
    - name: Balance Band
      expr: |
        CASE 
          WHEN member_balance < 10000 THEN 'Under $10K'
          WHEN member_balance BETWEEN 10000 AND 49999 THEN '$10K-$50K'
          WHEN member_balance BETWEEN 50000 AND 99999 THEN '$50K-$100K'
          WHEN member_balance BETWEEN 100000 AND 249999 THEN '$100K-$250K'
          WHEN member_balance BETWEEN 250000 AND 499999 THEN '$250K-$500K'
          ELSE '$500K and over'
        END
      comment: "Account balance range for segmentation"
    
    - name: Tenure Band
      expr: |
        CASE 
          WHEN membership_years < 1 THEN 'Less than 1 year'
          WHEN membership_years BETWEEN 1 AND 2 THEN '1-2 years'
          WHEN membership_years BETWEEN 3 AND 5 THEN '3-5 years'
          WHEN membership_years BETWEEN 6 AND 10 THEN '6-10 years'
          ELSE 'Over 10 years'
        END
      comment: "Length of membership for retention analysis"
    
    - name: Has Insurance
      expr: CASE WHEN insurance_opted_in THEN 'Yes' ELSE 'No' END
      comment: "Whether the member has opted into insurance coverage"
    
    - name: Payment Method
      expr: payment_method
      comment: "Method used to process the contribution payment"

  measures:
    - name: Total Contributions
      expr: SUM(contribution_amount)
      comment: "Sum of all contribution amounts"
    
    - name: Average Contribution
      expr: AVG(contribution_amount)
      comment: "Average contribution amount per transaction"
    
    - name: Contribution Count
      expr: COUNT(contribution_id)
      comment: "Number of contribution transactions"
    
    - name: Member Count
      expr: COUNT(DISTINCT member_id)
      comment: "Number of unique members"
    
    - name: Total Member Balance
      expr: SUM(DISTINCT member_balance)
      comment: "Sum of all member account balances (deduplicated)"
    
    - name: Average Member Balance
      expr: AVG(DISTINCT member_balance)
      comment: "Average account balance per member"
    
    - name: Concessional Contributions
      expr: SUM(contribution_amount) FILTER (WHERE is_concessional = TRUE)
      comment: "Total pre-tax (concessional) contributions"
    
    - name: Non-Concessional Contributions
      expr: SUM(contribution_amount) FILTER (WHERE is_concessional = FALSE)
      comment: "Total post-tax (non-concessional) contributions"
    
    - name: Employer Contributions
      expr: SUM(contribution_amount) FILTER (WHERE contribution_type = 'Employer SG')
      comment: "Total employer superannuation guarantee contributions"
    
    - name: Voluntary Contributions
      expr: SUM(contribution_amount) FILTER (WHERE contribution_type IN ('Salary Sacrifice', 'Personal'))
      comment: "Total voluntary contributions (salary sacrifice + personal)"
    
    - name: Average Contributions Per Member
      expr: SUM(contribution_amount) / NULLIF(COUNT(DISTINCT member_id), 0)
      comment: "Average total contributions per unique member"
    
    - name: Active Member Count
      expr: COUNT(DISTINCT member_id) FILTER (WHERE membership_status = 'Active')
      comment: "Number of members with active status"
    
    - name: Pension Member Count
      expr: COUNT(DISTINCT member_id) FILTER (WHERE member_type = 'Pension')
      comment: "Number of members in pension phase"
    
    - name: Insurance Opt-In Rate
      expr: COUNT(DISTINCT member_id) FILTER (WHERE insurance_opted_in = TRUE) * 100.0 / NULLIF(COUNT(DISTINCT member_id), 0)
      comment: "Percentage of members who have opted into insurance"
    
    - name: Average Member Age
      expr: AVG(DISTINCT member_age)
      comment: "Average age of members in years"
    
    - name: Average Tenure Years
      expr: AVG(DISTINCT membership_years)
      comment: "Average length of membership in years"
    
    - name: High Balance Member Count
      expr: COUNT(DISTINCT member_id) FILTER (WHERE member_balance >= 250000)
      comment: "Number of members with balance $250K or more"
    
    - name: New Members This Year
      expr: COUNT(DISTINCT member_id) FILTER (WHERE YEAR(join_date) = YEAR(CURRENT_DATE()))
      comment: "Number of members who joined in the current calendar year"
$$;

-- -----------------------------------------------------------------------------
-- Additional Metric View: Fee Analysis
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW fee_metrics
WITH METRICS
LANGUAGE YAML
AS $$
  version: 1.1
  comment: "Fee analysis metrics for super fund cost management and member impact assessment"
  
  source: |
    SELECT 
      f.fee_id,
      f.member_id,
      f.fee_type,
      f.fee_date,
      f.financial_year,
      f.amount as fee_amount,
      m.member_type,
      m.membership_status,
      m.state,
      m.gender,
      FLOOR(DATEDIFF(CURRENT_DATE(), m.date_of_birth) / 365.25) as member_age,
      e.industry,
      e.employer_size,
      COALESCE(mb.total_balance, 0) as member_balance
    FROM fees f
    JOIN members m ON f.member_id = m.member_id
    LEFT JOIN employers e ON m.employer_id = e.employer_id
    LEFT JOIN (
      SELECT member_id, SUM(current_balance) as total_balance 
      FROM member_investments 
      GROUP BY member_id
    ) mb ON m.member_id = mb.member_id
  
  dimensions:
    - name: Fee Type
      expr: fee_type
      comment: "Category of fee: Administration, Investment, Insurance, Advice, or Exit"
    
    - name: Financial Year
      expr: financial_year
      comment: "Australian financial year when the fee was charged"
    
    - name: Fee Month
      expr: DATE_TRUNC('MONTH', fee_date)
      comment: "Month when the fee was charged"
    
    - name: Member Type
      expr: member_type
      comment: "Type of membership"
    
    - name: Member State
      expr: state
      comment: "State where the member resides"
    
    - name: Industry
      expr: industry
      comment: "Industry of the member's employer"

  measures:
    - name: Total Fees
      expr: SUM(fee_amount)
      comment: "Sum of all fee amounts"
    
    - name: Average Fee
      expr: AVG(fee_amount)
      comment: "Average fee amount per transaction"
    
    - name: Fee Count
      expr: COUNT(fee_id)
      comment: "Number of fee transactions"
    
    - name: Members Charged
      expr: COUNT(DISTINCT member_id)
      comment: "Number of unique members charged fees"
    
    - name: Admin Fees
      expr: SUM(fee_amount) FILTER (WHERE fee_type = 'Administration')
      comment: "Total administration fees charged"
    
    - name: Insurance Premiums
      expr: SUM(fee_amount) FILTER (WHERE fee_type = 'Insurance')
      comment: "Total insurance premiums charged"
    
    - name: Investment Fees
      expr: SUM(fee_amount) FILTER (WHERE fee_type = 'Investment')
      comment: "Total investment management fees charged"
    
    - name: Average Fee Per Member
      expr: SUM(fee_amount) / NULLIF(COUNT(DISTINCT member_id), 0)
      comment: "Average total fees per unique member"
    
    - name: Fee to Balance Ratio
      expr: SUM(fee_amount) * 100.0 / NULLIF(SUM(DISTINCT member_balance), 0)
      comment: "Total fees as a percentage of total member balances"
$$;

-- -----------------------------------------------------------------------------
-- Additional Metric View: Withdrawal Analysis  
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW withdrawal_metrics
WITH METRICS
LANGUAGE YAML
AS $$
  version: 1.1
  comment: "Withdrawal and benefit payment metrics for cash flow analysis and member transitions"
  
  source: |
    SELECT 
      w.withdrawal_id,
      w.member_id,
      w.withdrawal_type,
      w.withdrawal_date,
      w.financial_year,
      w.amount as withdrawal_amount,
      w.tax_withheld,
      w.net_amount,
      w.destination,
      w.status,
      m.member_type,
      m.state,
      m.gender,
      FLOOR(DATEDIFF(CURRENT_DATE(), m.date_of_birth) / 365.25) as member_age,
      e.industry
    FROM withdrawals w
    JOIN members m ON w.member_id = m.member_id
    LEFT JOIN employers e ON m.employer_id = e.employer_id
  
  filter: status = 'Paid'
  
  dimensions:
    - name: Withdrawal Type
      expr: |
        CASE 
          WHEN withdrawal_type = 'Pension Payment' THEN 'Regular Pension Payment'
          WHEN withdrawal_type = 'Retirement' THEN 'Retirement Lump Sum'
          WHEN withdrawal_type = 'Rollover Out' THEN 'Transfer to Another Fund'
          WHEN withdrawal_type = 'Early Release' THEN 'Early Release (Hardship)'
          ELSE withdrawal_type
        END
      comment: "Type of withdrawal or benefit payment"
    
    - name: Financial Year
      expr: financial_year
      comment: "Australian financial year of the withdrawal"
    
    - name: Withdrawal Month
      expr: DATE_TRUNC('MONTH', withdrawal_date)
      comment: "Month of the withdrawal"
    
    - name: Destination
      expr: destination
      comment: "Where the funds were sent"
    
    - name: Member State
      expr: state
      comment: "State where the member resides"
    
    - name: Age Band
      expr: |
        CASE 
          WHEN member_age < 55 THEN 'Under 55'
          WHEN member_age BETWEEN 55 AND 59 THEN '55-59'
          WHEN member_age BETWEEN 60 AND 64 THEN '60-64'
          WHEN member_age BETWEEN 65 AND 74 THEN '65-74'
          ELSE '75 and over'
        END
      comment: "Age band of the member at withdrawal"

  measures:
    - name: Total Withdrawals
      expr: SUM(withdrawal_amount)
      comment: "Sum of all gross withdrawal amounts"
    
    - name: Total Net Payments
      expr: SUM(net_amount)
      comment: "Sum of all net payments after tax"
    
    - name: Total Tax Withheld
      expr: SUM(tax_withheld)
      comment: "Sum of all tax withheld from withdrawals"
    
    - name: Withdrawal Count
      expr: COUNT(withdrawal_id)
      comment: "Number of withdrawal transactions"
    
    - name: Members with Withdrawals
      expr: COUNT(DISTINCT member_id)
      comment: "Number of unique members who made withdrawals"
    
    - name: Average Withdrawal
      expr: AVG(withdrawal_amount)
      comment: "Average withdrawal amount per transaction"
    
    - name: Pension Payments
      expr: SUM(withdrawal_amount) FILTER (WHERE withdrawal_type = 'Pension Payment')
      comment: "Total regular pension payments"
    
    - name: Rollovers Out
      expr: SUM(withdrawal_amount) FILTER (WHERE withdrawal_type = 'Rollover Out')
      comment: "Total funds transferred to other super funds"
    
    - name: Retirement Lump Sums
      expr: SUM(withdrawal_amount) FILTER (WHERE withdrawal_type = 'Retirement')
      comment: "Total retirement lump sum payments"
    
    - name: Average Pension Payment
      expr: AVG(withdrawal_amount) FILTER (WHERE withdrawal_type = 'Pension Payment')
      comment: "Average regular pension payment amount"
$$;

-- =============================================================================
-- Verify the metric views were created
-- =============================================================================
-- DESCRIBE TABLE EXTENDED superfund_membership_metrics AS JSON;
-- DESCRIBE TABLE EXTENDED superfund_fee_metrics AS JSON;
-- DESCRIBE TABLE EXTENDED superfund_withdrawal_metrics AS JSON;

