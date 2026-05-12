-- ============================================================================
-- 7-Eleven Store Intelligence Demo - Gold Layer ETL (DLT Pipeline)
-- ============================================================================
-- This pipeline transforms Silver layer tables into Gold analytics tables
-- Using MATERIALIZED VIEWs for complex aggregations
-- ============================================================================

-- ============================================================================
-- GOLD_DAILY_STORE_SUMMARY
-- Daily KPIs per store with budget and cluster comparisons
-- ============================================================================
CREATE OR REFRESH MATERIALIZED VIEW gold_daily_store_summary
COMMENT "Daily store-level summary with KPIs, budget variance, and cluster comparisons"
AS
WITH daily_sales AS (
  SELECT
    s.store_id,
    st.store_code,
    st.store_name,
    st.state,
    st.cluster_id,
    sc.cluster_name,
    s.txn_date AS summary_date,
    s.day_of_week,
    s.is_weekend,
    SUM(s.revenue) AS total_sales,
    SUM(s.gross_profit) AS total_gp,
    SUM(s.cost) AS total_cost,
    SUM(s.units_sold) AS total_units,
    COUNT(DISTINCT s.txn_id) AS transaction_count
  FROM silver_sales_transactions s
  JOIN silver_stores st ON s.store_id = st.store_id
  LEFT JOIN silver_store_clusters sc ON st.cluster_id = sc.cluster_id
  GROUP BY ALL
),
with_budget AS (
  SELECT
    ds.*,
    b.budget_sales,
    b.budget_gp,
    CASE WHEN ds.transaction_count > 0
      THEN ds.total_sales / ds.transaction_count
      ELSE 0
    END AS avg_basket_value,
    CASE WHEN ds.transaction_count > 0
      THEN ds.total_units / ds.transaction_count
      ELSE 0
    END AS avg_basket_units,
    CASE WHEN ds.total_sales > 0
      THEN ROUND(ds.total_gp / ds.total_sales * 100, 2)
      ELSE 0
    END AS gp_margin_pct
  FROM daily_sales ds
  LEFT JOIN silver_budgets b
    ON ds.store_id = b.store_id
    AND b.period_type = 'DAILY'
    AND ds.summary_date BETWEEN b.period_start AND b.period_end
),
with_yoy AS (
  SELECT
    wb.*,
    DATE_SUB(wb.summary_date, 364) AS ly_date,
    ly.total_sales AS ly_sales,
    ly.total_gp AS ly_gp
  FROM with_budget wb
  LEFT JOIN daily_sales ly
    ON wb.store_id = ly.store_id
    AND ly.summary_date = DATE_SUB(wb.summary_date, 364)
),
cluster_avg AS (
  SELECT
    cluster_id,
    summary_date,
    AVG(total_sales) AS cluster_avg_sales
  FROM daily_sales
  GROUP BY cluster_id, summary_date
)
SELECT
  wy.store_id,
  wy.store_code,
  wy.store_name,
  wy.state,
  wy.cluster_id,
  wy.cluster_name,
  wy.summary_date,
  wy.day_of_week,
  wy.is_weekend,
  ROUND(wy.total_sales, 2) AS total_sales,
  ROUND(wy.total_gp, 2) AS total_gp,
  wy.gp_margin_pct,
  ROUND(wy.total_units, 2) AS total_units,
  ROUND(wy.total_cost, 2) AS total_cost,
  wy.transaction_count,
  ROUND(wy.avg_basket_value, 2) AS avg_basket_value,
  ROUND(wy.avg_basket_units, 2) AS avg_basket_units,
  wy.budget_sales,
  wy.budget_gp,
  ROUND(wy.total_sales - COALESCE(wy.budget_sales, 0), 2) AS sales_vs_budget,
  CASE WHEN wy.budget_sales > 0
    THEN ROUND((wy.total_sales - wy.budget_sales) / wy.budget_sales * 100, 2)
    ELSE NULL
  END AS sales_vs_budget_pct,
  ROUND(wy.total_gp - COALESCE(wy.budget_gp, 0), 2) AS gp_vs_budget,
  CASE WHEN wy.budget_gp > 0
    THEN ROUND((wy.total_gp - wy.budget_gp) / wy.budget_gp * 100, 2)
    ELSE NULL
  END AS gp_vs_budget_pct,
  wy.ly_date,
  wy.ly_sales,
  wy.ly_gp,
  CASE WHEN wy.ly_sales > 0
    THEN ROUND((wy.total_sales - wy.ly_sales) / wy.ly_sales * 100, 2)
    ELSE NULL
  END AS yoy_sales_growth,
  CASE WHEN wy.ly_gp > 0
    THEN ROUND((wy.total_gp - wy.ly_gp) / wy.ly_gp * 100, 2)
    ELSE NULL
  END AS yoy_gp_growth,
  ROUND(ca.cluster_avg_sales, 2) AS cluster_avg_sales,
  CASE WHEN ca.cluster_avg_sales > 0
    THEN ROUND((wy.total_sales - ca.cluster_avg_sales) / ca.cluster_avg_sales * 100, 2)
    ELSE NULL
  END AS vs_cluster_pct
FROM with_yoy wy
LEFT JOIN cluster_avg ca
  ON wy.cluster_id = ca.cluster_id
  AND wy.summary_date = ca.summary_date;


