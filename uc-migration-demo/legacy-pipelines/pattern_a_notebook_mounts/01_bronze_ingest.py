# Databricks notebook source
# =====================================================================
# Pattern A - Legacy medallion ingest (Hive metastore + DBFS mounts)
# Target: non-UC workspace / hive_metastore
# =====================================================================

# COMMAND ----------
# Mount landing storage (legacy pattern - credentials in cluster/secret scope)
dbutils.fs.mount(
    source="wasbs://landing@ffstorage.blob.core.windows.net/",
    mount_point="/mnt/landing",
    extra_configs={
        "fs.azure.account.key.ffstorage.blob.core.windows.net": dbutils.secrets.get("ff", "storagekey")
    },
)

# COMMAND ----------
# 2-level namespace on the workspace-local Hive metastore
spark.sql("CREATE DATABASE IF NOT EXISTS portfolio")
spark.sql("USE portfolio")

# COMMAND ----------
# Read raw files directly from the mount path
raw = (
    spark.read.format("csv")
    .option("header", True)
    .load("dbfs:/mnt/landing/transactions/*.csv")
)

# COMMAND ----------
# Persist as a MANAGED Hive metastore table (managed by the workspace HMS)
raw.write.mode("overwrite").saveAsTable("portfolio.transactions_raw")

print("Bronze rows:", spark.table("portfolio.transactions_raw").count())
