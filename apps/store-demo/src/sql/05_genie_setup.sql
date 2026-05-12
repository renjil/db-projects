-- ============================================================================
-- 7-Eleven Store Intelligence Demo - Genie Space Setup
-- ============================================================================
-- Adds table COMMENTs that Genie reads to understand the data model.
-- The Genie Space itself is created via the Databricks UI or REST API
-- (see the API reference block at the bottom of this file).
--
-- Parameters: ${catalog}, ${schema}  (set by the Databricks SQL API call)
-- ============================================================================

USE CATALOG ${catalog};
USE SCHEMA ${schema};

/*
GENIE SPACE CONFIGURATION
=========================

Space Name: 7-Eleven Store Assistant

Connected Tables (9 Gold tables):
---------------------------------
1. ${catalog}.${schema}.gold_daily_store_summary
2. ${catalog}.${schema}.gold_category_performance
3. ${catalog}.${schema}.gold_article_apsd
4. ${catalog}.${schema}.gold_inventory_health
5. ${catalog}.${schema}.gold_dead_stock
6. ${catalog}.${schema}.gold_hourly_sales
7. ${catalog}.${schema}.gold_writeoff_summary
8. ${catalog}.${schema}.gold_writeoff_detail
9. ${catalog}.${schema}.gold_product_lookup

Additional Views for Optimized Queries:
---------------------------------------
10. ${catalog}.${schema}.gold_metrics
11. ${catalog}.${schema}.gold_store_kpi_summary
12. ${catalog}.${schema}.gold_category_rankings
13. ${catalog}.${schema}.gold_article_rankings
14. ${catalog}.${schema}.gold_inventory_summary
15. ${catalog}.${schema}.gold_writeoff_trends
16. ${catalog}.${schema}.gold_cook_quantity_guide
17. ${catalog}.${schema}.gold_store_alerts
*/

-- Instructions to paste into Genie Space configuration:
/*
You are a store operations assistant for 7-Eleven Australia.

## Key Business Terms
- **APSD** = Average Per Store Per Day (units or $)
- **GP** = Gross Profit (Revenue - Cost)
- **SOH** = Stock on Hand (current inventory quantity)
- **Dead stock** = No sales in 28+ days with inventory still on hand
- **Cluster** = Group of comparable stores in the same State/Territory
- **Tailored in** = Article/product in the store's approved product range
- **Store Use** = Write-off reason code for items used in-store (e.g., milk for coffee)
- **OOS** = Out of Stock
- **WTD** = Week to Date
- **MTD** = Month to Date
- **L28D** = Last 28 Days
- **YoY** = Year over Year comparison

## Data Model Reference
- Store hierarchy: State > Cluster > Store
- Product hierarchy: Department > Category > Subcategory > Article
- Time periods: Daily, Weekly, Monthly, YTD
- Key metrics: Sales ($), GP ($), GP Margin (%), Units, APSD

## Query Defaults
- Default to user's accessible stores unless a specific store is mentioned
- Default time range: last 4 weeks (28 days) unless specified
- Compare to State Cluster averages for benchmarking
- Flag anomalies when >1 standard deviation from cluster average
- For rankings, show top 10 unless specified otherwise

## Response Guidelines
- Be concise and actionable - store managers are busy
- Include metric values (not just descriptions) in rankings
- Always specify the time period in responses
- For cook quantities, add 10% buffer for lunch peak hours (11am-2pm)
- Include reason codes when discussing write-offs
- Highlight anomalies with specific deviation from cluster
- Suggest actions where appropriate (reorder, markdown, transfer)

## Common Question Patterns
1. Sales/GP questions: Use gold_daily_store_summary or gold_store_kpi_summary
2. Category analysis: Use gold_category_performance or gold_category_rankings
3. Product/APSD questions: Use gold_article_apsd or gold_article_rankings
4. Inventory questions: Use gold_inventory_health or gold_inventory_summary
5. Dead stock questions: Use gold_dead_stock
6. Write-off questions: Use gold_writeoff_summary, gold_writeoff_detail, or gold_writeoff_trends
7. Cook quantity questions: Use gold_cook_quantity_guide or gold_hourly_sales
8. Product lookup: Use gold_product_lookup
9. Alerts: Use gold_store_alerts

## Example Queries to Learn From

-- "What were my sales yesterday?"
SELECT store_name, total_sales, total_gp, gp_margin_pct
FROM gold_daily_store_summary
WHERE summary_date = CURRENT_DATE() - 1;

-- "Top 10 selling articles by APSD"
SELECT article_name, category_name, avg_apsd_units, l28d_sales
FROM gold_article_rankings
WHERE rank_by_apsd <= 10
ORDER BY rank_by_apsd;

-- "Show me dead stock in Hot Food"
SELECT article_name, soh_qty, soh_value, days_since_last_sale
FROM gold_dead_stock
WHERE category_name = 'Hot Food'
ORDER BY soh_value DESC;

-- "How many meat pies should I cook tomorrow at 12pm?"
SELECT article_name, recommended_cook_qty_growth AS cook_qty
FROM gold_cook_quantity_guide
WHERE subcategory = 'Pies'
  AND day_of_week = DAYOFWEEK(CURRENT_DATE() + 1)
  AND hour_of_day = 12;
*/

