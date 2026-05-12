-- ============================================================================
-- 7-Eleven Store Intelligence Demo - Metrics Views for Genie
-- ============================================================================
-- These views provide optimized metrics for Genie natural language queries
-- ============================================================================

-- ============================================================================
-- GOLD_METRICS
-- Unified metrics view combining all key dimensions and measures
-- Optimized for Genie Space queries
-- ============================================================================
CREATE OR REFRESH MATERIALIZED VIEW gold_metrics
COMMENT "Unified metrics view for Genie natural language queries - combines store, category, and article dimensions"
AS
WITH daily_metrics AS (
  SELECT
    s.store_id,
    st.store_name,
    st.state,
    st.cluster_id,
    sc.cluster_name,
    c.category_id,
    c.category_name,
    c.subcategory,
    c.department,
    s.article_id,
    a.article_name,
    a.ean,
    s.txn_date,
    s.day_of_week,
    s.is_weekend,
    SUM(s.revenue) AS total_sales,
    SUM(s.gross_profit) AS total_gp,
    SUM(s.cost) AS total_cost,
    SUM(s.units_sold) AS total_units,
    COUNT(DISTINCT s.txn_id) AS transaction_count
  FROM silver_sales_transactions s
  JOIN silver_stores st ON s.store_id = st.store_id
  JOIN silver_articles a ON s.article_id = a.article_id
  JOIN silver_categories c ON a.category_id = c.category_id
  LEFT JOIN silver_store_clusters sc ON st.cluster_id = sc.cluster_id
  GROUP BY ALL
)
SELECT
  store_id,
  store_name,
  state,
  cluster_id,
  cluster_name,
  category_id,
  category_name,
  subcategory,
  department,
  article_id,
  article_name,
  ean,
  txn_date,
  day_of_week,
  is_weekend,

  -- Core Metrics
  ROUND(total_sales, 2) AS total_sales,
  ROUND(total_gp, 2) AS total_gp,
  ROUND(total_cost, 2) AS total_cost,
  ROUND(total_units, 2) AS total_units,
  transaction_count,

  -- Calculated Metrics
  ROUND(total_gp / NULLIF(total_sales, 0) * 100, 2) AS gp_margin_pct,
  ROUND(total_units / NULLIF(transaction_count, 0), 2) AS avg_basket_units,
  ROUND(total_sales / NULLIF(transaction_count, 0), 2) AS avg_basket_value
FROM daily_metrics;


