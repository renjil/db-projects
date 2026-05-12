-- ============================================================================
-- 7-Eleven Store Intelligence Demo - Row-Level Security Setup
-- Catalog/Schema: passed in as ${catalog}.${schema}
-- ============================================================================
-- This script sets up row-level security (RLS) for the Gold layer tables
-- Users only see data for stores they have access to
-- ============================================================================

USE CATALOG ${catalog};
USE SCHEMA ${schema};

-- ============================================================================
-- STEP 1: Create User-Store Access Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS silver_user_store_access (
  user_email STRING NOT NULL COMMENT 'User email address',
  store_id INT NOT NULL COMMENT 'Store ID the user has access to',
  role STRING COMMENT 'User role (e.g., Store Manager, Area Manager, Regional Manager)',
  access_level STRING COMMENT 'Access level (READ, WRITE, ADMIN)',
  granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When access was granted',
  granted_by STRING COMMENT 'Who granted the access',
  expires_at TIMESTAMP COMMENT 'When access expires (NULL = permanent)',
  is_active BOOLEAN DEFAULT TRUE COMMENT 'Whether access is currently active',
  CONSTRAINT pk_user_store PRIMARY KEY (user_email, store_id)
)
COMMENT 'User to store access mapping for row-level security';

-- ============================================================================
-- STEP 2: Add Sample Access Data for Demo Users
-- ============================================================================
-- Demo: All Databricks users get access to all stores
-- In production, this would be managed via identity provider integration

INSERT INTO silver_user_store_access (user_email, store_id, role, access_level, granted_by)
SELECT DISTINCT
  'demo@databricks.com' AS user_email,
  store_id,
  'Demo User' AS role,
  'READ' AS access_level,
  'system' AS granted_by
FROM silver_stores
WHERE NOT EXISTS (
  SELECT 1 FROM silver_user_store_access
  WHERE user_email = 'demo@databricks.com' AND silver_user_store_access.store_id = silver_stores.store_id
);

-- ============================================================================
-- STEP 3: Create Row Filter Function
-- ============================================================================
CREATE OR REPLACE FUNCTION check_store_access(store_id INT)
RETURNS BOOLEAN
COMMENT 'Row filter function for store-level access control'
RETURN (
  -- Databricks employees get access to all stores (for demo purposes)
  CURRENT_USER() LIKE '%@databricks.com'
  -- Or user has explicit access to this store
  OR EXISTS (
    SELECT 1
    FROM ${catalog}.${schema}.silver_user_store_access usa
    WHERE usa.user_email = CURRENT_USER()
      AND usa.store_id = check_store_access.store_id
      AND usa.is_active = TRUE
      AND (usa.expires_at IS NULL OR usa.expires_at > CURRENT_TIMESTAMP())
  )
);

-- ============================================================================
-- STEP 4: Apply Row Filter to Gold Tables
-- ============================================================================

-- Daily Store Summary
ALTER TABLE gold_daily_store_summary
SET ROW FILTER check_store_access ON (store_id);

-- Category Performance
ALTER TABLE gold_category_performance
SET ROW FILTER check_store_access ON (store_id);

-- Article APSD
ALTER TABLE gold_article_apsd
SET ROW FILTER check_store_access ON (store_id);

-- Inventory Health
ALTER TABLE gold_inventory_health
SET ROW FILTER check_store_access ON (store_id);

-- Dead Stock
ALTER TABLE gold_dead_stock
SET ROW FILTER check_store_access ON (store_id);

-- Hourly Sales
ALTER TABLE gold_hourly_sales
SET ROW FILTER check_store_access ON (store_id);

-- Write-off Summary
ALTER TABLE gold_writeoff_summary
SET ROW FILTER check_store_access ON (store_id);

-- Write-off Detail
ALTER TABLE gold_writeoff_detail
SET ROW FILTER check_store_access ON (store_id);

-- Write-off Reconciliation
ALTER TABLE gold_writeoff_reconciliation
SET ROW FILTER check_store_access ON (store_id);

-- Store Use Compliance
ALTER TABLE gold_store_use_compliance
SET ROW FILTER check_store_access ON (store_id);

-- Store Alerts
ALTER TABLE gold_store_alerts
SET ROW FILTER check_store_access ON (store_id);

-- ============================================================================
-- STEP 5: Add Geographic Coordinates to Stores
-- ============================================================================
-- Add columns for map visualization
ALTER TABLE silver_stores ADD COLUMNS IF NOT EXISTS (
  latitude DECIMAL(10,6) COMMENT 'Store latitude coordinate',
  longitude DECIMAL(10,6) COMMENT 'Store longitude coordinate'
);