-- ============================================================================
-- GOLD_CATEGORY_PERFORMANCE
-- Category-level metrics with cluster benchmarking and outlier detection
-- ============================================================================
CREATE OR REFRESH MATERIALIZED VIEW gold_category_performance
COMMENT "Category performance metrics with YoY growth, budget variance, and cluster benchmarks"
AS
WITH weekly_sales AS (
  SELECT
    s.store_id,
    st.store_code,
    st.store_name,
    st.cluster_id,
    sc.cluster_name,
    c.category_id,
    c.category_name,
    c.subcategory,
    c.department,
    'WEEKLY' AS period_type,
    DATE_TRUNC('WEEK', s.txn_date) AS period_start,
    DATE_ADD(DATE_TRUNC('WEEK', s.txn_date), 6) AS period_end,
    SUM(s.revenue) AS total_sales,
    SUM(s.gross_profit) AS total_gp,
    SUM(s.units_sold) AS total_units,
    SUM(s.cost) AS total_cost
  FROM silver_sales_transactions s
  JOIN silver_stores st ON s.store_id = st.store_id
  JOIN silver_articles a ON s.article_id = a.article_id
  JOIN silver_categories c ON a.category_id = c.category_id
  LEFT JOIN silver_store_clusters sc ON st.cluster_id = sc.cluster_id
  GROUP BY ALL
),
store_totals AS (
  SELECT
    store_id,
    period_start,
    SUM(total_sales) AS store_total_sales,
    SUM(total_gp) AS store_total_gp,
    SUM(total_units) AS store_total_units
  FROM weekly_sales
  GROUP BY store_id, period_start
),
with_shares AS (
  SELECT
    ws.*,
    ROUND(ws.total_gp / NULLIF(ws.total_sales, 0) * 100, 2) AS gp_margin_pct,
    ROUND(ws.total_sales / NULLIF(stot.store_total_sales, 0) * 100, 2) AS sales_share_pct,
    ROUND(ws.total_gp / NULLIF(stot.store_total_gp, 0) * 100, 2) AS gp_share_pct,
    ROUND(ws.total_units / NULLIF(stot.store_total_units, 0) * 100, 2) AS units_share_pct
  FROM weekly_sales ws
  JOIN store_totals stot
    ON ws.store_id = stot.store_id
    AND ws.period_start = stot.period_start
),
with_yoy AS (
  SELECT
    curr.*,
    ly.total_sales AS ly_sales,
    ly.total_gp AS ly_gp,
    ly.total_units AS ly_units
  FROM with_shares curr
  LEFT JOIN weekly_sales ly
    ON curr.store_id = ly.store_id
    AND curr.category_id = ly.category_id
    AND ly.period_start = DATE_SUB(curr.period_start, 364)
),
cluster_stats AS (
  SELECT
    cluster_id,
    category_id,
    period_start,
    AVG(total_sales) AS cluster_avg_sales,
    AVG(total_gp) AS cluster_avg_gp,
    STDDEV(total_sales) AS cluster_std_dev_sales
  FROM weekly_sales
  GROUP BY cluster_id, category_id, period_start
)
SELECT
  wy.store_id,
  wy.store_code,
  wy.store_name,
  wy.cluster_id,
  wy.cluster_name,
  wy.category_id,
  wy.category_name,
  wy.subcategory,
  wy.department,
  wy.period_type,
  wy.period_start,
  wy.period_end,
  ROUND(wy.total_sales, 2) AS total_sales,
  ROUND(wy.total_gp, 2) AS total_gp,
  ROUND(wy.total_units, 2) AS total_units,
  ROUND(wy.total_cost, 2) AS total_cost,
  wy.gp_margin_pct,
  wy.sales_share_pct,
  wy.gp_share_pct,
  wy.units_share_pct,
  wy.ly_sales,
  wy.ly_gp,
  wy.ly_units,
  CASE WHEN wy.ly_sales > 0
    THEN ROUND((wy.total_sales - wy.ly_sales) / wy.ly_sales * 100, 2)
    ELSE NULL
  END AS yoy_sales_growth,
  CASE WHEN wy.ly_gp > 0
    THEN ROUND((wy.total_gp - wy.ly_gp) / wy.ly_gp * 100, 2)
    ELSE NULL
  END AS yoy_gp_growth,
  CASE WHEN wy.ly_units > 0
    THEN ROUND((wy.total_units - wy.ly_units) / wy.ly_units * 100, 2)
    ELSE NULL
  END AS yoy_units_growth,
  CASE
    WHEN wy.ly_gp > 0 AND wy.ly_sales > 0 THEN
      ROUND(
        ((wy.total_gp - wy.ly_gp) / wy.ly_gp * 100) -
        ((wy.total_sales - wy.ly_sales) / wy.ly_sales * 100), 2
      )
    ELSE NULL
  END AS gp_vs_sales_growth_diff,
  NULL AS budget_sales,
  NULL AS budget_gp,
  NULL AS sales_vs_budget_pct,
  NULL AS gp_vs_budget_pct,
  ROUND(cs.cluster_avg_sales, 2) AS cluster_avg_sales,
  ROUND(cs.cluster_avg_gp, 2) AS cluster_avg_gp,
  CASE WHEN cs.cluster_avg_sales > 0
    THEN ROUND((wy.total_sales - cs.cluster_avg_sales) / cs.cluster_avg_sales * 100, 2)
    ELSE NULL
  END AS vs_cluster_sales_pct,
  CASE WHEN cs.cluster_avg_gp > 0
    THEN ROUND((wy.total_gp - cs.cluster_avg_gp) / cs.cluster_avg_gp * 100, 2)
    ELSE NULL
  END AS vs_cluster_gp_pct,
  ROUND(cs.cluster_std_dev_sales, 2) AS cluster_std_dev_sales,
  CASE
    WHEN cs.cluster_std_dev_sales > 0 AND
         (wy.total_sales - cs.cluster_avg_sales) > cs.cluster_std_dev_sales
    THEN TRUE ELSE FALSE
  END AS is_growth_outlier,
  CASE
    WHEN cs.cluster_std_dev_sales > 0 AND
         (cs.cluster_avg_sales - wy.total_sales) > cs.cluster_std_dev_sales
    THEN TRUE ELSE FALSE
  END AS is_decline_outlier