-- ============================================================================
-- GOLD_STORE_KPI_SUMMARY
-- Store-level KPI summary for quick lookups
-- ============================================================================
CREATE OR REFRESH MATERIALIZED VIEW gold_store_kpi_summary
COMMENT "Store-level KPI summary for dashboard and Genie queries"
AS
SELECT
  store_id,
  store_code,
  store_name,
  state,
  cluster_id,
  cluster_name,

  -- Today's metrics
  MAX(CASE WHEN summary_date = CURRENT_DATE() THEN total_sales END) AS today_sales,
  MAX(CASE WHEN summary_date = CURRENT_DATE() THEN total_gp END) AS today_gp,
  MAX(CASE WHEN summary_date = CURRENT_DATE() THEN gp_margin_pct END) AS today_gp_margin_pct,
  MAX(CASE WHEN summary_date = CURRENT_DATE() THEN sales_vs_budget_pct END) AS today_vs_budget_pct,
  MAX(CASE WHEN summary_date = CURRENT_DATE() THEN vs_cluster_pct END) AS today_vs_cluster_pct,

  -- Yesterday's metrics
  MAX(CASE WHEN summary_date = DATE_SUB(CURRENT_DATE(), 1) THEN total_sales END) AS yesterday_sales,
  MAX(CASE WHEN summary_date = DATE_SUB(CURRENT_DATE(), 1) THEN total_gp END) AS yesterday_gp,

  -- Week to date
  SUM(CASE WHEN summary_date >= DATE_TRUNC('WEEK', CURRENT_DATE()) THEN total_sales ELSE 0 END) AS wtd_sales,
  SUM(CASE WHEN summary_date >= DATE_TRUNC('WEEK', CURRENT_DATE()) THEN total_gp ELSE 0 END) AS wtd_gp,

  -- Month to date
  SUM(CASE WHEN summary_date >= DATE_TRUNC('MONTH', CURRENT_DATE()) THEN total_sales ELSE 0 END) AS mtd_sales,
  SUM(CASE WHEN summary_date >= DATE_TRUNC('MONTH', CURRENT_DATE()) THEN total_gp ELSE 0 END) AS mtd_gp,

  -- Last 7 days
  SUM(CASE WHEN summary_date >= DATE_SUB(CURRENT_DATE(), 7) THEN total_sales ELSE 0 END) AS l7d_sales,
  SUM(CASE WHEN summary_date >= DATE_SUB(CURRENT_DATE(), 7) THEN total_gp ELSE 0 END) AS l7d_gp,
  AVG(CASE WHEN summary_date >= DATE_SUB(CURRENT_DATE(), 7) THEN total_sales END) AS l7d_avg_daily_sales,

  -- Last 28 days
  SUM(CASE WHEN summary_date >= DATE_SUB(CURRENT_DATE(), 28) THEN total_sales ELSE 0 END) AS l28d_sales,
  SUM(CASE WHEN summary_date >= DATE_SUB(CURRENT_DATE(), 28) THEN total_gp ELSE 0 END) AS l28d_gp,
  AVG(CASE WHEN summary_date >= DATE_SUB(CURRENT_DATE(), 28) THEN total_sales END) AS l28d_avg_daily_sales,
  AVG(CASE WHEN summary_date >= DATE_SUB(CURRENT_DATE(), 28) THEN gp_margin_pct END) AS l28d_avg_gp_margin_pct,

  -- YoY growth (last 28 days)
  AVG(CASE WHEN summary_date >= DATE_SUB(CURRENT_DATE(), 28) THEN yoy_sales_growth END) AS l28d_avg_yoy_growth,

  -- Cluster comparison
  AVG(CASE WHEN summary_date >= DATE_SUB(CURRENT_DATE(), 28) THEN vs_cluster_pct END) AS l28d_avg_vs_cluster_pct

FROM gold_daily_store_summary
WHERE summary_date >= DATE_SUB(CURRENT_DATE(), 90)
GROUP BY store_id, store_code, store_name, state, cluster_id, cluster_name;


-- ============================================================================
-- GOLD_CATEGORY_RANKINGS
-- Category rankings within store for Genie queries
-- ============================================================================
CREATE OR REFRESH MATERIALIZED VIEW gold_category_rankings
COMMENT "Category rankings within store for Genie natural language queries"
AS
WITH category_l28d AS (
  SELECT
    store_id,
    store_code,
    store_name,
    category_id,
    category_name,
    subcategory,
    department,
    SUM(total_sales) AS l28d_sales,
    SUM(total_gp) AS l28d_gp,
    SUM(total_units) AS l28d_units,
    AVG(gp_margin_pct) AS avg_gp_margin_pct,
    AVG(yoy_sales_growth) AS avg_yoy_growth
  FROM gold_category_performance
  WHERE period_start >= DATE_SUB(CURRENT_DATE(), 28)
  GROUP BY store_id, store_code, store_name, category_id, category_name, subcategory, department
),
store_totals AS (
  SELECT
    store_id,
    SUM(l28d_sales) AS store_total_sales,
    SUM(l28d_gp) AS store_total_gp
  FROM category_l28d
  GROUP BY store_id
)
SELECT
  cl.*,
  ROUND(cl.l28d_sales / NULLIF(st.store_total_sales, 0) * 100, 2) AS sales_share_pct,
  ROUND(cl.l28d_gp / NULLIF(st.store_total_gp, 0) * 100, 2) AS gp_share_pct,
  ROW_NUMBER() OVER (PARTITION BY cl.store_id ORDER BY cl.l28d_sales DESC) AS rank_by_sales,
  ROW_NUMBER() OVER (PARTITION BY cl.store_id ORDER BY cl.l28d_gp DESC) AS rank_by_gp,
  ROW_NUMBER() OVER (PARTITION BY cl.store_id ORDER BY cl.l28d_units DESC) AS rank_by_units,
  ROW_NUMBER() OVER (PARTITION BY cl.store_id ORDER BY cl.avg_yoy_growth DESC) AS rank_by_growth