-- ============================================================================
-- SAMPLE QUESTIONS FOR GENIE SPACE
-- ============================================================================
-- Add these as sample questions in the Genie Space configuration

/*
SAMPLE QUESTIONS
================

Sales & Performance:
1. "What were my sales yesterday?"
2. "How am I tracking against budget this week?"
3. "Which categories have the highest sales this month?"
4. "Show me my YoY growth trend"
5. "How do I compare to other stores in my cluster?"

Product Analysis:
6. "Show me my top 10 selling articles by APSD"
7. "Which products have declining sales vs last year?"
8. "What are my highest margin products?"
9. "List products that sell better in my cluster than my store"

Inventory:
10. "What items should I reorder today?"
11. "Show me my projected out-of-stock items"
12. "List dead stock in Hot Food ranked by cost"
13. "What's my total dead stock value?"
14. "Which items have less than 3 days of stock?"

Write-offs:
15. "What were my write-offs yesterday?"
16. "Am I writing off more than other stores in my cluster?"
17. "Show me write-off anomalies this week"
18. "What's my write-off trend for the last 4 weeks?"
19. "List write-offs by reason code"

Food Service Operations:
20. "How many meat pies should I cook each hour tomorrow?"
21. "What's my recommended cook quantity for lunch peak?"
22. "Show me hourly sales patterns for Hot Food"
23. "Which food service items have the highest waste?"

Alerts:
24. "What alerts do I have today?"
25. "Show me critical alerts"
26. "List all my out-of-stock items"
*/

-- ============================================================================
-- TABLE DESCRIPTIONS FOR GENIE
-- ============================================================================
-- These COMMENTs help Genie understand the data model.
-- Resolved against the catalog/schema set in the USE statements above.

COMMENT ON TABLE gold_daily_store_summary IS
'Daily store-level KPIs including sales, GP, margin, budget variance, YoY growth, and cluster comparison. Use for daily performance questions.';

COMMENT ON TABLE gold_category_performance IS
'Weekly category-level metrics with sales share, YoY growth, and cluster benchmarks. Use for category analysis questions.';

COMMENT ON TABLE gold_article_apsd IS
'Article-level APSD (Average Per Store Per Day) with rankings by category, subcategory, and store. Use for product performance and ranking questions.';

COMMENT ON TABLE gold_inventory_health IS
'Current inventory status including SOH, days of stock, OOS flags, projected OOS, and reorder suggestions. Use for inventory and reorder questions.';

COMMENT ON TABLE gold_dead_stock IS
'Items with no sales in 28+ days but still have stock on hand. Includes cluster comparison and rankings by value. Use for dead stock analysis.';

COMMENT ON TABLE gold_hourly_sales IS
'Hourly sales patterns by article and day of week with cook quantity recommendations. Use for food service operations and cook quantity questions.';

COMMENT ON TABLE gold_writeoff_summary IS
'Aggregated write-offs by category with cluster comparison and anomaly detection. Use for write-off analysis questions.';

COMMENT ON TABLE gold_writeoff_detail IS
'Detailed write-off records with article info, reason codes, and team member. Use for specific write-off investigation.';

