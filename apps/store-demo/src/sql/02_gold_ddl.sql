-- ============================================================================
-- 7-Eleven Store Intelligence Demo - Gold Layer DDL
-- Catalog/Schema: passed in as ${catalog}.${schema}
-- ============================================================================

USE CATALOG ${catalog};
USE SCHEMA ${schema};

-- ============================================================================
-- GOLD ANALYTICS TABLES
-- ============================================================================

-- Daily Store Summary - KPIs per store per day
CREATE OR REPLACE TABLE gold_daily_store_summary (
  store_id INT NOT NULL,
  store_code STRING,
  store_name STRING,
  state STRING,
  cluster_id INT,
  cluster_name STRING,
  summary_date DATE NOT NULL,
  day_of_week INT,
  is_weekend BOOLEAN,
  total_sales DECIMAL(12,2),
  total_gp DECIMAL(12,2),
  gp_margin_pct DECIMAL(5,2),
  total_units DECIMAL(12,2),
  total_cost DECIMAL(12,2),
  transaction_count INT,
  avg_basket_value DECIMAL(10,2),
  avg_basket_units DECIMAL(10,2),
  budget_sales DECIMAL(12,2),
  budget_gp DECIMAL(12,2),
  sales_vs_budget DECIMAL(12,2),
  sales_vs_budget_pct DECIMAL(5,2),
  gp_vs_budget DECIMAL(12,2),
  gp_vs_budget_pct DECIMAL(5,2),
  ly_date DATE,
  ly_sales DECIMAL(12,2),
  ly_gp DECIMAL(12,2),
  yoy_sales_growth DECIMAL(5,2),
  yoy_gp_growth DECIMAL(5,2),
  cluster_avg_sales DECIMAL(12,2),
  vs_cluster_pct DECIMAL(5,2),
  CONSTRAINT pk_daily_summary PRIMARY KEY (store_id, summary_date)
)
PARTITIONED BY (summary_date);

-- Category Performance - category-level metrics
CREATE OR REPLACE TABLE gold_category_performance (
  store_id INT NOT NULL,
  store_code STRING,
  store_name STRING,
  cluster_id INT,
  cluster_name STRING,
  category_id INT NOT NULL,
  category_name STRING,
  subcategory STRING,
  department STRING,
  period_type STRING NOT NULL,
  period_start DATE NOT NULL,
  period_end DATE,
  total_sales DECIMAL(12,2),
  total_gp DECIMAL(12,2),
  total_units DECIMAL(12,2),
  total_cost DECIMAL(12,2),
  gp_margin_pct DECIMAL(5,2),
  sales_share_pct DECIMAL(5,2),
  gp_share_pct DECIMAL(5,2),
  units_share_pct DECIMAL(5,2),
  ly_sales DECIMAL(12,2),
  ly_gp DECIMAL(12,2),
  ly_units DECIMAL(12,2),
  yoy_sales_growth DECIMAL(5,2),
  yoy_gp_growth DECIMAL(5,2),
  yoy_units_growth DECIMAL(5,2),
  gp_vs_sales_growth_diff DECIMAL(5,2),
  budget_sales DECIMAL(12,2),
  budget_gp DECIMAL(12,2),
  sales_vs_budget_pct DECIMAL(5,2),
  gp_vs_budget_pct DECIMAL(5,2),
  cluster_avg_sales DECIMAL(12,2),
  cluster_avg_gp DECIMAL(12,2),
  vs_cluster_sales_pct DECIMAL(5,2),
  vs_cluster_gp_pct DECIMAL(5,2),
  cluster_std_dev_sales DECIMAL(12,2),
  is_growth_outlier BOOLEAN,
  is_decline_outlier BOOLEAN,
  CONSTRAINT pk_category_perf PRIMARY KEY (store_id, category_id, period_type, period_start)
)
PARTITIONED BY (period_start);