FROM category_l28d cl
JOIN store_totals st ON cl.store_id = st.store_id;


-- ============================================================================
-- GOLD_ARTICLE_RANKINGS
-- Article rankings within store for Genie queries
-- ============================================================================
CREATE OR REFRESH MATERIALIZED VIEW gold_article_rankings
COMMENT "Article rankings within store for Genie APSD queries"
AS
WITH article_l28d AS (
  SELECT
    store_id,
    store_code,
    store_name,
    cluster_id,
    article_id,
    article_code,
    article_name,
    ean,
    category_name,
    subcategory,
    department,
    is_tailored_in,
    SUM(total_units) AS l28d_units,
    SUM(total_sales) AS l28d_sales,
    SUM(total_gp) AS l28d_gp,
    AVG(apsd_units) AS avg_apsd_units,
    AVG(apsd_sales) AS avg_apsd_sales,
    AVG(cluster_apsd_units) AS avg_cluster_apsd_units,
    AVG(vs_cluster_apsd_pct) AS avg_vs_cluster_pct
  FROM gold_article_apsd
  WHERE period_start >= DATE_SUB(CURRENT_DATE(), 28)
  GROUP BY ALL
)
SELECT
  *,
  -- Store rankings
  ROW_NUMBER() OVER (PARTITION BY store_id ORDER BY avg_apsd_units DESC) AS rank_by_apsd,
  ROW_NUMBER() OVER (PARTITION BY store_id ORDER BY l28d_sales DESC) AS rank_by_sales,
  ROW_NUMBER() OVER (PARTITION BY store_id ORDER BY l28d_gp DESC) AS rank_by_gp,
  -- Category rankings
  ROW_NUMBER() OVER (PARTITION BY store_id, category_name ORDER BY avg_apsd_units DESC) AS rank_in_category,
  -- Subcategory rankings
  ROW_NUMBER() OVER (PARTITION BY store_id, subcategory ORDER BY avg_apsd_units DESC) AS rank_in_subcategory
FROM article_l28d;


-- ============================================================================
-- GOLD_INVENTORY_SUMMARY
-- Inventory summary for Genie queries
-- ============================================================================
CREATE OR REFRESH MATERIALIZED VIEW gold_inventory_summary
COMMENT "Inventory health summary for Genie queries"
AS
SELECT
  store_id,
  store_code,
  store_name,

  -- OOS counts
  COUNT(CASE WHEN is_out_of_stock THEN 1 END) AS oos_count,
  COUNT(CASE WHEN is_out_of_stock AND is_tailored_in THEN 1 END) AS oos_tailored_count,

  -- Projected OOS counts
  COUNT(CASE WHEN days_until_oos <= 1 THEN 1 END) AS projected_oos_1d_count,
  COUNT(CASE WHEN days_until_oos <= 3 THEN 1 END) AS projected_oos_3d_count,
  COUNT(CASE WHEN days_until_oos <= 7 THEN 1 END) AS projected_oos_7d_count,

  -- Dead stock
  COUNT(CASE WHEN is_dead_stock THEN 1 END) AS dead_stock_count,
  SUM(CASE WHEN is_dead_stock THEN soh_value ELSE 0 END) AS dead_stock_value,

  -- Total inventory
  COUNT(*) AS total_sku_count,
  SUM(soh_qty) AS total_soh_qty,
  SUM(soh_value) AS total_soh_value,

  -- Health metrics
  AVG(days_of_stock) AS avg_days_of_stock,
  SUM(CASE WHEN days_of_stock < 3 AND NOT is_out_of_stock THEN 1 ELSE 0 END) AS low_stock_count,
  SUM(CASE WHEN days_of_stock > 30 THEN 1 ELSE 0 END) AS overstock_count

