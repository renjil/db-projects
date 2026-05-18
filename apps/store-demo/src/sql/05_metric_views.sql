-- Databricks notebook source
CREATE WIDGET TEXT catalog DEFAULT '';
CREATE WIDGET TEXT schema  DEFAULT '';

-- COMMAND ----------
-- ============================================================================
-- 7-Eleven Store Intelligence Demo - Metric Views for Genie & AI/BI
-- Catalog/Schema: passed in as ${catalog}.${schema}
-- ============================================================================
-- Semantic Metric Views using WITH METRICS LANGUAGE YAML syntax
-- These define business metrics for natural language queries in Genie
-- ============================================================================

USE CATALOG ${catalog};
USE SCHEMA ${schema};

-- ============================================================================
-- STORE SALES METRICS
-- Core store performance metrics for daily sales analysis
-- ============================================================================
CREATE OR REPLACE VIEW mv_store_sales
WITH METRICS LANGUAGE YAML AS $$
version: 1.1
comment: "Store-level sales and profitability metrics for 7-Eleven Australia"
source: ${catalog}.${schema}.gold_daily_store_summary

dimensions:
  - name: Store
    expr: store_name
    comment: "Store name"
  - name: Store ID
    expr: store_id
    comment: "Unique store identifier"
  - name: State
    expr: state
    comment: "Australian state/territory"
  - name: Cluster
    expr: cluster_name
    comment: "Store cluster for benchmarking"
  - name: Date
    expr: summary_date
    comment: "Transaction date"
  - name: Day of Week
    expr: day_of_week
    comment: "Day of week (1=Sunday, 7=Saturday)"
  - name: Day Name
    expr: "CASE day_of_week WHEN 1 THEN 'Sunday' WHEN 2 THEN 'Monday' WHEN 3 THEN 'Tuesday' WHEN 4 THEN 'Wednesday' WHEN 5 THEN 'Thursday' WHEN 6 THEN 'Friday' WHEN 7 THEN 'Saturday' END"
    comment: "Day name (Monday, Tuesday, etc.)"
  - name: Is Weekend
    expr: is_weekend
    comment: "Whether the day is a weekend"
  - name: Month
    expr: DATE_TRUNC('MONTH', summary_date)
    comment: "Month of the transaction"
  - name: Week
    expr: DATE_TRUNC('WEEK', summary_date)
    comment: "Week of the transaction"

measures:
  - name: Total Sales
    expr: SUM(total_sales)
    comment: "Total revenue in dollars"
  - name: Total GP
    expr: SUM(total_gp)
    comment: "Total gross profit in dollars"
  - name: Total Cost
    expr: SUM(total_cost)
    comment: "Total cost of goods sold"
  - name: Total Units
    expr: SUM(total_units)
    comment: "Total units sold"
  - name: Transaction Count
    expr: SUM(transaction_count)
    comment: "Number of transactions"
  - name: GP Margin %
    expr: ROUND(SUM(total_gp) / NULLIF(SUM(total_sales), 0) * 100, 2)
    comment: "Gross profit margin percentage"
  - name: Average Basket Value
    expr: ROUND(SUM(total_sales) / NULLIF(SUM(transaction_count), 0), 2)
    comment: "Average transaction value"
  - name: Average Basket Units
    expr: ROUND(SUM(total_units) / NULLIF(SUM(transaction_count), 0), 2)
    comment: "Average units per transaction"
  - name: Budget
    expr: SUM(budget_sales)
    comment: "Budgeted sales amount"
  - name: Sales vs Budget %
    expr: ROUND(SUM(total_sales) / NULLIF(SUM(budget_sales), 0) * 100, 2)
    comment: "Sales performance vs budget percentage"
  - name: YoY Sales Growth %
    expr: ROUND(AVG(yoy_sales_growth), 2)
    comment: "Year-over-year sales growth percentage"
  - name: Cluster Average Sales
    expr: AVG(cluster_avg_sales)
    comment: "Average sales for stores in the same cluster"
  - name: vs Cluster %
    expr: ROUND(AVG(vs_cluster_pct), 2)
    comment: "Performance vs cluster average percentage"