-- Update with realistic Australian coordinates
-- Melbourne Area (VIC)
UPDATE silver_stores SET latitude = -37.8136, longitude = 144.9631 WHERE store_id = 1;
UPDATE silver_stores SET latitude = -37.9716, longitude = 145.0376 WHERE store_id = 2;
UPDATE silver_stores SET latitude = -37.8152, longitude = 144.9661 WHERE store_id = 3;

-- Sydney Area (NSW)
UPDATE silver_stores SET latitude = -33.8688, longitude = 151.2093 WHERE store_id = 4;
UPDATE silver_stores SET latitude = -33.7490, longitude = 151.2390 WHERE store_id = 5;
UPDATE silver_stores SET latitude = -33.8908, longitude = 151.2743 WHERE store_id = 6;

-- Brisbane Area (QLD)
UPDATE silver_stores SET latitude = -27.4705, longitude = 153.0260 WHERE store_id = 7;
UPDATE silver_stores SET latitude = -27.4975, longitude = 153.0137 WHERE store_id = 8;

-- Perth Area (WA)
UPDATE silver_stores SET latitude = -31.9505, longitude = 115.8605 WHERE store_id = 9;

-- Adelaide Area (SA)
UPDATE silver_stores SET latitude = -34.9285, longitude = 138.6007 WHERE store_id = 10;

-- ============================================================================
-- STEP 6: Create Helper Views for Access Management
-- ============================================================================

-- View: My Accessible Stores
CREATE OR REPLACE VIEW v_my_stores AS
SELECT
  s.*,
  usa.role,
  usa.access_level,
  usa.granted_at
FROM silver_stores s
JOIN silver_user_store_access usa ON s.store_id = usa.store_id
WHERE usa.user_email = CURRENT_USER()
  AND usa.is_active = TRUE
  AND (usa.expires_at IS NULL OR usa.expires_at > CURRENT_TIMESTAMP());

-- View: User Access Summary (for admins)
CREATE OR REPLACE VIEW v_user_access_summary AS
SELECT
  usa.user_email,
  COUNT(DISTINCT usa.store_id) AS store_count,
  COLLECT_SET(s.state) AS states,
  COLLECT_SET(usa.role) AS roles,
  MIN(usa.granted_at) AS first_grant,
  MAX(usa.granted_at) AS last_grant
FROM silver_user_store_access usa
JOIN silver_stores s ON usa.store_id = s.store_id
WHERE usa.is_active = TRUE
GROUP BY usa.user_email;

-- ============================================================================
-- STEP 7: Grant Permissions for Demo
-- ============================================================================
-- Grant SELECT on all Gold tables to users group
GRANT SELECT ON TABLE gold_daily_store_summary TO `users`;
GRANT SELECT ON TABLE gold_category_performance TO `users`;
GRANT SELECT ON TABLE gold_article_apsd TO `users`;
GRANT SELECT ON TABLE gold_inventory_health TO `users`;
GRANT SELECT ON TABLE gold_dead_stock TO `users`;
GRANT SELECT ON TABLE gold_hourly_sales TO `users`;
GRANT SELECT ON TABLE gold_writeoff_summary TO `users`;
GRANT SELECT ON TABLE gold_writeoff_detail TO `users`;
GRANT SELECT ON TABLE gold_writeoff_reconciliation TO `users`;
GRANT SELECT ON TABLE gold_store_use_compliance TO `users`;
GRANT SELECT ON TABLE gold_product_lookup TO `users`;
GRANT SELECT ON TABLE gold_store_alerts TO `users`;
GRANT SELECT ON TABLE gold_metrics TO `users`;
GRANT SELECT ON TABLE gold_store_kpi_summary TO `users`;
GRANT SELECT ON TABLE gold_category_rankings TO `users`;
GRANT SELECT ON TABLE gold_article_rankings TO `users`;
GRANT SELECT ON TABLE gold_inventory_summary TO `users`;
GRANT SELECT ON TABLE gold_writeoff_trends TO `users`;
GRANT SELECT ON TABLE gold_cook_quantity_guide TO `users`;

-- Grant EXECUTE on the row filter function
GRANT EXECUTE ON FUNCTION check_store_access TO `users`;

-- ============================================================================
-- STEP 8: Verification Queries
-- ============================================================================
-- Run these to verify RLS is working correctly

-- Check current user
SELECT CURRENT_USER() AS current_user;

-- Check accessible stores
SELECT * FROM v_my_stores;

-- Verify row filter is applied
DESCRIBE EXTENDED gold_daily_store_summary;

-- Test query (should only return accessible stores)
SELECT store_id, store_name, summary_date, total_sales
FROM gold_daily_store_summary
WHERE summary_date >= CURRENT_DATE() - 7
ORDER BY summary_date DESC, total_sales DESC
LIMIT 10;
