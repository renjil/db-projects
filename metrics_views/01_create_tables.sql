-- =============================================================================
-- Super Fund Membership Data Model
-- =============================================================================
-- This script creates the foundational tables for a superannuation fund 
-- membership analytics use case. Run this in Databricks SQL or a notebook.
--
-- Replace 'your_catalog.your_schema' with your target catalog and schema.
-- =============================================================================

-- Configuration: Set your target catalog and schema
-- USE CATALOG your_catalog;
-- USE SCHEMA your_schema;

-- -----------------------------------------------------------------------------
-- Table 1: MEMBERS - Core member information
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TABLE members (
    member_id STRING NOT NULL,
    first_name STRING,
    last_name STRING,
    date_of_birth DATE,
    gender STRING,
    email STRING,
    phone STRING,
    state STRING,
    postcode STRING,
    member_type STRING,  -- 'Accumulation', 'Pension', 'Transition to Retirement'
    membership_status STRING,  -- 'Active', 'Inactive', 'Closed'
    join_date DATE,
    employer_id STRING,
    insurance_opted_in BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- Table 2: EMPLOYERS - Employer/sponsor organizations
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TABLE employers (
    employer_id STRING NOT NULL,
    employer_name STRING,
    abn STRING,
    industry STRING,
    employer_size STRING,  -- 'Small', 'Medium', 'Large', 'Enterprise'
    state STRING,
    contribution_frequency STRING,  -- 'Weekly', 'Fortnightly', 'Monthly', 'Quarterly'
    default_contribution_rate DECIMAL(5,2),
    onboarded_date DATE,
    status STRING,  -- 'Active', 'Inactive'
    created_at TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- Table 3: INVESTMENT_OPTIONS - Available investment choices
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TABLE investment_options (
    option_id STRING NOT NULL,
    option_name STRING,
    option_category STRING,  -- 'Growth', 'Balanced', 'Conservative', 'Cash', 'Ethical'
    risk_level STRING,  -- 'High', 'Medium-High', 'Medium', 'Low-Medium', 'Low'
    target_return DECIMAL(5,2),
    management_fee_percent DECIMAL(5,4),
    is_default BOOLEAN,
    is_active BOOLEAN,
    created_at TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- Table 4: MEMBER_INVESTMENTS - Member's investment allocations
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TABLE member_investments (
    allocation_id STRING NOT NULL,
    member_id STRING,
    option_id STRING,
    allocation_percent DECIMAL(5,2),
    current_balance DECIMAL(18,2),
    effective_date DATE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- Table 5: CONTRIBUTIONS - All contribution transactions
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TABLE contributions (
    contribution_id STRING NOT NULL,
    member_id STRING,
    employer_id STRING,
    contribution_type STRING,  -- 'Employer SG', 'Salary Sacrifice', 'Personal', 'Spouse', 'Government Co-contribution', 'Rollover In'
    contribution_date DATE,
    financial_year STRING,
    amount DECIMAL(18,2),
    is_concessional BOOLEAN,
    payment_method STRING,  -- 'SuperStream', 'BPAY', 'Direct Debit', 'Rollover'
    status STRING,  -- 'Pending', 'Processed', 'Failed'
    created_at TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- Table 6: WITHDRAWALS - Withdrawal and benefit payment transactions
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TABLE withdrawals (
    withdrawal_id STRING NOT NULL,
    member_id STRING,
    withdrawal_type STRING,  -- 'Retirement', 'Early Release', 'Death Benefit', 'TPD', 'Rollover Out', 'Pension Payment'
    withdrawal_date DATE,
    financial_year STRING,
    amount DECIMAL(18,2),
    tax_withheld DECIMAL(18,2),
    net_amount DECIMAL(18,2),
    destination STRING,  -- 'Bank Account', 'Other Super Fund', 'Estate'
    status STRING,  -- 'Pending', 'Approved', 'Paid', 'Rejected'
    created_at TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- Table 7: FEES - Fee transactions charged to members
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TABLE fees (
    fee_id STRING NOT NULL,
    member_id STRING,
    fee_type STRING,  -- 'Administration', 'Investment', 'Insurance', 'Advice', 'Exit'
    fee_date DATE,
    financial_year STRING,
    amount DECIMAL(18,2),
    description STRING,
    created_at TIMESTAMP
);

