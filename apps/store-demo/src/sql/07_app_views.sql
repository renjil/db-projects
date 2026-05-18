-- Databricks notebook source
CREATE WIDGET TEXT catalog DEFAULT '';
CREATE WIDGET TEXT schema  DEFAULT '';

-- COMMAND ----------
-- ============================================================================
-- App-compat views
-- ============================================================================
-- The Streamlit app queries three table names that the older iteration of
-- this demo created. The current DLT pipeline produces equivalent data under
-- different names, so we wrap them as views the app expects:
--
--   gold_store_kpi_override  → gold_store_kpi_summary  (1:1 passthrough)
--   gold_product_performance → gold_article_apsd       (column rename / derive)
--   gold_budget_tracking     → gold_daily_store_summary aggregated by period
-- ============================================================================

USE CATALOG ${catalog};
USE SCHEMA  ${schema};

-- COMMAND ----------
CREATE OR REPLACE VIEW gold_store_kpi_override AS
SELECT * FROM gold_store_kpi_summary;

-- COMMAND ----------
CREATE OR REPLACE VIEW gold_product_performance AS
SELECT
  store_id,
  store_code,
  store_name,
  category_name,
  subcategory,
  article_id,
  article_name,
  total_units AS total_qty,
  total_sales,
  total_gp,
  ROUND(total_gp / NULLIF(total_sales, 0) * 100, 2) AS gp_margin_pct,
  apsd_sales AS apsd,
  apsd_units,
  rank_in_store,
  rank_in_category
FROM gold_article_apsd;

-- COMMAND ----------
CREATE OR REPLACE VIEW gold_budget_tracking AS
SELECT
  store_id,
  store_name,
  state,
  'L7D' AS period_type,
  ROUND(SUM(total_sales), 2) AS actual_sales,
  ROUND(SUM(budget_sales), 2) AS budget_sales,
  CASE WHEN SUM(budget_sales) > 0
       THEN ROUND(SUM(total_sales) / SUM(budget_sales) * 100, 2)
       ELSE NULL END AS actual_vs_budget_pct,
  ROUND(SUM(ly_sales), 2) AS ly_sales,
  CASE WHEN SUM(ly_sales) > 0
       THEN ROUND((SUM(total_sales) - SUM(ly_sales)) / SUM(ly_sales) * 100, 2)
       ELSE NULL END AS actual_vs_ly_pct
FROM gold_daily_store_summary
WHERE summary_date >= CURRENT_DATE() - 7
GROUP BY store_id, store_name, state

UNION ALL

SELECT
  store_id,
  store_name,
  state,
  'L28D' AS period_type,
  ROUND(SUM(total_sales), 2) AS actual_sales,
  ROUND(SUM(budget_sales), 2) AS budget_sales,
  CASE WHEN SUM(budget_sales) > 0
       THEN ROUND(SUM(total_sales) / SUM(budget_sales) * 100, 2)
       ELSE NULL END AS actual_vs_budget_pct,
  ROUND(SUM(ly_sales), 2) AS ly_sales,
  CASE WHEN SUM(ly_sales) > 0
       THEN ROUND((SUM(total_sales) - SUM(ly_sales)) / SUM(ly_sales) * 100, 2)
       ELSE NULL END AS actual_vs_ly_pct
FROM gold_daily_store_summary
WHERE summary_date >= CURRENT_DATE() - 28
GROUP BY store_id, store_name, state;