COMMENT ON TABLE gold_product_lookup IS
'Denormalized product master with vendor info, pricing, and shelf life. Use for product lookup and supplier questions.';

COMMENT ON TABLE gold_store_alerts IS
'Pre-computed alerts for OOS, projected OOS, dead stock, and write-off anomalies. Use for alert questions.';

COMMENT ON TABLE gold_metrics IS
'Unified metrics view combining store, category, and article dimensions. Optimized for flexible Genie queries.';

COMMENT ON TABLE gold_store_kpi_summary IS
'Store-level KPI summary with today, yesterday, WTD, MTD, L7D, L28D metrics. Use for quick store performance overview.';

COMMENT ON TABLE gold_category_rankings IS
'Category rankings within each store with sales share and growth metrics. Use for category comparison questions.';

COMMENT ON TABLE gold_article_rankings IS
'Article rankings within store with APSD and cluster comparison. Use for product ranking and APSD questions.';

COMMENT ON TABLE gold_inventory_summary IS
'Store-level inventory health summary with OOS counts, dead stock value, and stock levels. Use for inventory overview.';

COMMENT ON TABLE gold_writeoff_trends IS
'Write-off trends by store with daily, weekly, and monthly summaries. Use for write-off trend analysis.';

COMMENT ON TABLE gold_cook_quantity_guide IS
'Hourly cook quantity recommendations for food service items with demand level indicators. Use for cook planning.';

-- ============================================================================
-- GENIE SPACE CREATION (API REFERENCE)
-- ============================================================================
-- Use Databricks REST API to create Genie Space programmatically:
--   POST /api/2.0/preview/genie/spaces
-- Substitute your warehouse_id, catalog, and schema below.

/*
API Request Body:
{
  "display_name": "7-Eleven Store Assistant",
  "description": "AI-powered store operations assistant for 7-Eleven Australia. Ask questions about sales, inventory, write-offs, and cook quantities.",
  "warehouse_id": "<YOUR_WAREHOUSE_ID>",
  "tables": [
    {"catalog_name": "<CATALOG>", "schema_name": "<SCHEMA>", "table_name": "gold_daily_store_summary"},
    {"catalog_name": "<CATALOG>", "schema_name": "<SCHEMA>", "table_name": "gold_category_performance"},
    {"catalog_name": "<CATALOG>", "schema_name": "<SCHEMA>", "table_name": "gold_article_apsd"},
    {"catalog_name": "<CATALOG>", "schema_name": "<SCHEMA>", "table_name": "gold_inventory_health"},
    {"catalog_name": "<CATALOG>", "schema_name": "<SCHEMA>", "table_name": "gold_dead_stock"},
    {"catalog_name": "<CATALOG>", "schema_name": "<SCHEMA>", "table_name": "gold_hourly_sales"},
    {"catalog_name": "<CATALOG>", "schema_name": "<SCHEMA>", "table_name": "gold_writeoff_summary"},
    {"catalog_name": "<CATALOG>", "schema_name": "<SCHEMA>", "table_name": "gold_writeoff_detail"},
    {"catalog_name": "<CATALOG>", "schema_name": "<SCHEMA>", "table_name": "gold_product_lookup"},
    {"catalog_name": "<CATALOG>", "schema_name": "<SCHEMA>", "table_name": "gold_store_alerts"},
    {"catalog_name": "<CATALOG>", "schema_name": "<SCHEMA>", "table_name": "gold_metrics"},
    {"catalog_name": "<CATALOG>", "schema_name": "<SCHEMA>", "table_name": "gold_store_kpi_summary"},
    {"catalog_name": "<CATALOG>", "schema_name": "<SCHEMA>", "table_name": "gold_category_rankings"},
    {"catalog_name": "<CATALOG>", "schema_name": "<SCHEMA>", "table_name": "gold_article_rankings"},
    {"catalog_name": "<CATALOG>", "schema_name": "<SCHEMA>", "table_name": "gold_inventory_summary"},
    {"catalog_name": "<CATALOG>", "schema_name": "<SCHEMA>", "table_name": "gold_writeoff_trends"},
    {"catalog_name": "<CATALOG>", "schema_name": "<SCHEMA>", "table_name": "gold_cook_quantity_guide"}
  ]
}
*/