FROM with_yoy wy
LEFT JOIN cluster_stats cs
  ON wy.cluster_id = cs.cluster_id
  AND wy.category_id = cs.category_id
  AND wy.period_start = cs.period_start;


-- ============================================================================
-- GOLD_ARTICLE_APSD
-- Article-level APSD (Average Per Store Per Day) with rankings
-- ============================================================================
CREATE OR REFRESH MATERIALIZED VIEW gold_article_apsd
COMMENT "Article APSD metrics with cluster benchmarks and multiple ranking dimensions"
AS
WITH article_weekly AS (
  SELECT
    s.store_id,
    st.store_code,
    st.store_name,
    st.cluster_id,
    sc.cluster_name,
    s.article_id,
    a.article_code,
    a.article_name,
    a.ean,
    c.category_id,
    c.category_name,
    c.subcategory,
    c.department,
    sl.layout_location,
    sl.shelf_position,
    sl.is_tailored_in,
    v.vendor_name,
    a.unit_cost,
    a.unit_price,
    a.margin_pct,
    'WEEKLY' AS period_type,
    DATE_TRUNC('WEEK', s.txn_date) AS period_start,
    DATE_ADD(DATE_TRUNC('WEEK', s.txn_date), 6) AS period_end,
    COUNT(DISTINCT s.txn_date) AS days_in_period,
    SUM(s.units_sold) AS total_units,
    SUM(s.revenue) AS total_sales,
    SUM(s.gross_profit) AS total_gp
  FROM silver_sales_transactions s
  JOIN silver_stores st ON s.store_id = st.store_id
  JOIN silver_articles a ON s.article_id = a.article_id
  JOIN silver_categories c ON a.category_id = c.category_id
  LEFT JOIN silver_store_clusters sc ON st.cluster_id = sc.cluster_id
  LEFT JOIN silver_store_layouts sl
    ON s.store_id = sl.store_id AND s.article_id = sl.article_id
  LEFT JOIN silver_vendors v ON a.vendor_id = v.vendor_id
  GROUP BY ALL
),
with_apsd AS (
  SELECT
    *,
    ROUND(total_units / NULLIF(days_in_period, 0), 4) AS apsd_units,
    ROUND(total_sales / NULLIF(days_in_period, 0), 4) AS apsd_sales,
    ROUND(total_gp / NULLIF(days_in_period, 0), 4) AS apsd_gp
  FROM article_weekly
),
cluster_apsd AS (
  SELECT
    cluster_id,
    article_id,
    period_start,
    AVG(apsd_units) AS cluster_apsd_units,
    AVG(apsd_sales) AS cluster_apsd_sales,
    AVG(apsd_gp) AS cluster_apsd_gp
  FROM with_apsd
  GROUP BY cluster_id, article_id, period_start
),
with_cluster AS (
  SELECT
    wa.*,
    ROUND(ca.cluster_apsd_units, 4) AS cluster_apsd_units,
    ROUND(ca.cluster_apsd_sales, 4) AS cluster_apsd_sales,
    ROUND(ca.cluster_apsd_gp, 4) AS cluster_apsd_gp,
    CASE WHEN ca.cluster_apsd_units > 0
      THEN ROUND((wa.apsd_units - ca.cluster_apsd_units) / ca.cluster_apsd_units * 100, 2)
      ELSE NULL
    END AS vs_cluster_apsd_pct
  FROM with_apsd wa
  LEFT JOIN cluster_apsd ca
    ON wa.cluster_id = ca.cluster_id
    AND wa.article_id = ca.article_id
    AND wa.period_start = ca.period_start
)
SELECT
  wc.*,
  ROW_NUMBER() OVER (PARTITION BY store_id, category_id, period_start ORDER BY apsd_units DESC) AS rank_in_category,
  ROW_NUMBER() OVER (PARTITION BY store_id, subcategory, period_start ORDER BY apsd_units DESC) AS rank_in_subcategory,
  ROW_NUMBER() OVER (PARTITION BY store_id, layout_location, period_start ORDER BY apsd_units DESC) AS rank_in_layout,
  ROW_NUMBER() OVER (PARTITION BY store_id, period_start ORDER BY apsd_units DESC) AS rank_in_store,
  ROW_NUMBER() OVER (PARTITION BY cluster_id, category_id, period_start ORDER BY cluster_apsd_units DESC) AS cluster_rank_in_category
FROM with_cluster wc;


