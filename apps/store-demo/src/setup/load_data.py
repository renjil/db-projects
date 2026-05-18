# Databricks notebook source
# MAGIC %md
# MAGIC # load_data
# MAGIC
# MAGIC Generates the synthetic 7-Eleven demo data **on serverless compute**
# MAGIC and writes each table into the Silver layer.
# MAGIC
# MAGIC No local Python or CLI is needed — this runs entirely as a Databricks job.
# MAGIC
# MAGIC Widgets (populated from the job's `base_parameters`):
# MAGIC - `catalog` — Unity Catalog name (e.g. `retail_demo`)
# MAGIC - `schema`  — schema name (e.g. `store_demo`)
# MAGIC
# MAGIC Prerequisite: the Silver tables must already exist (the `setup_silver_ddl`
# MAGIC job runs before this in the `setup_all` orchestrator).

# COMMAND ----------
dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
if not catalog or not schema:
    raise ValueError("Both 'catalog' and 'schema' widgets must be set")

spark.sql(f"USE CATALOG {catalog}")
spark.sql(f"USE SCHEMA  {schema}")
print(f"Using {catalog}.{schema}")


# COMMAND ----------
# MAGIC %md
# MAGIC ## Load the data-generator module
# MAGIC
# MAGIC `_data_generator.py` is deployed alongside this notebook by the bundle.
# MAGIC We add its directory to `sys.path` and import it as a regular Python module.

# COMMAND ----------
import sys, os

# When deployed by DAB, this notebook lives at
# ${workspace.file_path}/src/setup/load_data.py and _data_generator.py is next to it.
notebook_dir = os.path.dirname(
    dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get()
)
# notebook_dir is a workspace path like /Workspace/.../src/setup -- import from the file-system equivalent.
sys.path.insert(0, "/Workspace" + notebook_dir if not notebook_dir.startswith("/Workspace") else notebook_dir)

import _data_generator as gen
print(f"Loaded generator: {gen.__file__}")


# COMMAND ----------
# MAGIC %md
# MAGIC ## Generate all rows in memory

# COMMAND ----------
print("Generating dimension data...")
clusters     = gen.generate_store_clusters()
stores       = gen.generate_stores(clusters)
categories   = gen.generate_categories()
vendors      = gen.generate_vendors()
articles     = gen.generate_articles(categories, vendors)
layouts      = gen.generate_store_layouts(stores, articles, categories)
team_members = gen.generate_team_members(stores)

print(f"  {len(clusters)} clusters, {len(stores)} stores, {len(categories)} categories, "
      f"{len(vendors)} vendors, {len(articles)} articles, {len(layouts)} layouts, "
      f"{len(team_members)} team members")

print("Generating fact data (this may take a minute)...")
transactions = gen.generate_sales_transactions(stores, layouts, articles, categories)
inventory    = gen.generate_inventory(stores, layouts, articles, transactions)
writeoffs    = gen.generate_writeoffs(stores, layouts, articles, team_members)
purchases    = gen.generate_purchases(stores, layouts, articles, vendors)
budgets      = gen.generate_budgets(stores, categories)
reviews      = gen.generate_customer_reviews(stores)
print(f"  {len(transactions):,} transactions, {len(inventory):,} inventory rows, "
      f"{len(writeoffs):,} write-offs, {len(purchases):,} purchases, "
      f"{len(budgets):,} budgets, {len(reviews):,} reviews")


# COMMAND ----------
# MAGIC %md
# MAGIC ## Write each table via Spark
# MAGIC
# MAGIC For every table we:
# MAGIC 1. Coerce `date` / `datetime` objects in the generator dicts to ISO strings (so
# MAGIC    Spark schema inference doesn't choke).
# MAGIC 2. Register the rows as a temp view.
# MAGIC 3. `INSERT OVERWRITE TABLE <target> (col_list) SELECT col_list ...` —
# MAGIC    matches the target table's columns by name, leaves IDENTITY columns
# MAGIC    alone, and fills `updated_at` with `current_timestamp()` where the
# MAGIC    table expects it.

# COMMAND ----------
import datetime

def _normalize(rows):
    """Stringify dates/datetimes for clean Spark schema inference."""
    out = []
    for r in rows:
        nr = {}
        for k, v in r.items():
            nr[k] = v.isoformat() if isinstance(v, (datetime.date, datetime.datetime)) else v
        out.append(nr)
    return out


def load_table(table_name, rows):
    target = f"{catalog}.{schema}.{table_name}"
    rows = _normalize(rows)
    if not rows:
        print(f"  - {table_name}: no rows generated")
        return

    df = spark.createDataFrame(rows)
    df.createOrReplaceTempView("tmp_load")

    target_cols = [f.name for f in spark.table(target).schema]
    df_cols = df.columns

    # Build SELECT clause: take each target column from tmp_load when available,
    # supply current_timestamp() for `updated_at` / `created_at` (the generator
    # doesn't produce these), and skip GENERATED-ALWAYS-AS-IDENTITY columns by
    # omitting them from both sides of the INSERT.
    timestamp_fallback_cols = {"updated_at", "created_at"}
    insert_cols, select_exprs = [], []
    for c in target_cols:
        if c in df_cols:
            insert_cols.append(c)
            select_exprs.append(c)
        elif c in timestamp_fallback_cols:
            insert_cols.append(c)
            select_exprs.append(f"current_timestamp() AS {c}")
        # else: identity column — omit entirely.

    col_list = ", ".join(insert_cols)
    select_list = ", ".join(select_exprs)
    spark.sql(
        f"INSERT OVERWRITE TABLE {target} ({col_list}) "
        f"SELECT {select_list} FROM tmp_load"
    )
    print(f"  ✓ {table_name}: {spark.table(target).count():,} rows")


# COMMAND ----------
datasets = [
    ("silver_store_clusters",     clusters),
    ("silver_stores",             stores),
    ("silver_categories",         categories),
    ("silver_vendors",            vendors),
    ("silver_articles",           articles),
    ("silver_store_layouts",      layouts),
    ("silver_team_members",       team_members),
    ("silver_sales_transactions", transactions),
    ("silver_inventory",          inventory),
    ("silver_write_offs",         writeoffs),
    ("silver_purchases",          purchases),
    ("silver_budgets",            budgets),
    ("silver_customer_reviews",   reviews),
]

for name, rows in datasets:
    load_table(name, rows)

print("\nAll Silver tables loaded.")
