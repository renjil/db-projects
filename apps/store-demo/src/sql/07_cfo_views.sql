-- ============================================================================
-- 7-Eleven CFO Executive Dashboard - SQL Views
-- Catalog/Schema: passed in as ${catalog}.${schema}
-- ============================================================================

USE CATALOG ${catalog};
USE SCHEMA ${schema};

-- ============================================================================
-- CFO EXECUTIVE SUMMARY VIEW
-- High-level KPIs: MTD, YTD, vs Budget, YoY
-- ============================================================================

CREATE OR REPLACE VIEW vw_cfo_executive_summary AS
WITH mtd_data AS (
  SELECT
    SUM(total_sales) AS mtd_sales,
    SUM(total_gp) AS mtd_gp,
    ROUND(SUM(total_gp) / NULLIF(SUM(total_sales), 0) * 100, 2) AS mtd_gp_margin_pct,
    SUM(budget_sales) AS mtd_budget_sales,
    SUM(budget_gp) AS mtd_budget_gp,
    ROUND((SUM(total_sales) - SUM(budget_sales)) / NULLIF(SUM(budget_sales), 0) * 100, 2) AS mtd_vs_budget_pct,
    ROUND((SUM(total_gp) - SUM(budget_gp)) / NULLIF(SUM(budget_gp), 0) * 100, 2) AS mtd_gp_vs_budget_pct,
    SUM(ly_sales) AS mtd_ly_sales,
    SUM(ly_gp) AS mtd_ly_gp,
    ROUND((SUM(total_sales) - SUM(ly_sales)) / NULLIF(SUM(ly_sales), 0) * 100, 2) AS mtd_yoy_growth_pct,
    SUM(transaction_count) AS mtd_transactions,
    ROUND(SUM(total_sales) / NULLIF(SUM(transaction_count), 0), 2) AS mtd_avg_basket
  FROM gold_daily_store_summary
  WHERE summary_date >= DATE_TRUNC('MONTH', CURRENT_DATE())
    AND summary_date <= CURRENT_DATE()
),
ytd_data AS (
  SELECT
    SUM(total_sales) AS ytd_sales,
    SUM(total_gp) AS ytd_gp,
    ROUND(SUM(total_gp) / NULLIF(SUM(total_sales), 0) * 100, 2) AS ytd_gp_margin_pct,
    SUM(budget_sales) AS ytd_budget_sales,
    SUM(budget_gp) AS ytd_budget_gp,
    ROUND((SUM(total_sales) - SUM(budget_sales)) / NULLIF(SUM(budget_sales), 0) * 100, 2) AS ytd_vs_budget_pct,
    ROUND((SUM(total_gp) - SUM(budget_gp)) / NULLIF(SUM(budget_gp), 0) * 100, 2) AS ytd_gp_vs_budget_pct,
    SUM(ly_sales) AS ytd_ly_sales,
    ROUND((SUM(total_sales) - SUM(ly_sales)) / NULLIF(SUM(ly_sales), 0) * 100, 2) AS ytd_yoy_growth_pct
  FROM gold_daily_store_summary
  WHERE summary_date >= DATE_TRUNC('YEAR', CURRENT_DATE())
    AND summary_date <= CURRENT_DATE()
),
mtd_writeoffs AS (
  SELECT
    SUM(total_value) AS mtd_writeoff_value
  FROM gold_writeoff_summary
  WHERE writeoff_date >= DATE_TRUNC('MONTH', CURRENT_DATE())
    AND writeoff_date <= CURRENT_DATE()
)
SELECT
  m.*,
  y.ytd_sales,
  y.ytd_gp,
  y.ytd_gp_margin_pct,
  y.ytd_budget_sales,
  y.ytd_budget_gp,
  y.ytd_vs_budget_pct,
  y.ytd_gp_vs_budget_pct,
  y.ytd_yoy_growth_pct,
  w.mtd_writeoff_value,
  ROUND(w.mtd_writeoff_value / NULLIF(m.mtd_sales, 0) * 100, 2) AS mtd_writeoff_pct_of_sales
FROM mtd_data m, ytd_data y, mtd_writeoffs w;