-- Article APSD - Average Per Store Per Day metrics
CREATE OR REPLACE TABLE gold_article_apsd (
  store_id INT NOT NULL,
  store_code STRING,
  store_name STRING,
  cluster_id INT,
  cluster_name STRING,
  article_id INT NOT NULL,
  article_code STRING,
  article_name STRING,
  ean STRING,
  category_id INT,
  category_name STRING,
  subcategory STRING,
  department STRING,
  layout_location STRING,
  shelf_position STRING,
  is_tailored_in BOOLEAN,
  vendor_name STRING,
  unit_cost DECIMAL(10,4),
  unit_price DECIMAL(10,2),
  margin_pct DECIMAL(5,2),
  period_type STRING NOT NULL,
  period_start DATE NOT NULL,
  period_end DATE,
  days_in_period INT,
  total_units DECIMAL(12,2),
  total_sales DECIMAL(12,2),
  total_gp DECIMAL(12,2),
  apsd_units DECIMAL(10,4),
  apsd_sales DECIMAL(10,4),
  apsd_gp DECIMAL(10,4),
  cluster_apsd_units DECIMAL(10,4),
  cluster_apsd_sales DECIMAL(10,4),
  cluster_apsd_gp DECIMAL(10,4),
  vs_cluster_apsd_pct DECIMAL(5,2),
  rank_in_category INT,
  rank_in_subcategory INT,
  rank_in_layout INT,
  rank_in_store INT,
  cluster_rank_in_category INT,
  CONSTRAINT pk_article_apsd PRIMARY KEY (store_id, article_id, period_type, period_start)
)
PARTITIONED BY (period_start);

-- Inventory Health - current stock status
CREATE OR REPLACE TABLE gold_inventory_health (
  store_id INT NOT NULL,
  store_code STRING,
  store_name STRING,
  cluster_id INT,
  article_id INT NOT NULL,
  article_code STRING,
  article_name STRING,
  ean STRING,
  category_name STRING,
  subcategory STRING,
  department STRING,
  layout_location STRING,
  vendor_name STRING,
  is_tailored_in BOOLEAN,
  is_food_service BOOLEAN,
  soh_qty DECIMAL(10,2),
  soh_value DECIMAL(12,2),
  unit_cost DECIMAL(10,4),
  unit_price DECIMAL(10,2),
  avg_daily_sales_units DECIMAL(10,4),
  avg_daily_sales_value DECIMAL(10,4),
  days_of_stock DECIMAL(10,2),
  last_sale_date DATE,
  last_sale_hour INT,
  days_since_last_sale INT,
  last_receipt_date DATE,
  first_oos_date DATE,
  is_out_of_stock BOOLEAN,
  is_dead_stock BOOLEAN,
  projected_oos_date DATE,
  days_until_oos INT,
  case_size INT,
  min_order_qty INT,
  max_order_qty INT,
  lead_time_days INT,
  reorder_point DECIMAL(10,2),
  suggested_reorder_qty DECIMAL(10,2),
  apsd_units DECIMAL(10,4),
  apsd_rank_in_store INT,
  updated_at TIMESTAMP,
  CONSTRAINT pk_inventory_health PRIMARY KEY (store_id, article_id)
);

-- Dead Stock - no sales in 28+ days
CREATE OR REPLACE TABLE gold_dead_stock (
  store_id INT NOT NULL,
  store_code STRING,
  store_name STRING,
  cluster_id INT,
  cluster_name STRING,
  article_id INT NOT NULL,
  article_code STRING,
  article_name STRING,
  ean STRING,
  category_name STRING,
  subcategory STRING,
  department STRING,
  layout_location STRING,
  vendor_name STRING,
  is_tailored_in BOOLEAN,
  soh_qty DECIMAL(10,2),
  soh_value DECIMAL(12,2),
  unit_cost DECIMAL(10,4),
  last_sale_date DATE,
  days_since_last_sale INT,
  cluster_has_sales BOOLEAN,
  cluster_apsd_units DECIMAL(10,4),
  cluster_total_units_28d DECIMAL(12,2),
  rank_by_soh_qty INT,
  rank_by_soh_value INT,
  updated_at TIMESTAMP,
  CONSTRAINT pk_dead_stock PRIMARY KEY (store_id, article_id)
);

