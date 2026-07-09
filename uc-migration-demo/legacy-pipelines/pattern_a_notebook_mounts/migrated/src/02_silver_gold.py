# Databricks notebook source
# =====================================================================
# Pattern A - Silver + Gold (Unity Catalog)
# Migrated: 3-level names, managed Delta throughout (gold no longer
# external PARQUET on a mount), UC grants.
# =====================================================================

# COMMAND ----------
dbutils.widgets.text("catalog", "renjiharold_demo")
dbutils.widgets.text("schema", "portfolio")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")

spark.sql(f"USE CATALOG {catalog}")
spark.sql(f"USE SCHEMA {schema}")

# COMMAND ----------
# Silver: cleanse, written as a UC-managed Delta table (3-level name)
silver = spark.sql(
    f"""
    SELECT CAST(transaction_id AS STRING) AS transaction_id,
           account_id,
           instrument,
           txn_type,
           CAST(amount AS DOUBLE) AS amount,
           currency,
           CAST(txn_ts AS TIMESTAMP) AS txn_ts
    FROM {catalog}.{schema}.transactions_raw
    WHERE amount IS NOT NULL
    """
)
silver.write.mode("overwrite").saveAsTable(f"{catalog}.{schema}.transactions_silver")

# COMMAND ----------
# Gold: aggregate written as a UC-managed Delta table.
# (Was: parquet .save() to dbfs:/mnt/curated + external CREATE TABLE USING PARQUET.)
gold = spark.sql(
    f"""
    SELECT instrument,
           to_date(txn_ts) AS dt,
           SUM(amount)     AS total_amount,
           COUNT(*)        AS txn_count
    FROM {catalog}.{schema}.transactions_silver
    GROUP BY instrument, to_date(txn_ts)
    """
)
gold.write.mode("overwrite").saveAsTable(f"{catalog}.{schema}.gold_daily")

# COMMAND ----------
# UC grants applied out-of-band via sql/03_grants.sql (idempotent).
# Left here as a comment for traceability; the pipeline does not manage grants.
# GRANT SELECT ON TABLE renjiharold_demo.portfolio.transactions_silver TO `portfolio-analysts`;
