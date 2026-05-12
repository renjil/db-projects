-- ============================================================================
-- 7-Eleven Store Intelligence Demo - Silver Layer DDL
-- Catalog/Schema: passed in as ${catalog}.${schema}
-- ============================================================================

USE CATALOG ${catalog};
USE SCHEMA ${schema};

-- ============================================================================
-- DIMENSION TABLES
-- ============================================================================

-- Store Clusters (comparable store groups by state/territory)
CREATE OR REPLACE TABLE silver_store_clusters (
  cluster_id INT NOT NULL,
  cluster_code STRING NOT NULL,
  cluster_name STRING NOT NULL,
  state STRING NOT NULL,
  region STRING,
  store_count INT,
  CONSTRAINT pk_store_clusters PRIMARY KEY (cluster_id)
);

-- Stores
CREATE OR REPLACE TABLE silver_stores (
  store_id INT NOT NULL,
  store_code STRING NOT NULL,
  store_name STRING NOT NULL,
  address STRING,
  city STRING,
  state STRING NOT NULL,
  postcode STRING,
  cluster_id INT,
  territory STRING,
  format_type STRING,
  open_date DATE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  CONSTRAINT pk_stores PRIMARY KEY (store_id),
  CONSTRAINT fk_stores_cluster FOREIGN KEY (cluster_id) REFERENCES silver_store_clusters(cluster_id)
);

-- Categories
CREATE OR REPLACE TABLE silver_categories (
  category_id INT NOT NULL,
  category_code STRING NOT NULL,
  category_name STRING NOT NULL,
  subcategory STRING,
  department STRING,
  layout_group STRING,
  is_food_service BOOLEAN DEFAULT FALSE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT pk_categories PRIMARY KEY (category_id)
);

-- Vendors
CREATE OR REPLACE TABLE silver_vendors (
  vendor_id INT NOT NULL,
  vendor_code STRING NOT NULL,
  vendor_name STRING NOT NULL,
  contact_email STRING,
  contact_phone STRING,
  lead_time_days INT,
  delivery_days STRING,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT pk_vendors PRIMARY KEY (vendor_id)
);

-- Articles (Products/SKUs)
CREATE OR REPLACE TABLE silver_articles (
  article_id INT NOT NULL,
  article_code STRING NOT NULL,
  article_name STRING NOT NULL,
  ean STRING,
  category_id INT NOT NULL,
  vendor_id INT,
  unit_cost DECIMAL(10,4) NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  margin_pct DECIMAL(5,2),
  purchase_margin_pct DECIMAL(5,2),
  pack_qty INT,
  case_size INT,
  min_order_qty INT,
  max_order_qty INT,
  shelf_life_days INT,
  is_food_service BOOLEAN DEFAULT FALSE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  CONSTRAINT pk_articles PRIMARY KEY (article_id),
  CONSTRAINT fk_articles_category FOREIGN KEY (category_id) REFERENCES silver_categories(category_id),
  CONSTRAINT fk_articles_vendor FOREIGN KEY (vendor_id) REFERENCES silver_vendors(vendor_id)
);

-- Store Layouts (which articles are in each store's planogram)
CREATE OR REPLACE TABLE silver_store_layouts (
  store_id INT NOT NULL,
  article_id INT NOT NULL,
  layout_location STRING NOT NULL,
  shelf_position STRING,
  facing_count INT,
  is_tailored_in BOOLEAN NOT NULL DEFAULT TRUE,
  effective_date DATE NOT NULL,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  CONSTRAINT pk_store_layouts PRIMARY KEY (store_id, article_id),
  CONSTRAINT fk_layouts_store FOREIGN KEY (store_id) REFERENCES silver_stores(store_id),
  CONSTRAINT fk_layouts_article FOREIGN KEY (article_id) REFERENCES silver_articles(article_id)
);

-- Team Members
CREATE OR REPLACE TABLE silver_team_members (
  member_id INT NOT NULL,
  member_code STRING NOT NULL,
  store_id INT NOT NULL,
  member_name STRING NOT NULL,
  role STRING,
  hire_date DATE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  CONSTRAINT pk_team_members PRIMARY KEY (member_id),
  CONSTRAINT fk_members_store FOREIGN KEY (store_id) REFERENCES silver_stores(store_id)
);

-- ============================================================================
-- FACT TABLES
-- ============================================================================

-- Sales Transactions
CREATE OR REPLACE TABLE silver_sales_transactions (
  txn_id BIGINT NOT NULL,
  store_id INT NOT NULL,
  article_id INT NOT NULL,
  txn_date DATE NOT NULL,
  txn_hour INT NOT NULL,
  txn_minute INT,
  txn_timestamp TIMESTAMP NOT NULL,
  day_of_week INT NOT NULL,
  is_weekend BOOLEAN NOT NULL,
  units_sold DECIMAL(10,2) NOT NULL,
  revenue DECIMAL(12,2) NOT NULL,
  cost DECIMAL(12,2) NOT NULL,
  gross_profit DECIMAL(12,2) NOT NULL,
  txn_type STRING NOT NULL DEFAULT 'SALE',
  CONSTRAINT pk_sales PRIMARY KEY (txn_id),
  CONSTRAINT fk_sales_store FOREIGN KEY (store_id) REFERENCES silver_stores(store_id),
  CONSTRAINT fk_sales_article FOREIGN KEY (article_id) REFERENCES silver_articles(article_id)
)
PARTITIONED BY (txn_date)
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);

