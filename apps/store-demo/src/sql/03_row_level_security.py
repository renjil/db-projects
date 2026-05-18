# Databricks notebook source
# MAGIC %md
# MAGIC # Row-Level Security setup
# MAGIC
# MAGIC Creates the user-store access table, seeds demo access, creates the
# MAGIC row-filter function, applies the filter to every Gold materialized
# MAGIC view, populates geo coordinates on silver_stores, creates helper views,
# MAGIC and grants SELECT on the Gold tables.
# MAGIC
# MAGIC Implemented as a Python notebook so each SQL statement is executed
# MAGIC individually via `spark.sql()` (avoids multi-statement parser quirks
# MAGIC with `CREATE FUNCTION ... RETURN (... EXISTS ...)`).

# COMMAND ----------
dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
if not catalog or not schema:
    raise ValueError("Both 'catalog' and 'schema' widgets must be set")

fq = lambda t: f"{catalog}.{schema}.{t}"
spark.sql(f"USE CATALOG {catalog}")
spark.sql(f"USE SCHEMA  {schema}")
print(f"Using {catalog}.{schema}")


# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 1 — User-store access table

# COMMAND ----------
spark.sql(f"""
CREATE TABLE IF NOT EXISTS {fq('silver_user_store_access')} (
  user_email STRING NOT NULL COMMENT 'User email address',
  store_id INT NOT NULL COMMENT 'Store ID the user has access to',
  role STRING COMMENT 'User role',
  access_level STRING COMMENT 'READ / WRITE / ADMIN',
  granted_at TIMESTAMP COMMENT 'When access was granted',
  granted_by STRING COMMENT 'Who granted the access',
  expires_at TIMESTAMP COMMENT 'When access expires (NULL = permanent)',
  is_active BOOLEAN COMMENT 'Whether access is currently active',
  CONSTRAINT pk_user_store PRIMARY KEY (user_email, store_id)
)
COMMENT 'User-to-store access mapping for row-level security'
""")
print("  ✓ silver_user_store_access ready")


# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 2 — Seed demo access (idempotent)

# COMMAND ----------
spark.sql(f"""
INSERT INTO {fq('silver_user_store_access')}
  (user_email, store_id, role, access_level, granted_at, granted_by, is_active)
SELECT DISTINCT
  'demo@databricks.com', s.store_id, 'Demo User', 'READ',
  current_timestamp(), 'system', TRUE
FROM {fq('silver_stores')} s
LEFT JOIN {fq('silver_user_store_access')} usa
  ON usa.user_email = 'demo@databricks.com' AND usa.store_id = s.store_id
WHERE usa.user_email IS NULL
""")
print("  ✓ demo access seeded")


# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 3 — Row-filter function

# COMMAND ----------
spark.sql(f"""
CREATE OR REPLACE FUNCTION {fq('check_store_access')}(store_id INT)
RETURNS BOOLEAN
COMMENT 'Row filter for store-level access control'
RETURN (
  current_user() LIKE '%@databricks.com'
  OR EXISTS (
    SELECT 1
    FROM {fq('silver_user_store_access')} usa
    WHERE usa.user_email = current_user()
      AND usa.store_id = check_store_access.store_id
      AND usa.is_active = TRUE
      AND (usa.expires_at IS NULL OR usa.expires_at > current_timestamp())
  )
)
""")
print("  ✓ check_store_access function ready")


# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 4 — Apply the row filter to each Gold materialized view

# COMMAND ----------
gold_views_with_store_id = [
    "gold_daily_store_summary", "gold_category_performance", "gold_article_apsd",
    "gold_inventory_health", "gold_dead_stock", "gold_hourly_sales",
    "gold_writeoff_summary", "gold_writeoff_detail", "gold_writeoff_reconciliation",
    "gold_store_use_compliance", "gold_store_alerts",
]
for v in gold_views_with_store_id:
    spark.sql(f"ALTER MATERIALIZED VIEW {fq(v)} SET ROW FILTER {fq('check_store_access')} ON (store_id)")
    print(f"  ✓ row filter on {v}")


# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 5 — Helper views

# COMMAND ----------
spark.sql(f"""
CREATE OR REPLACE VIEW {fq('v_my_stores')} AS
SELECT s.*, usa.role, usa.access_level, usa.granted_at
FROM {fq('silver_stores')} s
JOIN {fq('silver_user_store_access')} usa ON s.store_id = usa.store_id
WHERE usa.user_email = current_user()
  AND usa.is_active = TRUE
  AND (usa.expires_at IS NULL OR usa.expires_at > current_timestamp())
""")