$$;


-- ============================================================================
-- CATEGORY PERFORMANCE METRICS
-- Category-level analysis for product mix optimization
-- ============================================================================
CREATE OR REPLACE VIEW mv_category_performance
WITH METRICS LANGUAGE YAML AS $$
version: 1.1
comment: "Category performance metrics for product mix analysis"
source: ${catalog}.${schema}.gold_category_performance

dimensions:
  - name: Store
    expr: store_name
    comment: "Store name"
  - name: Store ID
    expr: store_id
    comment: "Unique store identifier"
  - name: Category
    expr: category_name
    comment: "Product category name"
  - name: Subcategory
    expr: subcategory
    comment: "Product subcategory"
  - name: Department
    expr: department
    comment: "Product department"
  - name: Period Start
    expr: period_start
    comment: "Start of the analysis period"
  - name: Period End
    expr: period_end
    comment: "End of the analysis period"

measures:
  - name: Category Sales
    expr: SUM(total_sales)
    comment: "Total category sales in dollars"
  - name: Category GP
    expr: SUM(total_gp)
    comment: "Total category gross profit"
  - name: Category Units
    expr: SUM(total_units)
    comment: "Total category units sold"
  - name: Category GP Margin %
    expr: ROUND(SUM(total_gp) / NULLIF(SUM(total_sales), 0) * 100, 2)
    comment: "Category gross profit margin percentage"
  - name: Sales Share %
    expr: ROUND(AVG(sales_share_pct), 2)
    comment: "Category share of total store sales"
  - name: GP Share %
    expr: ROUND(AVG(gp_share_pct), 2)
    comment: "Category share of total store GP"
  - name: YoY Growth %
    expr: ROUND(AVG(yoy_sales_growth), 2)
    comment: "Year-over-year category growth"
  - name: vs Cluster %
    expr: ROUND(AVG(vs_cluster_sales_pct), 2)
    comment: "Category performance vs cluster average"
  - name: Cluster Avg Sales
    expr: AVG(cluster_avg_sales)
    comment: "Cluster average category sales"
$$;


-- ============================================================================
-- ARTICLE APSD METRICS
-- Article-level APSD (Average Per Store Per Day) analysis
-- ============================================================================
CREATE OR REPLACE VIEW mv_article_apsd
WITH METRICS LANGUAGE YAML AS $$
version: 1.1
comment: "Article APSD metrics for product performance analysis"
source: ${catalog}.${schema}.gold_article_apsd

dimensions:
  - name: Store
    expr: store_name
    comment: "Store name"
  - name: Store ID
    expr: store_id
    comment: "Unique store identifier"
  - name: Article
    expr: article_name
    comment: "Product/article name"
  - name: Article Code
    expr: article_code
    comment: "Product code/SKU"
  - name: EAN
    expr: ean
    comment: "Product barcode"
  - name: Category
    expr: category_name
    comment: "Product category"
  - name: Subcategory
    expr: subcategory
    comment: "Product subcategory"
  - name: Department
    expr: department
    comment: "Product department"
  - name: Is Tailored In
    expr: is_tailored_in
    comment: "Whether article is in store's approved range"
  - name: Period Start
    expr: period_start
    comment: "Analysis period start"