-- ============================================================================
-- GOLD_INVENTORY_HEALTH
-- Current inventory status with days of stock and reorder recommendations
-- ============================================================================
CREATE OR REFRESH MATERIALIZED VIEW gold_inventory_health
COMMENT "Current inventory health with days of stock, OOS predictions, and reorder suggestions"
AS
WITH avg_daily_sales AS (
  SELECT
    store_id,
    article_id,
    AVG(units_sold) AS avg_daily_units,
    AVG(revenue) AS avg_daily_value,
    MAX(txn_date) AS last_sale_date,
    MAX(CASE WHEN txn_date = (SELECT MAX(txn_date) FROM silver_sales_transactions)
        THEN txn_hour ELSE NULL END) AS last_sale_hour
  FROM silver_sales_transactions
  WHERE txn_date >= DATE_SUB(CURRENT_DATE(), 28)
  GROUP BY store_id, article_id
),
with_health AS (
  SELECT
    i.store_id,
    st.store_code,
    st.store_name,
    st.cluster_id,
    i.article_id,
    a.article_code,
    a.article_name,
    a.ean,
    c.category_name,
    c.subcategory,
    c.department,
    sl.layout_location,
    v.vendor_name,
    sl.is_tailored_in,
    c.is_food_service,
    ROUND(i.soh_qty, 2) AS soh_qty,
    ROUND(i.soh_value, 2) AS soh_value,
    a.unit_cost,
    a.unit_price,
    ROUND(COALESCE(ads.avg_daily_units, 0), 4) AS avg_daily_sales_units,
    ROUND(COALESCE(ads.avg_daily_value, 0), 4) AS avg_daily_sales_value,
    CASE
      WHEN COALESCE(ads.avg_daily_units, 0) > 0
      THEN ROUND(i.soh_qty / ads.avg_daily_units, 2)
      ELSE 999
    END AS days_of_stock,
    ads.last_sale_date,
    ads.last_sale_hour,
    i.days_since_last_sale,
    i.last_receipt_date,
    i.first_oos_date,
    i.soh_qty <= 0 AS is_out_of_stock,
    (i.days_since_last_sale >= 28 AND i.soh_qty > 0) AS is_dead_stock,
    CASE
      WHEN COALESCE(ads.avg_daily_units, 0) > 0 AND i.soh_qty > 0
      THEN DATE_ADD(CURRENT_DATE(), CAST(FLOOR(i.soh_qty / ads.avg_daily_units) AS INT))
      ELSE NULL
    END AS projected_oos_date,
    a.case_size,
    a.min_order_qty,
    a.max_order_qty,
    v.lead_time_days
  FROM silver_inventory i
  JOIN silver_stores st ON i.store_id = st.store_id
  JOIN silver_articles a ON i.article_id = a.article_id
  JOIN silver_categories c ON a.category_id = c.category_id
  LEFT JOIN silver_store_layouts sl
    ON i.store_id = sl.store_id AND i.article_id = sl.article_id
  LEFT JOIN silver_vendors v ON a.vendor_id = v.vendor_id
  LEFT JOIN avg_daily_sales ads
    ON i.store_id = ads.store_id AND i.article_id = ads.article_id
)
SELECT
  wh.*,
  CASE
    WHEN projected_oos_date IS NOT NULL
    THEN DATEDIFF(projected_oos_date, CURRENT_DATE())
    ELSE NULL
  END AS days_until_oos,
  ROUND(avg_daily_sales_units * COALESCE(lead_time_days, 3), 2) AS reorder_point,
  CASE
    WHEN avg_daily_sales_units > 0 THEN
      GREATEST(
        COALESCE(min_order_qty, 1),
        LEAST(
          COALESCE(max_order_qty, 999),
          CEIL((avg_daily_sales_units * 7 - soh_qty) / COALESCE(NULLIF(case_size, 0), 1)) * COALESCE(case_size, 1)
        )
      )
    ELSE 0
  END AS suggested_reorder_qty,
  avg_daily_sales_units AS apsd_units,
  ROW_NUMBER() OVER (PARTITION BY store_id ORDER BY avg_daily_sales_units DESC) AS apsd_rank_in_store,
  CURRENT_TIMESTAMP() AS updated_at
FROM with_health wh;


-- ============================================================================
-- GOLD_DEAD_STOCK
-- Items with no sales in 28+ days but still have stock on hand
-- ============================================================================
CREATE OR REFRESH MATERIALIZED VIEW gold_dead_stock
COMMENT "Dead stock analysis - items with no sales in 28+ days with inventory on hand"
AS
WITH cluster_sales AS (
  SELECT
    st.cluster_id,
    s.article_id,
    SUM(s.units_sold) AS cluster_total_units_28d,
    AVG(s.units_sold) AS cluster_apsd_units,
    COUNT(DISTINCT s.store_id) AS stores_with_sales
  FROM silver_sales_transactions s
  JOIN silver_stores st ON s.store_id = st.store_id
  WHERE s.txn_date >= DATE_SUB(CURRENT_DATE(), 28)
  GROUP BY st.cluster_id, s.article_id
)
SELECT
  i.store_id,
  st.store_code,
  st.store_name,
  st.cluster_id,
  sc.cluster_name,
  i.article_id,
  a.article_code,
  a.article_name,
  a.ean,
  c.category_name,
  c.subcategory,
  c.department,
  sl.layout_location,
  v.vendor_name,
  sl.is_tailored_in,
  ROUND(i.soh_qty, 2) AS soh_qty,
  ROUND(i.soh_value, 2) AS soh_value,
  a.unit_cost,
  i.last_sale_date,
  i.days_since_last_sale,
  cs.stores_with_sales > 0 AS cluster_has_sales,
  ROUND(cs.cluster_apsd_units, 4) AS cluster_apsd_units,
  ROUND(cs.cluster_total_units_28d, 2) AS cluster_total_units_28d,
  ROW_NUMBER() OVER (PARTITION BY i.store_id ORDER BY i.soh_qty DESC) AS rank_by_soh_qty,
  ROW_NUMBER() OVER (PARTITION BY i.store_id ORDER BY i.soh_value DESC) AS rank_by_soh_value,
  CURRENT_TIMESTAMP() AS updated_at
FROM silver_inventory i
JOIN silver_stores st ON i.store_id = st.store_id
JOIN silver_articles a ON i.article_id = a.article_id
JOIN silver_categories c ON a.category_id = c.category_id
LEFT JOIN silver_store_clusters sc ON st.cluster_id = sc.cluster_id
LEFT JOIN silver_store_layouts sl
  ON i.store_id = sl.store_id AND i.article_id = sl.article_id
LEFT JOIN silver_vendors v ON a.vendor_id = v.vendor_id
LEFT JOIN cluster_sales cs ON st.cluster_id = cs.cluster_id AND i.article_id = cs.article_id
WHERE i.days_since_last_sale >= 28
  AND i.soh_qty > 0;


