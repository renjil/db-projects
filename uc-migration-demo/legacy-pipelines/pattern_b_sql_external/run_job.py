"""Pattern B driver - legacy job entrypoint (spark-submit / Jobs task).

Executes pipeline.sql statement-by-statement. Sets a couple of legacy
Hive-metastore-oriented Spark configs that are not needed under UC.
"""
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

# Legacy configs (not required / not honored the same way under UC)
spark.conf.set("spark.databricks.hive.metastore.glueCatalog.enabled", "false")
spark.conf.set("spark.sql.legacy.createHiveTableByDefault", "true")

with open("pipeline.sql") as f:
    for stmt in f.read().split(";"):
        if stmt.strip():
            spark.sql(stmt)

print("Pattern B pipeline complete.")