measures:
  - name: APSD Units
    expr: ROUND(AVG(apsd_units), 2)
    comment: "Average units sold per store per day"
  - name: APSD Sales
    expr: ROUND(AVG(apsd_sales), 2)
    comment: "Average sales per store per day in dollars"
  - name: Total Units
    expr: SUM(total_units)
    comment: "Total units sold in period"
  - name: Total Sales
    expr: SUM(total_sales)
    comment: "Total sales in period"
  - name: Total GP
    expr: SUM(total_gp)
    comment: "Total gross profit in period"
  - name: GP Margin %
    expr: ROUND(SUM(total_gp) / NULLIF(SUM(total_sales), 0) * 100, 2)
    comment: "Gross profit margin percentage"
  - name: Cluster APSD Units
    expr: ROUND(AVG(cluster_apsd_units), 2)
    comment: "Cluster average APSD units"
  - name: vs Cluster APSD %
    expr: ROUND(AVG(vs_cluster_apsd_pct), 2)
    comment: "APSD performance vs cluster average"
  - name: Days Sold
    expr: SUM(days_in_period)
    comment: "Number of days with sales"
$$;


-- ============================================================================
-- INVENTORY HEALTH METRICS
-- Stock levels, OOS, and dead stock analysis
-- ============================================================================
CREATE OR REPLACE VIEW mv_inventory_health
WITH METRICS LANGUAGE YAML AS $$
version: 1.1
comment: "Inventory health metrics for stock management"
source: ${catalog}.${schema}.gold_inventory_health

dimensions:
  - name: Store
    expr: store_name
    comment: "Store name"
  - name: Store ID
    expr: store_id
    comment: "Unique store identifier"
  - name: Article
    expr: article_name
    comment: "Product/article name"
  - name: Article Code
    expr: article_code
    comment: "Product code/SKU"
  - name: Category
    expr: category_name
    comment: "Product category"
  - name: Subcategory
    expr: subcategory
    comment: "Product subcategory"
  - name: Is Tailored In
    expr: is_tailored_in
    comment: "Whether article is in store's approved range"
  - name: Is Out of Stock
    expr: is_out_of_stock
    comment: "Whether item is currently OOS"
  - name: Is Dead Stock
    expr: is_dead_stock
    comment: "Whether item has no sales in 28+ days"
  - name: Stock Status
    expr: "CASE WHEN is_out_of_stock THEN 'Out of Stock' WHEN is_dead_stock THEN 'Dead Stock' WHEN days_of_stock < 3 THEN 'Low Stock' WHEN days_of_stock > 30 THEN 'Overstock' ELSE 'Normal' END"
    comment: "Current stock status category"

measures:
  - name: SOH Qty
    expr: SUM(soh_qty)
    comment: "Stock on hand quantity"
  - name: SOH Value
    expr: SUM(soh_value)
    comment: "Stock on hand value in dollars"
  - name: Days of Stock
    expr: ROUND(AVG(days_of_stock), 1)
    comment: "Average days of stock remaining"
  - name: OOS Count
    expr: SUM(CASE WHEN is_out_of_stock THEN 1 ELSE 0 END)
    comment: "Number of out-of-stock items"
  - name: OOS Tailored Count
    expr: SUM(CASE WHEN is_out_of_stock AND is_tailored_in THEN 1 ELSE 0 END)
    comment: "OOS items in approved range"
  - name: Dead Stock Count
    expr: SUM(CASE WHEN is_dead_stock THEN 1 ELSE 0 END)
    comment: "Number of dead stock items"
  - name: Dead Stock Value
    expr: SUM(CASE WHEN is_dead_stock THEN soh_value ELSE 0 END)
    comment: "Value of dead stock in dollars"
  - name: Low Stock Count
    expr: SUM(CASE WHEN days_of_stock < 3 AND NOT is_out_of_stock THEN 1 ELSE 0 END)
    comment: "Items with less than 3 days of stock"
  - name: Projected OOS 3 Days
    expr: SUM(CASE WHEN days_until_oos <= 3 THEN 1 ELSE 0 END)
    comment: "Items projected to be OOS within 3 days"
  - name: SKU Count
    expr: COUNT(*)
    comment: "Total number of SKUs"
$$;