-- ============================================================================
-- GOLD_HOURLY_SALES
-- Hourly sales patterns for cook quantity recommendations
-- ============================================================================
CREATE OR REFRESH MATERIALIZED VIEW gold_hourly_sales
COMMENT "Hourly sales patterns by article for cook quantity optimization"
AS
WITH hourly_agg AS (
  SELECT
    s.store_id,
    st.store_code,
    st.store_name,
    s.article_id,
    a.article_code,
    a.article_name,
    c.category_name,
    c.subcategory,
    c.is_food_service,
    s.day_of_week,
    CASE s.day_of_week
      WHEN 1 THEN 'Monday'
      WHEN 2 THEN 'Tuesday'
      WHEN 3 THEN 'Wednesday'
      WHEN 4 THEN 'Thursday'
      WHEN 5 THEN 'Friday'
      WHEN 6 THEN 'Saturday'
      WHEN 7 THEN 'Sunday'
    END AS day_name,
    s.txn_hour AS hour_of_day,
    s.is_weekend,
    s.txn_hour BETWEEN 11 AND 14 AS is_lunch_peak,
    MIN(s.txn_date) AS period_start,
    MAX(s.txn_date) AS period_end,
    COUNT(DISTINCT DATE_TRUNC('WEEK', s.txn_date)) AS weeks_in_period,
    SUM(s.units_sold) AS total_units,
    SUM(s.revenue) AS total_sales,
    AVG(s.units_sold) AS avg_units,
    AVG(s.revenue) AS avg_sales,
    MIN(s.units_sold) AS min_units,
    MAX(s.units_sold) AS max_units,
    STDDEV(s.units_sold) AS std_dev_units
  FROM silver_sales_transactions s
  JOIN silver_stores st ON s.store_id = st.store_id
  JOIN silver_articles a ON s.article_id = a.article_id
  JOIN silver_categories c ON a.category_id = c.category_id
  GROUP BY ALL
),
daily_totals AS (
  SELECT
    store_id,
    article_id,
    day_of_week,
    SUM(total_units) AS daily_total_units
  FROM hourly_agg
  GROUP BY store_id, article_id, day_of_week
)
SELECT
  ha.*,
  ROUND(ha.total_units / NULLIF(dt.daily_total_units, 0) * 100, 2) AS pct_of_daily_units,
  CEIL(ha.avg_units + COALESCE(ha.std_dev_units, 0)) AS recommended_cook_qty,
  CASE
    WHEN ha.is_lunch_peak
    THEN CEIL((ha.avg_units + COALESCE(ha.std_dev_units, 0)) * 1.10)
    ELSE CEIL(ha.avg_units + COALESCE(ha.std_dev_units, 0))
  END AS recommended_cook_qty_growth
FROM hourly_agg ha
LEFT JOIN daily_totals dt
  ON ha.store_id = dt.store_id
  AND ha.article_id = dt.article_id
  AND ha.day_of_week = dt.day_of_week;


-- ============================================================================
-- GOLD_WRITEOFF_SUMMARY
-- Aggregated write-offs with cluster benchmarking and anomaly detection
-- ============================================================================
CREATE OR REFRESH MATERIALIZED VIEW gold_writeoff_summary
COMMENT "Write-off summary by category with cluster comparison and anomaly flags"
AS
WITH writeoff_agg AS (
  SELECT
    w.store_id,
    st.store_code,
    st.store_name,
    st.cluster_id,
    sc.cluster_name,
    w.writeoff_date,
    c.category_name,
    c.subcategory,
    c.department,
    w.reason_code,
    SUM(w.quantity) AS total_qty,
    SUM(w.value) AS total_value,
    COUNT(*) AS item_count
  FROM silver_write_offs w
  JOIN silver_stores st ON w.store_id = st.store_id
  JOIN silver_articles a ON w.article_id = a.article_id
  JOIN silver_categories c ON a.category_id = c.category_id
  LEFT JOIN silver_store_clusters sc ON st.cluster_id = sc.cluster_id
  GROUP BY ALL
),
cluster_stats AS (
  SELECT
    cluster_id,
    writeoff_date,
    category_name,
    reason_code,
    AVG(total_qty) AS cluster_avg_qty,
    AVG(total_value) AS cluster_avg_value,
    STDDEV(total_qty) AS cluster_std_dev_qty,
    STDDEV(total_value) AS cluster_std_dev_value
  FROM writeoff_agg
  GROUP BY cluster_id, writeoff_date, category_name, reason_code
)
SELECT
  wa.store_id,
  wa.store_code,
  wa.store_name,
  wa.cluster_id,
  wa.cluster_name,
  wa.writeoff_date,
  wa.category_name,
  wa.subcategory,
  wa.department,
  wa.reason_code,
  ROUND(wa.total_qty, 2) AS total_qty,
  ROUND(wa.total_value, 2) AS total_value,
  wa.item_count,
  ROUND(cs.cluster_avg_qty, 2) AS cluster_avg_qty,
  ROUND(cs.cluster_avg_value, 2) AS cluster_avg_value,
  ROUND(cs.cluster_std_dev_qty, 2) AS cluster_std_dev_qty,
  ROUND(cs.cluster_std_dev_value, 2) AS cluster_std_dev_value,
  CASE WHEN cs.cluster_avg_qty > 0
    THEN ROUND((wa.total_qty - cs.cluster_avg_qty) / cs.cluster_avg_qty * 100, 2)
    ELSE NULL
  END AS vs_cluster_qty_pct,
  CASE WHEN cs.cluster_avg_value > 0
    THEN ROUND((wa.total_value - cs.cluster_avg_value) / cs.cluster_avg_value * 100, 2)
    ELSE NULL
  END AS vs_cluster_value_pct,
  CASE WHEN cs.cluster_std_dev_qty > 0
    THEN ROUND((wa.total_qty - cs.cluster_avg_qty) / cs.cluster_std_dev_qty, 2)
    ELSE 0
  END AS std_dev_from_cluster,
  CASE
    WHEN cs.cluster_std_dev_qty > 0 AND
         ABS(wa.total_qty - cs.cluster_avg_qty) > cs.cluster_std_dev_qty
    THEN TRUE ELSE FALSE
  END AS is_anomaly,
  CASE
    WHEN cs.cluster_std_dev_qty > 0 AND
         (wa.total_qty - cs.cluster_avg_qty) > cs.cluster_std_dev_qty
    THEN 'HIGH'
    WHEN cs.cluster_std_dev_qty > 0 AND
         (cs.cluster_avg_qty - wa.total_qty) > cs.cluster_std_dev_qty
    THEN 'LOW'
    ELSE NULL
  END AS anomaly_direction