-- Hourly Sales - sales patterns by hour and day of week
CREATE OR REPLACE TABLE gold_hourly_sales (
  store_id INT NOT NULL,
  store_code STRING,
  store_name STRING,
  article_id INT NOT NULL,
  article_code STRING,
  article_name STRING,
  category_name STRING,
  subcategory STRING,
  is_food_service BOOLEAN,
  day_of_week INT NOT NULL,
  day_name STRING,
  hour_of_day INT NOT NULL,
  is_weekend BOOLEAN,
  is_lunch_peak BOOLEAN,
  period_start DATE,
  period_end DATE,
  weeks_in_period INT,
  total_units DECIMAL(12,2),
  total_sales DECIMAL(12,2),
  avg_units DECIMAL(10,4),
  avg_sales DECIMAL(10,4),
  min_units DECIMAL(10,2),
  max_units DECIMAL(10,2),
  std_dev_units DECIMAL(10,4),
  pct_of_daily_units DECIMAL(5,2),
  recommended_cook_qty DECIMAL(10,2),
  recommended_cook_qty_growth DECIMAL(10,2),
  CONSTRAINT pk_hourly_sales PRIMARY KEY (store_id, article_id, day_of_week, hour_of_day)
);

-- Write-off Summary - aggregated write-offs by category
CREATE OR REPLACE TABLE gold_writeoff_summary (
  store_id INT NOT NULL,
  store_code STRING,
  store_name STRING,
  cluster_id INT,
  cluster_name STRING,
  writeoff_date DATE NOT NULL,
  category_name STRING,
  subcategory STRING,
  department STRING,
  reason_code STRING,
  total_qty DECIMAL(12,2),
  total_value DECIMAL(12,2),
  item_count INT,
  cluster_avg_qty DECIMAL(12,2),
  cluster_avg_value DECIMAL(12,2),
  cluster_std_dev_qty DECIMAL(12,2),
  cluster_std_dev_value DECIMAL(12,2),
  vs_cluster_qty_pct DECIMAL(5,2),
  vs_cluster_value_pct DECIMAL(5,2),
  std_dev_from_cluster DECIMAL(5,2),
  is_anomaly BOOLEAN,
  anomaly_direction STRING,
  CONSTRAINT pk_writeoff_summary PRIMARY KEY (store_id, writeoff_date, category_name, reason_code)
)
PARTITIONED BY (writeoff_date);

-- Write-off Detail - detailed write-off records
CREATE OR REPLACE TABLE gold_writeoff_detail (
  writeoff_id BIGINT NOT NULL,
  store_id INT,
  store_code STRING,
  store_name STRING,
  cluster_id INT,
  article_id INT,
  article_code STRING,
  article_name STRING,
  ean STRING,
  category_name STRING,
  subcategory STRING,
  department STRING,
  writeoff_date DATE NOT NULL,
  writeoff_time STRING,
  writeoff_hour INT,
  quantity DECIMAL(10,2),
  value DECIMAL(12,2),
  unit_cost DECIMAL(10,4),
  reason_code STRING,
  reason_desc STRING,
  team_member_name STRING,
  team_member_role STRING,
  is_store_use BOOLEAN,
  cluster_avg_qty_for_article DECIMAL(10,2),
  is_anomaly_for_article BOOLEAN,
  CONSTRAINT pk_writeoff_detail PRIMARY KEY (writeoff_id)
)
PARTITIONED BY (writeoff_date);