-- ============================================================================
-- WRITE-OFF METRICS
-- Shrinkage and waste analysis
-- ============================================================================
CREATE OR REPLACE VIEW mv_writeoffs
WITH METRICS LANGUAGE YAML AS $$
version: 1.1
comment: "Write-off and shrinkage metrics for waste management"
source: ${catalog}.${schema}.gold_writeoff_summary

dimensions:
  - name: Store
    expr: store_name
    comment: "Store name"
  - name: Store ID
    expr: store_id
    comment: "Unique store identifier"
  - name: Cluster
    expr: cluster_name
    comment: "Store cluster for benchmarking"
  - name: Category
    expr: category_name
    comment: "Product category"
  - name: Subcategory
    expr: subcategory
    comment: "Product subcategory"
  - name: Reason Code
    expr: reason_code
    comment: "Write-off reason code"
  - name: Reason Description
    expr: reason_code
    comment: "Write-off reason description"
  - name: Date
    expr: writeoff_date
    comment: "Write-off date"
  - name: Month
    expr: DATE_TRUNC('MONTH', writeoff_date)
    comment: "Write-off month"
  - name: Week
    expr: DATE_TRUNC('WEEK', writeoff_date)
    comment: "Write-off week"
  - name: Is Anomaly
    expr: is_anomaly
    comment: "Whether write-off is flagged as anomaly"

measures:
  - name: Write-off Value
    expr: SUM(total_value)
    comment: "Total write-off value in dollars"
  - name: Write-off Qty
    expr: SUM(total_qty)
    comment: "Total write-off quantity"
  - name: Write-off Cost
    expr: SUM(total_value)
    comment: "Total write-off cost"
  - name: Cluster Avg Write-off
    expr: AVG(cluster_avg_value)
    comment: "Cluster average write-off value"
  - name: vs Cluster %
    expr: ROUND(AVG(vs_cluster_value_pct), 2)
    comment: "Write-off vs cluster average percentage"
  - name: Anomaly Count
    expr: SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END)
    comment: "Number of anomaly write-offs"
  - name: Anomaly Value
    expr: SUM(CASE WHEN is_anomaly THEN total_value ELSE 0 END)
    comment: "Value of anomaly write-offs"
  - name: Std Dev from Cluster
    expr: ROUND(AVG(std_dev_from_cluster), 2)
    comment: "Standard deviations from cluster average"
$$;


-- ============================================================================
-- HOURLY SALES METRICS
-- Time-of-day analysis for cook quantity planning
-- ============================================================================
CREATE OR REPLACE VIEW mv_hourly_sales
WITH METRICS LANGUAGE YAML AS $$
version: 1.1
comment: "Hourly sales patterns for food service cook quantity planning"
source: ${catalog}.${schema}.gold_hourly_sales

filter: is_food_service = true

dimensions:
  - name: Store
    expr: store_name
    comment: "Store name"
  - name: Store ID
    expr: store_id
    comment: "Unique store identifier"
  - name: Article
    expr: article_name
    comment: "Food service article name"
  - name: Category
    expr: category_name
    comment: "Product category"
  - name: Subcategory
    expr: subcategory
    comment: "Product subcategory (e.g., Pies, Sausage Rolls)"
  - name: Day of Week
    expr: day_of_week
    comment: "Day of week (1=Sunday)"
  - name: Day Name
    expr: "CASE day_of_week WHEN 1 THEN 'Sunday' WHEN 2 THEN 'Monday' WHEN 3 THEN 'Tuesday' WHEN 4 THEN 'Wednesday' WHEN 5 THEN 'Thursday' WHEN 6 THEN 'Friday' WHEN 7 THEN 'Saturday' END"
    comment: "Day name"
  - name: Hour
    expr: hour_of_day
    comment: "Hour of day (0-23)"
  - name: Is Weekend
    expr: is_weekend
    comment: "Whether it's a weekend day"
  - name: Is Lunch Peak
    expr: is_lunch_peak
    comment: "Whether it's lunch peak hour (11am-2pm)"
  - name: Time Period
    expr: "CASE WHEN hour_of_day BETWEEN 6 AND 10 THEN 'Morning' WHEN hour_of_day BETWEEN 11 AND 14 THEN 'Lunch' WHEN hour_of_day BETWEEN 15 AND 17 THEN 'Afternoon' WHEN hour_of_day BETWEEN 18 AND 21 THEN 'Evening' ELSE 'Night' END"
    comment: "Time period of day"