FROM writeoff_agg wa
LEFT JOIN cluster_stats cs
  ON wa.cluster_id = cs.cluster_id
  AND wa.writeoff_date = cs.writeoff_date
  AND wa.category_name = cs.category_name
  AND wa.reason_code = cs.reason_code;


-- ============================================================================
-- GOLD_WRITEOFF_DETAIL
-- Detailed write-off records enriched with article and team member info
-- ============================================================================
CREATE OR REFRESH MATERIALIZED VIEW gold_writeoff_detail
COMMENT "Detailed write-off records with enriched article and team member information"
AS
WITH cluster_article_avg AS (
  SELECT
    st.cluster_id,
    w.article_id,
    AVG(w.quantity) AS cluster_avg_qty
  FROM silver_write_offs w
  JOIN silver_stores st ON w.store_id = st.store_id
  WHERE w.writeoff_date >= DATE_SUB(CURRENT_DATE(), 28)
  GROUP BY st.cluster_id, w.article_id
)
SELECT
  w.writeoff_id,
  w.store_id,
  st.store_code,
  st.store_name,
  st.cluster_id,
  w.article_id,
  a.article_code,
  a.article_name,
  a.ean,
  c.category_name,
  c.subcategory,
  c.department,
  w.writeoff_date,
  w.writeoff_time,
  w.writeoff_hour,
  ROUND(w.quantity, 2) AS quantity,
  ROUND(w.value, 2) AS value,
  a.unit_cost,
  w.reason_code,
  w.reason_desc,
  COALESCE(w.team_member_name, tm.member_name) AS team_member_name,
  tm.role AS team_member_role,
  w.reason_code IN ('STORE_USE', 'SU', 'STAFF_MEAL') AS is_store_use,
  ROUND(caa.cluster_avg_qty, 2) AS cluster_avg_qty_for_article,
  CASE
    WHEN caa.cluster_avg_qty > 0 AND w.quantity > caa.cluster_avg_qty * 2
    THEN TRUE ELSE FALSE
  END AS is_anomaly_for_article
FROM silver_write_offs w
JOIN silver_stores st ON w.store_id = st.store_id
JOIN silver_articles a ON w.article_id = a.article_id
JOIN silver_categories c ON a.category_id = c.category_id
LEFT JOIN silver_team_members tm ON w.team_member_id = tm.member_id
LEFT JOIN cluster_article_avg caa
  ON st.cluster_id = caa.cluster_id AND w.article_id = caa.article_id;


-- ============================================================================
-- GOLD_WRITEOFF_RECONCILIATION
-- Purchase vs Sales vs Write-off variance analysis
-- ============================================================================
CREATE OR REFRESH MATERIALIZED VIEW gold_writeoff_reconciliation
COMMENT "Stock reconciliation showing purchase, sales, and write-off variance"
AS
WITH daily_activity AS (
  SELECT
    i.store_id,
    st.store_code,
    st.store_name,
    i.article_id,
    a.article_code,
    a.article_name,
    c.category_name,
    i.snapshot_date AS reconciliation_date,
    DAYOFWEEK(i.snapshot_date) AS day_of_week,
    CASE DAYOFWEEK(i.snapshot_date)
      WHEN 1 THEN 'Sunday'
      WHEN 2 THEN 'Monday'
      WHEN 3 THEN 'Tuesday'
      WHEN 4 THEN 'Wednesday'
      WHEN 5 THEN 'Thursday'
      WHEN 6 THEN 'Friday'
      WHEN 7 THEN 'Saturday'
    END AS day_name,
    i.soh_qty AS closing_stock,
    a.shelf_life_days
  FROM silver_inventory i
  JOIN silver_stores st ON i.store_id = st.store_id
  JOIN silver_articles a ON i.article_id = a.article_id
  JOIN silver_categories c ON a.category_id = c.category_id
),
purchases AS (
  SELECT store_id, article_id, receipt_date, SUM(qty_received) AS purchases_qty
  FROM silver_purchases
  GROUP BY store_id, article_id, receipt_date
),
sales AS (
  SELECT store_id, article_id, txn_date, SUM(units_sold) AS sales_qty
  FROM silver_sales_transactions
  GROUP BY store_id, article_id, txn_date
),
writeoffs AS (
  SELECT store_id, article_id, writeoff_date, SUM(quantity) AS writeoff_qty
  FROM silver_write_offs
  GROUP BY store_id, article_id, writeoff_date
),
writeoff_stats AS (
  SELECT store_id, article_id, AVG(writeoff_qty) AS avg_daily_writeoff, STDDEV(writeoff_qty) AS std_dev_writeoff
  FROM writeoffs WHERE writeoff_date >= DATE_SUB(CURRENT_DATE(), 28)
  GROUP BY store_id, article_id
)
SELECT
  da.store_id, da.store_code, da.store_name, da.article_id, da.article_code, da.article_name, da.category_name,
  da.reconciliation_date, da.day_of_week, da.day_name,
  ROUND(da.closing_stock - COALESCE(p.purchases_qty, 0) + COALESCE(s.sales_qty, 0) + COALESCE(w.writeoff_qty, 0), 2) AS opening_stock,
  ROUND(COALESCE(p.purchases_qty, 0), 2) AS purchases_qty,
  ROUND(COALESCE(s.sales_qty, 0), 2) AS sales_qty,
  ROUND(COALESCE(w.writeoff_qty, 0), 2) AS writeoff_qty,
  ROUND(da.closing_stock, 2) AS closing_stock,
  ROUND(COALESCE(ws.avg_daily_writeoff, 0), 2) AS expected_writeoff,
  ROUND(COALESCE(w.writeoff_qty, 0) - COALESCE(ws.avg_daily_writeoff, 0), 2) AS writeoff_variance,
  CASE WHEN ws.avg_daily_writeoff > 0
    THEN ROUND((COALESCE(w.writeoff_qty, 0) - ws.avg_daily_writeoff) / ws.avg_daily_writeoff * 100, 2)
    ELSE NULL
  END AS variance_pct,
  CASE WHEN ws.std_dev_writeoff > 0 AND ABS(COALESCE(w.writeoff_qty, 0) - ws.avg_daily_writeoff) > ws.std_dev_writeoff
    THEN TRUE ELSE FALSE
  END AS is_variance_anomaly,
  CASE
    WHEN COALESCE(w.writeoff_qty, 0) > COALESCE(ws.avg_daily_writeoff, 0) + COALESCE(ws.std_dev_writeoff, 0) THEN 'HIGH'
    WHEN COALESCE(w.writeoff_qty, 0) < COALESCE(ws.avg_daily_writeoff, 0) - COALESCE(ws.std_dev_writeoff, 0) THEN 'LOW'
    ELSE NULL
  END AS variance_direction,
  da.shelf_life_days,
  ROUND(ws.avg_daily_writeoff, 2) AS avg_daily_writeoff,
  ROUND(ws.std_dev_writeoff, 2) AS std_dev_writeoff
