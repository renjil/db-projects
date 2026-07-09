# Databricks notebook source
# =====================================================================
# Pattern A - Bronze ingest (Unity Catalog)
# Migrated from hive_metastore + DBFS mounts -> renjiharold_demo.portfolio
# 3-level namespace, UC Volume for file reads, managed Delta tables.
# =====================================================================

# COMMAND ----------
# Parameters (overridable via DAB job parameters)
dbutils.widgets.text("catalog", "renjiharold_demo")
dbutils.widgets.text("schema", "portfolio")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

# COMMAND ----------
# No dbutils.fs.mount: landing storage is governed by UC.
# Files are read from a UC Volume instead of dbfs:/mnt/landing.
# (Storage Credential + Volume are provisioned once via sql/01_provision.sql.)

# COMMAND ----------
# 3-level namespace on Unity Catalog
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
spark.sql(f"USE CATALOG {catalog}")
spark.sql(f"USE SCHEMA {schema}")

# COMMAND ----------
# Read raw files from the UC Volume (replaces dbfs:/mnt/landing)
landing_path = f"/Volumes/{catalog}/{schema}/landing/transactions"
raw = (
    spark.read.format("csv")
    .option("header", True)
    .load(f"{landing_path}/*.csv")
)

# COMMAND ----------
# Persist as a UC-managed Delta table (fully qualified 3-level name)
raw.write.mode("overwrite").saveAsTable(f"{catalog}.{schema}.transactions_raw")

print("Bronze rows:", spark.table(f"{catalog}.{schema}.transactions_raw").count())
