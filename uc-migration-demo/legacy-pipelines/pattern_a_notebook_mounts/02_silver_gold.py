# Databricks notebook source
# =====================================================================
# Pattern A - Silver + Gold (Hive metastore + DBFS mounts)
# =====================================================================

# COMMAND ----------
spark.sql("USE portfolio")

# COMMAND ----------
# Silver: cleanse, written as another managed HMS table (2-level name)
silver = spark.sql(
    """
    SELECT CAST(transaction_id AS STRING) AS transaction_id,
           account_id,
           instrument,
           txn_type,
           CAST(amount AS DOUBLE) AS amount,
           currency,
           CAST(txn_ts AS TIMESTAMP) AS txn_ts
    FROM portfolio.transactions_raw
    WHERE amount IS NOT NULL
    """
)
silver.write.mode("overwrite").saveAsTable("portfolio.transactions_silver")

# COMMAND ----------
# Gold: aggregate written to a mount path, then registered as an EXTERNAL table
gold = spark.sql(
    """
    SELECT instrument,
           to_date(txn_ts) AS dt,
           SUM(amount)     AS total_amount,
           COUNT(*)        AS txn_count
    FROM portfolio.transactions_silver
    GROUP BY instrument, to_date(txn_ts)
    """
)
(
    gold.write.mode("overwrite")
    .format("parquet")
    .save("dbfs:/mnt/curated/portfolio/gold_daily")
)

spark.sql(
    """
    CREATE TABLE IF NOT EXISTS portfolio.gold_daily
    USING PARQUET
    LOCATION 'dbfs:/mnt/curated/portfolio/gold_daily'
    """
)

# COMMAND ----------
# Legacy Hive-style grant on the managed table
spark.sql("GRANT SELECT ON TABLE portfolio.transactions_silver TO `portfolio-analysts`")