FROM daily_activity da
LEFT JOIN purchases p ON da.store_id = p.store_id AND da.article_id = p.article_id AND da.reconciliation_date = p.receipt_date
LEFT JOIN sales s ON da.store_id = s.store_id AND da.article_id = s.article_id AND da.reconciliation_date = s.txn_date
LEFT JOIN writeoffs w ON da.store_id = w.store_id AND da.article_id = w.article_id AND da.reconciliation_date = w.writeoff_date
LEFT JOIN writeoff_stats ws ON da.store_id = ws.store_id AND da.article_id = ws.article_id;


-- ============================================================================
-- GOLD_STORE_USE_COMPLIANCE
-- Tracking Store Use write-offs (e.g., milk for coffee machines)
-- ============================================================================
CREATE OR REFRESH MATERIALIZED VIEW gold_store_use_compliance
COMMENT "Store Use write-off compliance tracking"
AS
WITH store_use AS (
  SELECT
    w.store_id, st.store_code, st.store_name, w.writeoff_date AS compliance_date,
    DAYOFWEEK(w.writeoff_date) AS day_of_week,
    CASE DAYOFWEEK(w.writeoff_date) WHEN 1 THEN 'Sunday' WHEN 2 THEN 'Monday' WHEN 3 THEN 'Tuesday' WHEN 4 THEN 'Wednesday' WHEN 5 THEN 'Thursday' WHEN 6 THEN 'Friday' WHEN 7 THEN 'Saturday' END AS day_name,
    w.article_id, a.article_name, c.category_name,
    SUM(w.quantity) AS store_use_qty, SUM(w.value) AS store_use_value
  FROM silver_write_offs w
  JOIN silver_stores st ON w.store_id = st.store_id
  JOIN silver_articles a ON w.article_id = a.article_id
  JOIN silver_categories c ON a.category_id = c.category_id
  WHERE w.reason_code IN ('STORE_USE', 'SU', 'STAFF_MEAL')
  GROUP BY ALL
),
store_use_stats AS (
  SELECT store_id, article_id, AVG(store_use_qty) AS avg_daily_store_use, STDDEV(store_use_qty) AS std_dev_store_use
  FROM store_use GROUP BY store_id, article_id
)
SELECT
  su.*, su.store_use_qty > 0 AS has_store_use,
  ROUND(COALESCE(sus.avg_daily_store_use, 0), 2) AS avg_daily_store_use,
  ROUND(COALESCE(sus.std_dev_store_use, 0), 2) AS std_dev_store_use,
  su.store_use_qty = 0 AND sus.avg_daily_store_use > 0 AS is_missing,
  CASE WHEN sus.std_dev_store_use > 0 AND su.store_use_qty > sus.avg_daily_store_use + sus.std_dev_store_use THEN TRUE ELSE FALSE END AS is_outlier_high,
  CASE WHEN sus.std_dev_store_use > 0 AND su.store_use_qty < sus.avg_daily_store_use - sus.std_dev_store_use THEN TRUE ELSE FALSE END AS is_outlier_low,
  CASE WHEN sus.avg_daily_store_use > 0 THEN ROUND((su.store_use_qty - sus.avg_daily_store_use) / sus.avg_daily_store_use * 100, 2) ELSE NULL END AS deviation_from_avg
FROM store_use su
LEFT JOIN store_use_stats sus ON su.store_id = sus.store_id AND su.article_id = sus.article_id;


-- ============================================================================
-- GOLD_PRODUCT_LOOKUP
-- Denormalized article master for Genie natural language queries
-- ============================================================================
CREATE OR REFRESH MATERIALIZED VIEW gold_product_lookup
COMMENT "Denormalized product master for Genie natural language queries"
AS
SELECT
  a.article_id, a.article_code, a.article_name, a.ean, c.category_name, c.subcategory, c.department, c.layout_group,
  a.vendor_id, v.vendor_name, v.contact_email AS vendor_contact, v.delivery_days, v.lead_time_days,
  a.unit_cost, a.unit_price, a.margin_pct, a.purchase_margin_pct, ROUND(a.unit_price - a.unit_cost, 4) AS gp_per_unit,
  a.pack_qty, a.case_size, a.min_order_qty, a.max_order_qty, a.shelf_life_days, c.is_food_service, a.is_active,
  CURRENT_TIMESTAMP() AS updated_at