FROM gold_inventory_health
GROUP BY store_id, store_code, store_name;


-- ============================================================================
-- GOLD_WRITEOFF_TRENDS
-- Write-off trends for Genie queries
-- ============================================================================
CREATE OR REFRESH MATERIALIZED VIEW gold_writeoff_trends
COMMENT "Write-off trends summary for Genie queries"
AS
SELECT
  store_id,
  store_code,
  store_name,
  cluster_id,
  cluster_name,

  -- Today
  SUM(CASE WHEN writeoff_date = CURRENT_DATE() THEN total_value ELSE 0 END) AS today_writeoff_value,
  SUM(CASE WHEN writeoff_date = CURRENT_DATE() THEN total_qty ELSE 0 END) AS today_writeoff_qty,

  -- Yesterday
  SUM(CASE WHEN writeoff_date = DATE_SUB(CURRENT_DATE(), 1) THEN total_value ELSE 0 END) AS yesterday_writeoff_value,

  -- Last 7 days
  SUM(CASE WHEN writeoff_date >= DATE_SUB(CURRENT_DATE(), 7) THEN total_value ELSE 0 END) AS l7d_writeoff_value,
  SUM(CASE WHEN writeoff_date >= DATE_SUB(CURRENT_DATE(), 7) THEN total_qty ELSE 0 END) AS l7d_writeoff_qty,
  AVG(CASE WHEN writeoff_date >= DATE_SUB(CURRENT_DATE(), 7) THEN total_value END) AS l7d_avg_daily_writeoff,

  -- Last 28 days
  SUM(CASE WHEN writeoff_date >= DATE_SUB(CURRENT_DATE(), 28) THEN total_value ELSE 0 END) AS l28d_writeoff_value,
  AVG(CASE WHEN writeoff_date >= DATE_SUB(CURRENT_DATE(), 28) THEN total_value END) AS l28d_avg_daily_writeoff,

  -- Cluster comparison (last 7 days)
  AVG(CASE WHEN writeoff_date >= DATE_SUB(CURRENT_DATE(), 7) THEN vs_cluster_value_pct END) AS l7d_vs_cluster_pct,

  -- Anomaly count (last 7 days)
  SUM(CASE WHEN writeoff_date >= DATE_SUB(CURRENT_DATE(), 7) AND is_anomaly THEN 1 ELSE 0 END) AS l7d_anomaly_count

FROM gold_writeoff_summary
WHERE writeoff_date >= DATE_SUB(CURRENT_DATE(), 90)
GROUP BY store_id, store_code, store_name, cluster_id, cluster_name;


-- ============================================================================
-- GOLD_COOK_QUANTITY_GUIDE
-- Hourly cook quantity recommendations for food service items
-- ============================================================================
CREATE OR REFRESH MATERIALIZED VIEW gold_cook_quantity_guide
COMMENT "Hourly cook quantity recommendations for food service items"
AS
SELECT
  store_id,
  store_code,
  store_name,
  article_id,
  article_code,
  article_name,
  category_name,
  subcategory,
  day_of_week,
  day_name,
  hour_of_day,
  is_weekend,
  is_lunch_peak,
  ROUND(avg_units, 2) AS avg_hourly_units,
  ROUND(std_dev_units, 2) AS std_dev_units,
  recommended_cook_qty,
  recommended_cook_qty_growth,
  ROUND(pct_of_daily_units, 2) AS pct_of_daily_units,
  -- Peak indicator
  CASE
    WHEN pct_of_daily_units >= 15 THEN 'HIGH'
    WHEN pct_of_daily_units >= 10 THEN 'MEDIUM'
    ELSE 'LOW'
  END AS demand_level
FROM gold_hourly_sales
WHERE is_food_service = TRUE
ORDER BY store_id, article_id, day_of_week, hour_of_day;