-- Inventory (current snapshot)
CREATE OR REPLACE TABLE silver_inventory (
  store_id INT NOT NULL,
  article_id INT NOT NULL,
  snapshot_date DATE NOT NULL,
  soh_qty DECIMAL(10,2) NOT NULL,
  soh_value DECIMAL(12,2) NOT NULL,
  last_receipt_date DATE,
  last_sale_date DATE,
  days_since_last_sale INT,
  first_oos_date DATE,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  CONSTRAINT pk_inventory PRIMARY KEY (store_id, article_id),
  CONSTRAINT fk_inventory_store FOREIGN KEY (store_id) REFERENCES silver_stores(store_id),
  CONSTRAINT fk_inventory_article FOREIGN KEY (article_id) REFERENCES silver_articles(article_id)
);

-- Purchases (goods receipts)
CREATE OR REPLACE TABLE silver_purchases (
  purchase_id BIGINT NOT NULL,
  store_id INT NOT NULL,
  article_id INT NOT NULL,
  vendor_id INT,
  receipt_date DATE NOT NULL,
  receipt_timestamp TIMESTAMP,
  qty_ordered DECIMAL(10,2),
  qty_received DECIMAL(10,2) NOT NULL,
  unit_cost DECIMAL(10,4) NOT NULL,
  total_cost DECIMAL(12,2) NOT NULL,
  po_number STRING,
  CONSTRAINT pk_purchases PRIMARY KEY (purchase_id),
  CONSTRAINT fk_purchases_store FOREIGN KEY (store_id) REFERENCES silver_stores(store_id),
  CONSTRAINT fk_purchases_article FOREIGN KEY (article_id) REFERENCES silver_articles(article_id)
)
PARTITIONED BY (receipt_date);

-- Write-offs
CREATE OR REPLACE TABLE silver_write_offs (
  writeoff_id BIGINT NOT NULL,
  store_id INT NOT NULL,
  article_id INT NOT NULL,
  writeoff_date DATE NOT NULL,
  writeoff_time STRING,
  writeoff_hour INT,
  quantity DECIMAL(10,2) NOT NULL,
  value DECIMAL(12,2) NOT NULL,
  reason_code STRING NOT NULL,
  reason_desc STRING,
  team_member_id INT,
  team_member_name STRING,
  CONSTRAINT pk_writeoffs PRIMARY KEY (writeoff_id),
  CONSTRAINT fk_writeoffs_store FOREIGN KEY (store_id) REFERENCES silver_stores(store_id),
  CONSTRAINT fk_writeoffs_article FOREIGN KEY (article_id) REFERENCES silver_articles(article_id)
)
PARTITIONED BY (writeoff_date);

-- Budgets
CREATE OR REPLACE TABLE silver_budgets (
  budget_id BIGINT NOT NULL,
  store_id INT NOT NULL,
  category_id INT,
  period_type STRING NOT NULL,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  budget_sales DECIMAL(12,2) NOT NULL,
  budget_gp DECIMAL(12,2) NOT NULL,
  budget_units DECIMAL(10,2),
  CONSTRAINT pk_budgets PRIMARY KEY (budget_id),
  CONSTRAINT fk_budgets_store FOREIGN KEY (store_id) REFERENCES silver_stores(store_id),
  CONSTRAINT fk_budgets_category FOREIGN KEY (category_id) REFERENCES silver_categories(category_id)
);

-- ============================================================================
-- VERIFY TABLES CREATED
-- ============================================================================
SHOW TABLES;