-- Write-off Reconciliation - purchase vs sales vs write-off
CREATE OR REPLACE TABLE gold_writeoff_reconciliation (
  store_id INT NOT NULL,
  store_code STRING,
  store_name STRING,
  article_id INT NOT NULL,
  article_code STRING,
  article_name STRING,
  category_name STRING,
  reconciliation_date DATE NOT NULL,
  day_of_week INT,
  day_name STRING,
  opening_stock DECIMAL(10,2),
  purchases_qty DECIMAL(10,2),
  sales_qty DECIMAL(10,2),
  writeoff_qty DECIMAL(10,2),
  closing_stock DECIMAL(10,2),
  expected_writeoff DECIMAL(10,2),
  writeoff_variance DECIMAL(10,2),
  variance_pct DECIMAL(5,2),
  is_variance_anomaly BOOLEAN,
  variance_direction STRING,
  shelf_life_days INT,
  avg_daily_writeoff DECIMAL(10,2),
  std_dev_writeoff DECIMAL(10,2),
  CONSTRAINT pk_writeoff_recon PRIMARY KEY (store_id, article_id, reconciliation_date)
)
PARTITIONED BY (reconciliation_date);

-- Store Use Compliance - tracking store use write-offs (milk for coffee)
CREATE OR REPLACE TABLE gold_store_use_compliance (
  store_id INT NOT NULL,
  store_code STRING,
  store_name STRING,
  compliance_date DATE NOT NULL,
  day_of_week INT,
  day_name STRING,
  article_id INT,
  article_name STRING,
  category_name STRING,
  store_use_qty DECIMAL(10,2),
  store_use_value DECIMAL(12,2),
  has_store_use BOOLEAN,
  avg_daily_store_use DECIMAL(10,2),
  std_dev_store_use DECIMAL(10,2),
  is_missing BOOLEAN,
  is_outlier_high BOOLEAN,
  is_outlier_low BOOLEAN,
  deviation_from_avg DECIMAL(5,2),
  CONSTRAINT pk_store_use PRIMARY KEY (store_id, article_id, compliance_date)
)
PARTITIONED BY (compliance_date);

-- Product Lookup - article master for Genie queries
CREATE OR REPLACE TABLE gold_product_lookup (
  article_id INT NOT NULL,
  article_code STRING,
  article_name STRING,
  ean STRING,
  category_name STRING,
  subcategory STRING,
  department STRING,
  layout_group STRING,
  vendor_id INT,
  vendor_name STRING,
  vendor_contact STRING,
  delivery_days STRING,
  lead_time_days INT,
  unit_cost DECIMAL(10,4),
  unit_price DECIMAL(10,2),
  margin_pct DECIMAL(5,2),
  purchase_margin_pct DECIMAL(5,2),
  gp_per_unit DECIMAL(10,4),
  pack_qty INT,
  case_size INT,
  min_order_qty INT,
  max_order_qty INT,
  shelf_life_days INT,
  is_food_service BOOLEAN,
  is_active BOOLEAN,
  updated_at TIMESTAMP,
  CONSTRAINT pk_product_lookup PRIMARY KEY (article_id)
);

-- Store Alerts - pre-computed alerts for the app
CREATE OR REPLACE TABLE gold_store_alerts (
  alert_id BIGINT NOT NULL,
  store_id INT,
  store_code STRING,
  alert_date DATE NOT NULL,
  alert_time TIMESTAMP,
  alert_type STRING,
  alert_severity STRING,
  alert_title STRING,
  alert_message STRING,
  article_id INT,
  article_name STRING,
  category_name STRING,
  metric_value DECIMAL(12,2),
  threshold_value DECIMAL(12,2),
  action_recommended STRING,
  is_acknowledged BOOLEAN DEFAULT FALSE,
  acknowledged_by STRING,
  acknowledged_at TIMESTAMP,
  created_at TIMESTAMP,
  expires_at TIMESTAMP,
  CONSTRAINT pk_store_alerts PRIMARY KEY (alert_id)
);

-- ============================================================================
-- VERIFY TABLES CREATED
-- ============================================================================
SHOW TABLES;