measures:
  - name: Avg Hourly Units
    expr: ROUND(AVG(avg_units), 2)
    comment: "Average units sold per hour"
  - name: Recommended Cook Qty
    expr: ROUND(AVG(recommended_cook_qty), 0)
    comment: "Recommended cook quantity (avg + 1 std dev)"
  - name: Cook Qty with Growth
    expr: ROUND(AVG(recommended_cook_qty_growth), 0)
    comment: "Recommended cook qty with 10% growth buffer"
  - name: "% of Daily Units"
    expr: ROUND(AVG(pct_of_daily_units), 2)
    comment: "Percentage of daily units sold in this hour"
  - name: Std Dev Units
    expr: ROUND(AVG(std_dev_units), 2)
    comment: "Standard deviation of hourly units"
  - name: Max Hourly Units
    expr: MAX(max_units)
    comment: "Maximum units sold in an hour"
$$;


-- ============================================================================
-- STORE ALERTS METRICS
-- Pre-computed alerts for operational issues
-- ============================================================================
CREATE OR REPLACE VIEW mv_store_alerts
WITH METRICS LANGUAGE YAML AS $$
version: 1.1
comment: "Store operational alerts for proactive management"
source: ${catalog}.${schema}.gold_store_alerts

dimensions:
  - name: Store ID
    expr: store_id
    comment: "Store identifier (alerts table has no store_name)"
  - name: Alert Type
    expr: alert_type
    comment: "Type of alert (OOS, Projected OOS, Dead Stock, Write-off Anomaly)"
  - name: Severity
    expr: alert_severity
    comment: "Alert severity (Critical, High, Medium, Low)"
  - name: Category
    expr: category_name
    comment: "Affected product category"
  - name: Article
    expr: article_name
    comment: "Affected article name"
  - name: Alert Date
    expr: alert_date
    comment: "Date alert was generated"

measures:
  - name: Alert Count
    expr: COUNT(*)
    comment: "Total number of alerts"
  - name: Critical Alerts
    expr: SUM(CASE WHEN alert_severity = 'Critical' THEN 1 ELSE 0 END)
    comment: "Number of critical alerts"
  - name: High Alerts
    expr: SUM(CASE WHEN alert_severity = 'High' THEN 1 ELSE 0 END)
    comment: "Number of high severity alerts"
  - name: OOS Alerts
    expr: SUM(CASE WHEN alert_type = 'OOS' THEN 1 ELSE 0 END)
    comment: "Out of stock alerts"
  - name: Projected OOS Alerts
    expr: SUM(CASE WHEN alert_type = 'Projected OOS' THEN 1 ELSE 0 END)
    comment: "Projected out of stock alerts"
  - name: Dead Stock Alerts
    expr: SUM(CASE WHEN alert_type = 'Dead Stock' THEN 1 ELSE 0 END)
    comment: "Dead stock alerts"
  - name: Writeoff Anomaly Alerts
    expr: SUM(CASE WHEN alert_type = 'Write-off Anomaly' THEN 1 ELSE 0 END)
    comment: "Write-off anomaly alerts"
  - name: Alert Value
    expr: SUM(metric_value)
    comment: "Total monetary value of alerts"
$$;


-- ============================================================================
-- VERIFICATION
-- ============================================================================
-- After running, verify metric views are created:
-- SHOW VIEWS IN ${catalog}.${schema} LIKE 'mv_%';