-- ============================================================================
-- CFO MONTHLY SALES TREND VIEW
-- 12-month trend with TY vs LY comparison
-- ============================================================================

CREATE OR REPLACE VIEW vw_cfo_monthly_sales_trend AS
SELECT
  DATE_TRUNC('MONTH', summary_date) AS month_date,
  DATE_FORMAT(summary_date, 'MMM yyyy') AS month_label,
  SUM(total_sales) AS total_sales,
  SUM(total_gp) AS total_gp,
  ROUND(SUM(total_gp) / NULLIF(SUM(total_sales), 0) * 100, 2) AS gp_margin_pct,
  SUM(budget_sales) AS budget_sales,
  SUM(budget_gp) AS budget_gp,
  SUM(ly_sales) AS ly_sales,
  SUM(ly_gp) AS ly_gp,
  ROUND((SUM(total_sales) - SUM(ly_sales)) / NULLIF(SUM(ly_sales), 0) * 100, 2) AS yoy_growth_pct,
  ROUND((SUM(total_sales) - SUM(budget_sales)) / NULLIF(SUM(budget_sales), 0) * 100, 2) AS vs_budget_pct
FROM gold_daily_store_summary
WHERE summary_date >= ADD_MONTHS(DATE_TRUNC('MONTH', CURRENT_DATE()), -11)
  AND summary_date <= CURRENT_DATE()
GROUP BY DATE_TRUNC('MONTH', summary_date), DATE_FORMAT(summary_date, 'MMM yyyy')
ORDER BY month_date;

-- ============================================================================
-- CFO STATE PERFORMANCE VIEW
-- Performance by state with budget and YoY
-- ============================================================================

CREATE OR REPLACE VIEW vw_cfo_state_performance AS
SELECT
  state,
  SUM(total_sales) AS total_sales,
  SUM(total_gp) AS total_gp,
  ROUND(SUM(total_gp) / NULLIF(SUM(total_sales), 0) * 100, 2) AS gp_margin_pct,
  SUM(budget_sales) AS budget_sales,
  SUM(budget_gp) AS budget_gp,
  SUM(total_sales) - SUM(budget_sales) AS sales_variance,
  ROUND((SUM(total_sales) - SUM(budget_sales)) / NULLIF(SUM(budget_sales), 0) * 100, 2) AS vs_budget_pct,
  SUM(ly_sales) AS ly_sales,
  ROUND((SUM(total_sales) - SUM(ly_sales)) / NULLIF(SUM(ly_sales), 0) * 100, 2) AS yoy_growth_pct,
  SUM(transaction_count) AS transaction_count,
  COUNT(DISTINCT store_id) AS store_count
FROM gold_daily_store_summary
WHERE summary_date >= DATE_TRUNC('MONTH', CURRENT_DATE())
  AND summary_date <= CURRENT_DATE()
GROUP BY state
ORDER BY total_sales DESC;

-- ============================================================================
-- CFO BUDGET VARIANCE BY MONTH VIEW
-- Actual vs Budget by month for trend analysis
-- ============================================================================

CREATE OR REPLACE VIEW vw_cfo_budget_variance AS
SELECT
  DATE_TRUNC('MONTH', summary_date) AS month_date,
  DATE_FORMAT(summary_date, 'MMM yyyy') AS month_label,
  state,
  SUM(total_sales) AS actual_sales,
  SUM(budget_sales) AS budget_sales,
  SUM(total_sales) - SUM(budget_sales) AS sales_variance,
  ROUND((SUM(total_sales) - SUM(budget_sales)) / NULLIF(SUM(budget_sales), 0) * 100, 2) AS sales_variance_pct,
  SUM(total_gp) AS actual_gp,
  SUM(budget_gp) AS budget_gp,
  SUM(total_gp) - SUM(budget_gp) AS gp_variance,
  ROUND((SUM(total_gp) - SUM(budget_gp)) / NULLIF(SUM(budget_gp), 0) * 100, 2) AS gp_variance_pct
FROM gold_daily_store_summary
WHERE summary_date >= ADD_MONTHS(DATE_TRUNC('MONTH', CURRENT_DATE()), -11)
  AND summary_date <= CURRENT_DATE()