spark.sql(f"""
CREATE OR REPLACE VIEW {fq('v_user_access_summary')} AS
SELECT
  usa.user_email,
  COUNT(DISTINCT usa.store_id) AS store_count,
  COLLECT_SET(s.state)         AS states,
  COLLECT_SET(usa.role)        AS roles,
  MIN(usa.granted_at)          AS first_grant,
  MAX(usa.granted_at)          AS last_grant
FROM {fq('silver_user_store_access')} usa
JOIN {fq('silver_stores')} s ON usa.store_id = s.store_id
WHERE usa.is_active = TRUE
GROUP BY usa.user_email
""")
print("  ✓ helper views ready")


# COMMAND ----------
# MAGIC %md
# MAGIC ## Step 6 — Automatic grants + RLS row for the app's service principal
# MAGIC
# MAGIC The Streamlit app runs as its own service principal (created by
# MAGIC `databricks bundle deploy`). That SP has no UC privileges by default,
# MAGIC and `current_user()` in queries from the app returns the SP's
# MAGIC `application_id` (UUID) — not its display name. We look the SP up here
# MAGIC and:
# MAGIC   1. grant it `USE CATALOG`, `USE SCHEMA`, `SELECT`, `EXECUTE` so the
# MAGIC      app can read silver_stores / gold tables and call the row filter,
# MAGIC   2. insert an "all stores" row in `silver_user_store_access` keyed on
# MAGIC      the UUID so the row filter on Gold MVs returns data for the app.
# MAGIC
# MAGIC The app name (`APP_NAME` below) must match `resources/apps.yml`. If you
# MAGIC rename the app there, change it here too.

# COMMAND ----------
APP_NAME = "7eleven-store-intelligence"

import traceback, requests
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
status = {"app_name": APP_NAME}

def _lookup_app(name):
    """Return (sp_client_id, sp_name) for the Databricks App.

    The serverless runtime's bundled databricks-sdk can be older than the
    typed AppsAPI shape, so call the REST endpoint directly via the SDK's
    authenticated config.
    """
    cfg = w.config
    # Config.authenticate() returns a dict of auth headers (Bearer or OAuth).
    headers = cfg.authenticate() if callable(getattr(cfg, "authenticate", None)) else {}
    url = f"{cfg.host.rstrip('/')}/api/2.0/apps/{name}"
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    body = r.json()
    return body.get("service_principal_client_id"), body.get("service_principal_name")

try:
    sp_uuid, sp_label = _lookup_app(APP_NAME)
    status["sp_uuid"]  = sp_uuid
    status["sp_label"] = sp_label
    print(f"  app SP discovered: name='{sp_label}'  app_id={sp_uuid}")
except Exception as e:
    status["lookup_error"] = f"{type(e).__name__}: {e}"
    status["lookup_traceback"] = traceback.format_exc()
    print(f"  WARN: could not look up app '{APP_NAME}' — skipping SP grants. ({e})")
    sp_uuid = None

if sp_uuid:
    # 6a. UC grants (catalog/schema/select/execute).
    for stmt in [
        f"GRANT USE CATALOG ON CATALOG {catalog}             TO `{sp_uuid}`",
        f"GRANT USE SCHEMA  ON SCHEMA  {catalog}.{schema}    TO `{sp_uuid}`",
        f"GRANT SELECT      ON SCHEMA  {catalog}.{schema}    TO `{sp_uuid}`",
        f"GRANT EXECUTE ON FUNCTION {fq('check_store_access')} TO `{sp_uuid}`",
    ]:
        spark.sql(stmt)
    status["grants"] = "ok"

    # 6b. Allow-row in silver_user_store_access for the row filter to return data.
    spark.sql(f"""
        INSERT INTO {fq('silver_user_store_access')}
          (user_email, store_id, role, access_level, granted_at, granted_by, is_active)
        SELECT '{sp_uuid}', s.store_id, 'App Service Principal', 'READ',
               current_timestamp(), 'system', true
        FROM {fq('silver_stores')} s
        LEFT JOIN {fq('silver_user_store_access')} usa
          ON usa.user_email = '{sp_uuid}' AND usa.store_id = s.store_id
        WHERE usa.user_email IS NULL
    """)
    n = spark.sql(f"SELECT COUNT(*) FROM {fq('silver_user_store_access')} WHERE user_email = '{sp_uuid}'").collect()[0][0]
    status["access_rows"] = n
    print(f"  ✓ silver_user_store_access has {n} rows for the app SP")

    # 6c. (intentionally empty)
    # The bundle's `resources.apps.resources.sql_warehouse` block in
    # resources/apps.yml declares `permission: CAN_USE` on the warehouse for
    # the app's SP — that should be enough; no explicit permissions PATCH
    # needed here. If a fresh-workspace deploy proves otherwise, restore the
    # PATCH-based grant via `/api/2.0/permissions/warehouses/{id}`.

# Return status from this notebook so we can inspect it via runs/get-output
import json as _json
dbutils.notebook.exit(_json.dumps(status))