FROM silver_articles a
JOIN silver_categories c ON a.category_id = c.category_id
LEFT JOIN silver_vendors v ON a.vendor_id = v.vendor_id;


-- ============================================================================
-- GOLD_STORE_ALERTS
-- Pre-computed alerts for the Databricks App
-- ============================================================================
CREATE OR REFRESH MATERIALIZED VIEW gold_store_alerts
COMMENT "Pre-computed alerts for store operations dashboard"
AS
WITH oos_alerts AS (
  SELECT ROW_NUMBER() OVER (ORDER BY store_id, article_id) AS alert_id, store_id, store_code, CURRENT_DATE() AS alert_date, CURRENT_TIMESTAMP() AS alert_time,
    'OUT_OF_STOCK' AS alert_type, 'HIGH' AS alert_severity, CONCAT('OOS: ', article_name) AS alert_title,
    CONCAT(article_name, ' is out of stock. Last sale: ', COALESCE(CAST(last_sale_date AS STRING), 'N/A')) AS alert_message,
    article_id, article_name, category_name, soh_qty AS metric_value, 0 AS threshold_value, 'Order immediately or transfer from nearby store' AS action_recommended
  FROM gold_inventory_health WHERE is_out_of_stock = TRUE AND is_tailored_in = TRUE
),
projected_oos_alerts AS (
  SELECT ROW_NUMBER() OVER (ORDER BY store_id, days_until_oos) + 100000 AS alert_id, store_id, store_code, CURRENT_DATE() AS alert_date, CURRENT_TIMESTAMP() AS alert_time,
    'PROJECTED_OOS' AS alert_type, CASE WHEN days_until_oos <= 2 THEN 'HIGH' ELSE 'MEDIUM' END AS alert_severity, CONCAT('Low Stock: ', article_name) AS alert_title,
    CONCAT(article_name, ' will be OOS in ', days_until_oos, ' days. Current SOH: ', ROUND(soh_qty, 0)) AS alert_message,
    article_id, article_name, category_name, days_until_oos AS metric_value, 3 AS threshold_value, CONCAT('Reorder suggested qty: ', ROUND(suggested_reorder_qty, 0)) AS action_recommended
  FROM gold_inventory_health WHERE days_until_oos <= 3 AND days_until_oos > 0 AND is_tailored_in = TRUE
),
dead_stock_alerts AS (
  SELECT ROW_NUMBER() OVER (ORDER BY store_id, soh_value DESC) + 200000 AS alert_id, store_id, store_code, CURRENT_DATE() AS alert_date, CURRENT_TIMESTAMP() AS alert_time,
    'DEAD_STOCK' AS alert_type, 'LOW' AS alert_severity, CONCAT('Dead Stock: ', article_name) AS alert_title,
    CONCAT(article_name, ' - No sales for ', days_since_last_sale, ' days. Value: $', ROUND(soh_value, 2)) AS alert_message,
    article_id, article_name, category_name, soh_value AS metric_value, 28 AS threshold_value,
    CASE WHEN cluster_has_sales THEN 'Consider markdown or transfer' ELSE 'Review range - no cluster sales' END AS action_recommended
  FROM gold_dead_stock WHERE rank_by_soh_value <= 10
),
writeoff_anomaly_alerts AS (
  SELECT ROW_NUMBER() OVER (ORDER BY store_id, writeoff_date DESC) + 300000 AS alert_id, store_id, store_code, writeoff_date AS alert_date, CURRENT_TIMESTAMP() AS alert_time,
    'WRITEOFF_ANOMALY' AS alert_type, 'MEDIUM' AS alert_severity, CONCAT('High Write-off: ', category_name) AS alert_title,
    CONCAT(category_name, ' write-off $', ROUND(total_value, 2), ' is ', ROUND(ABS(std_dev_from_cluster), 1), ' std devs from cluster') AS alert_message,
    NULL AS article_id, NULL AS article_name, category_name, total_value AS metric_value, cluster_avg_value AS threshold_value,
    'Review write-off practices and compare to cluster stores' AS action_recommended
  FROM gold_writeoff_summary WHERE is_anomaly = TRUE AND anomaly_direction = 'HIGH' AND writeoff_date >= DATE_SUB(CURRENT_DATE(), 7)
)
SELECT *, FALSE AS is_acknowledged, NULL AS acknowledged_by, NULL AS acknowledged_at, CURRENT_TIMESTAMP() AS created_at, DATE_ADD(CURRENT_DATE(), 7) AS expires_at FROM oos_alerts
UNION ALL
SELECT *, FALSE AS is_acknowledged, NULL AS acknowledged_by, NULL AS acknowledged_at, CURRENT_TIMESTAMP() AS created_at, DATE_ADD(CURRENT_DATE(), 3) AS expires_at FROM projected_oos_alerts
UNION ALL
SELECT *, FALSE AS is_acknowledged, NULL AS acknowledged_by, NULL AS acknowledged_at, CURRENT_TIMESTAMP() AS created_at, DATE_ADD(CURRENT_DATE(), 14) AS expires_at FROM dead_stock_alerts
UNION ALL
SELECT *, FALSE AS is_acknowledged, NULL AS acknowledged_by, NULL AS acknowledged_at, CURRENT_TIMESTAMP() AS created_at, DATE_ADD(CURRENT_DATE(), 7) AS expires_at FROM writeoff_anomaly_alerts;