GROUP BY DATE_TRUNC('MONTH', summary_date), DATE_FORMAT(summary_date, 'MMM yyyy'), state
ORDER BY month_date, state;

-- ============================================================================
-- CFO CATEGORY PERFORMANCE VIEW
-- Category breakdown with GP contribution
-- ============================================================================

CREATE OR REPLACE VIEW vw_cfo_category_performance AS
SELECT
  category_name,
  department,
  SUM(total_sales) AS total_sales,
  SUM(total_gp) AS total_gp,
  ROUND(SUM(total_gp) / NULLIF(SUM(total_sales), 0) * 100, 2) AS gp_margin_pct,
  ROUND(SUM(total_sales) / NULLIF((SELECT SUM(total_sales) FROM gold_category_performance
    WHERE period_start >= DATE_TRUNC('MONTH', CURRENT_DATE())), 0) * 100, 2) AS sales_share_pct,
  ROUND(SUM(total_gp) / NULLIF((SELECT SUM(total_gp) FROM gold_category_performance
    WHERE period_start >= DATE_TRUNC('MONTH', CURRENT_DATE())), 0) * 100, 2) AS gp_share_pct,
  AVG(yoy_sales_growth) AS avg_yoy_sales_growth,
  AVG(yoy_gp_growth) AS avg_yoy_gp_growth,
  SUM(budget_sales) AS budget_sales,
  ROUND((SUM(total_sales) - SUM(budget_sales)) / NULLIF(SUM(budget_sales), 0) * 100, 2) AS vs_budget_pct
FROM gold_category_performance
WHERE period_start >= DATE_TRUNC('MONTH', CURRENT_DATE())
  AND period_start <= CURRENT_DATE()
GROUP BY category_name, department
ORDER BY total_sales DESC;

-- ============================================================================
-- CFO SHRINKAGE SUMMARY VIEW
-- Write-offs aggregated by state, category, reason
-- ============================================================================

CREATE OR REPLACE VIEW vw_cfo_shrinkage_summary AS
SELECT
  DATE_TRUNC('MONTH', writeoff_date) AS month_date,
  DATE_FORMAT(writeoff_date, 'MMM yyyy') AS month_label,
  SUM(total_value) AS total_writeoff_value,
  SUM(total_qty) AS total_writeoff_qty,
  SUM(item_count) AS item_count,
  SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END) AS anomaly_count
FROM gold_writeoff_summary
WHERE writeoff_date >= ADD_MONTHS(DATE_TRUNC('MONTH', CURRENT_DATE()), -11)
  AND writeoff_date <= CURRENT_DATE()
GROUP BY DATE_TRUNC('MONTH', writeoff_date), DATE_FORMAT(writeoff_date, 'MMM yyyy')
ORDER BY month_date;

-- ============================================================================
-- CFO SHRINKAGE BY STATE VIEW
-- Write-offs by state for geographic comparison
-- ============================================================================

CREATE OR REPLACE VIEW vw_cfo_shrinkage_by_state AS
SELECT
  ds.state,
  SUM(ws.total_value) AS writeoff_value,
  SUM(ws.total_qty) AS writeoff_qty,
  SUM(CASE WHEN ws.is_anomaly THEN 1 ELSE 0 END) AS anomaly_count,
  COUNT(DISTINCT ws.store_id) AS stores_with_writeoffs
FROM gold_writeoff_summary ws
JOIN gold_daily_store_summary ds
  ON ws.store_id = ds.store_id
  AND ws.writeoff_date = ds.summary_date
WHERE ws.writeoff_date >= DATE_TRUNC('MONTH', CURRENT_DATE())
  AND ws.writeoff_date <= CURRENT_DATE()
GROUP BY ds.state
ORDER BY writeoff_value DESC;

-- ============================================================================
-- CFO SHRINKAGE BY CATEGORY VIEW
-- Write-offs by category
-- ============================================================================

CREATE OR REPLACE VIEW vw_cfo_shrinkage_by_category AS
SELECT
  category_name,
  SUM(total_value) AS writeoff_value,
  SUM(total_qty) AS writeoff_qty,
  SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END) AS anomaly_count
FROM gold_writeoff_summary
WHERE writeoff_date >= DATE_TRUNC('MONTH', CURRENT_DATE())
  AND writeoff_date <= CURRENT_DATE()
GROUP BY category_name
ORDER BY writeoff_value DESC;

-- ============================================================================
-- CFO SHRINKAGE BY REASON VIEW
-- Write-offs by reason code
-- ============================================================================

CREATE OR REPLACE VIEW vw_cfo_shrinkage_by_reason AS
SELECT
  reason_code,
  SUM(total_value) AS writeoff_value,
  SUM(total_qty) AS writeoff_qty,
  COUNT(*) AS record_count
FROM gold_writeoff_summary
WHERE writeoff_date >= DATE_TRUNC('MONTH', CURRENT_DATE())
  AND writeoff_date <= CURRENT_DATE()
GROUP BY reason_code
ORDER BY writeoff_value DESC;

-- ============================================================================
-- CFO INVENTORY SUMMARY VIEW
-- Network-level inventory health metrics
-- ============================================================================

CREATE OR REPLACE VIEW vw_cfo_inventory_summary AS
SELECT
  SUM(soh_value) AS total_inventory_value,
  SUM(CASE WHEN is_dead_stock THEN soh_value ELSE 0 END) AS dead_stock_value,
  ROUND(SUM(CASE WHEN is_dead_stock THEN soh_value ELSE 0 END) /
    NULLIF(SUM(soh_value), 0) * 100, 2) AS dead_stock_pct,
  SUM(CASE WHEN is_out_of_stock AND is_tailored_in THEN 1 ELSE 0 END) AS oos_count,
  SUM(CASE WHEN days_until_oos <= 3 AND days_until_oos > 0 THEN 1 ELSE 0 END) AS oos_risk_3d_count,
  SUM(CASE WHEN days_of_stock > 30 THEN soh_value ELSE 0 END) AS overstock_value,
  ROUND(AVG(days_of_stock), 1) AS avg_days_of_stock,
  COUNT(DISTINCT store_id) AS store_count,
  COUNT(DISTINCT article_id) AS sku_count
FROM gold_inventory_health
WHERE is_tailored_in = TRUE;

-- ============================================================================
-- CFO DEAD STOCK BY CATEGORY VIEW
-- Dead stock breakdown by category
-- ============================================================================

CREATE OR REPLACE VIEW vw_cfo_dead_stock_by_category AS
SELECT
  category_name,
  COUNT(*) AS item_count,
  SUM(soh_value) AS dead_stock_value,
  SUM(soh_qty) AS dead_stock_qty,
  ROUND(AVG(days_since_last_sale), 0) AS avg_days_since_sale,
  SUM(CASE WHEN cluster_has_sales THEN 1 ELSE 0 END) AS items_selling_elsewhere
FROM gold_dead_stock
GROUP BY category_name
ORDER BY dead_stock_value DESC;

-- ============================================================================
-- CFO INVENTORY BY STOCK STATUS VIEW
-- Inventory breakdown by stock status
-- ============================================================================

CREATE OR REPLACE VIEW vw_cfo_inventory_by_status AS
SELECT
  CASE
    WHEN is_out_of_stock THEN 'Out of Stock'
    WHEN is_dead_stock THEN 'Dead Stock'
    WHEN days_of_stock < 3 THEN 'Critical (<3 days)'
    WHEN days_of_stock < 7 THEN 'Low (3-7 days)'
    WHEN days_of_stock > 30 THEN 'Overstock (>30 days)'
    ELSE 'Normal'
  END AS stock_status,
  COUNT(*) AS item_count,
  SUM(soh_value) AS inventory_value
FROM gold_inventory_health
WHERE is_tailored_in = TRUE
GROUP BY
  CASE
    WHEN is_out_of_stock THEN 'Out of Stock'
    WHEN is_dead_stock THEN 'Dead Stock'
    WHEN days_of_stock < 3 THEN 'Critical (<3 days)'
    WHEN days_of_stock < 7 THEN 'Low (3-7 days)'
    WHEN days_of_stock > 30 THEN 'Overstock (>30 days)'
    ELSE 'Normal'
  END
ORDER BY inventory_value DESC;

-- ============================================================================
-- VERIFY VIEWS CREATED
-- ============================================================================
SHOW VIEWS;
