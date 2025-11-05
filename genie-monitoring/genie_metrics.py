# Databricks notebook source
# MAGIC %md
# MAGIC
# MAGIC # Genie Space Usage Metrics Ingestion
# MAGIC
# MAGIC Run this notebook to ingest data from Databricks APIs.
# MAGIC Data being ingested are:
# MAGIC - Genie Space details - [ListSpaces](https://docs.databricks.com/api/workspace/genie/listspaces)
# MAGIC - Conversations per Space - [ListConversations](https://docs.databricks.com/api/workspace/genie/listconversations)
# MAGIC - Messages per space - [ListConversationsMessages](https://docs.databricks.com/api/workspace/genie/listconversationmessages)
# MAGIC
# MAGIC This notebook also creates Gold Tables for dashboard consumption.
# MAGIC
# MAGIC The Dashboard Genie Usage Analytics also makes use of data from [System Tables Audit events](https://docs.databricks.com/aws/en/admin/account-settings/audit-logs#aibi-genie-events).
# MAGIC
# MAGIC You can extend and adopt the metrics either using data from the API or System Tables.
# MAGIC
# MAGIC

# COMMAND ----------

# DBTITLE 1,User to specify catalog and schema for storing data
dbutils.widgets.text("catalog", "renjiharold_demo", "Catalog")
dbutils.widgets.text("schema", "genie_analytics", "Schema")

# COMMAND ----------

# DBTITLE 1,Imports and Config
# %pip install databricks-sdk==0.33.0

from databricks.sdk import WorkspaceClient
from databricks.sdk.core import ApiClient
from pyspark.sql import functions as F, types as T
import json, time
from typing import Dict, Iterable, List

CATALOG = dbutils.widgets.get("catalog").strip()
SCHEMA  = dbutils.widgets.get("schema").strip()

SPACES_TABLE = f"{CATALOG}.{SCHEMA}.genie_spaces"
CONV_TABLE   = f"{CATALOG}.{SCHEMA}.genie_conversations"
MSG_TABLE    = f"{CATALOG}.{SCHEMA}.genie_messages"

PAGE_SIZE = 100
THROTTLE_S = 0.15  # polite pacing to avoid 429s

w = WorkspaceClient()
api: ApiClient = w.api_client

spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"USE CATALOG {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
spark.sql(f"USE {SCHEMA}")


# COMMAND ----------

# DBTITLE 1,REST API Helpers
def _paged_get(path: str, items_key: str) -> Iterable[Dict]:
    page_token = None
    while True:
        q = {"page_size": PAGE_SIZE}
        if page_token:
            q["page_token"] = page_token
        resp = api.do("GET", path, query=q)
        items = resp.get(items_key, [])
        for it in items:
            yield it
        page_token = resp.get("next_page_token")
        if not page_token:
            break

def list_spaces() -> List[Dict]:
    # GET /api/2.0/genie/spaces  (List Genie spaces)
    # Docs: https://docs.databricks.com/api/workspace/genie/listspaces
    return list(_paged_get("/api/2.0/genie/spaces", "spaces"))

def list_conversations(space_id: str) -> List[Dict]:
    # GET /api/2.0/genie/spaces/{space_id}/conversations  (include_all across users)
    # Docs: https://docs.databricks.com/api/workspace/genie/listconversations
    return list(_paged_get(f"/api/2.0/genie/spaces/{space_id}/conversations?include_all=true", "conversations"))

def list_conversation_messages(space_id: str, conversation_id: str) -> List[Dict]:
    # GET /api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages
    # Docs: https://docs.databricks.com/api/workspace/genie/listconversationmessages
    return list(_paged_get(f"/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages", "messages"))


# COMMAND ----------

# DBTITLE 1,Ingest Spaces data
spaces = list_spaces()

spaces_df = spark.createDataFrame(
    [(json.dumps(s),) for s in spaces],
    schema=T.StructType([T.StructField("payload_json", T.StringType(), False)])
).withColumn("ingested_at", F.current_timestamp()) \
 .withColumn("space_id", F.get_json_object("payload_json", "$.space_id")) \
 .withColumn("title",    F.get_json_object("payload_json", "$.title")) \
 .withColumn("description", F.get_json_object("payload_json", "$.description")) \
 .withColumn("warehouse_id", F.get_json_object("payload_json", "$.warehouse_id"))

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {SPACES_TABLE} (
  space_id STRING,
  title STRING,
  description STRING,
  warehouse_id STRING,
  payload_json STRING,
  ingested_at TIMESTAMP
) USING DELTA
""")

spaces_df.select("space_id","title","description","warehouse_id","payload_json","ingested_at") \
    .dropna(subset=["space_id"]) \
    .dropDuplicates(["space_id"]) \
    .createOrReplaceTempView("_spaces_incoming")

spark.sql(f"""
MERGE INTO {SPACES_TABLE} t
USING _spaces_incoming s
ON t.space_id = s.space_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
""")


# COMMAND ----------

# DBTITLE 1,Ingest Conversation data
all_convs = []

# space id's for testing. Remove for PROD
space_ids = [
    {"space_id": "01f08d8be94b1fec8bde6037d5eaf022"},
    {"space_id": "01f0892583d31d2da542584ff87dcf62"},
    {"space_id": "01f08799e3b3163984675dd16cd34c8e"},
]

for s in space_ids: # replace spaces with space_ids for TEST
    sid = s.get("space_id")
    if not sid: 
        continue
    convs = list_conversations(sid)  # include_all=true
    for c in convs:
        all_convs.append((sid, json.dumps(c)))
    time.sleep(THROTTLE_S)

convs_df = spark.createDataFrame(
    all_convs,
    schema=T.StructType([
        T.StructField("space_id", T.StringType(), False),
        T.StructField("payload_json", T.StringType(), False),
    ])
).withColumn("ingested_at", F.current_timestamp())

# Flatten common fields from conversation payload
convs_flat = (convs_df
  .withColumn("conversation_id", F.get_json_object("payload_json", "$.conversation_id"))
  .withColumn("title", F.get_json_object("payload_json", "$.title"))
  .withColumn("created_timestamp", F.from_unixtime((F.get_json_object("payload_json", "$.created_timestamp"))/1000))
  .select(
      "space_id","conversation_id","title",
      "created_timestamp","ingested_at","payload_json"
  )
  .dropna(subset=["conversation_id"])
  .dropDuplicates(["conversation_id"])
)

spark.sql(f"""
CREATE TABLE IF NOT EXISTS {CONV_TABLE} (
  space_id STRING,
  conversation_id STRING,
  title STRING,
  created_timestamp TIMESTAMP,
  ingested_at TIMESTAMP,
  payload_json STRING
) USING DELTA
PARTITIONED BY (space_id)
""")

convs_flat.createOrReplaceTempView("_convs_incoming")
spark.sql(f"""
MERGE INTO {CONV_TABLE} t
USING _convs_incoming s
ON t.conversation_id = s.conversation_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
""")


# COMMAND ----------

# DBTITLE 1,Ingest messages data
conv_ids = [r["conversation_id"] for r in spark.table(CONV_TABLE).select("conversation_id").collect()]
space_by_conv = {r["conversation_id"]: r["space_id"] for r in spark.table(CONV_TABLE).select("conversation_id","space_id").collect()}

rows = []
for cid in conv_ids:
    sid = space_by_conv[cid]
    msgs = list_conversation_messages(sid, cid)
    for m in msgs:
        rows.append((sid, cid, json.dumps(m)))
    time.sleep(THROTTLE_S)

msgs_df = spark.createDataFrame(
    rows,
    schema=T.StructType([
        T.StructField("space_id", T.StringType(), False),
        T.StructField("conversation_id", T.StringType(), False),
        T.StructField("payload_json", T.StringType(), False),
    ])
).withColumn("ingested_at", F.current_timestamp())

# Flatten common message fields
messages_flat = (
    msgs_df
    .withColumn("message_id", F.get_json_object("payload_json", "$.message_id"))
    .withColumn("author_id", F.get_json_object("payload_json", "$.user_id"))
    .withColumn("created_timestamp",
        F.from_unixtime((F.get_json_object("payload_json", "$.created_timestamp"))/1000)
    )
    .withColumn("last_updated_timestamp",
        F.from_unixtime((F.get_json_object("payload_json", "$.last_updated_timestamp"))/1000)
    )
    .withColumn("content", F.get_json_object("payload_json", "$.content"))
    .select(
        "space_id","conversation_id","message_id","author_id",
        "created_timestamp", "last_updated_timestamp", "content", "ingested_at", "payload_json"
    )
    .dropna(subset=["message_id"])
    .dropDuplicates(["message_id"])
)


# COMMAND ----------

# DBTITLE 1,Get User Details
ids = [r["author_id"] for r in messages_flat.select("author_id").distinct().collect()]

def get_user_details(uid):
    try:
        u = w.users.get(uid)
        return (u.id, getattr(u, "display_name", None), getattr(u, "user_name", None), getattr(u, "active", None))
    except Exception:
        return None

user_id_list = [get_user_details(uid) for uid in ids]

lookup_df = spark.createDataFrame(
    user_id_list,
    schema=T.StructType([
        T.StructField("user_id", T.StringType()),
        T.StructField("display_name", T.StringType()),
        T.StructField("user_email", T.StringType()),
        T.StructField("active", T.BooleanType()),
    ])
)
lookup_df.display()

# COMMAND ----------

df_enriched = (
    messages_flat.alias("m")
    .join(
        F.broadcast(lookup_df).alias("u"),
        F.col("m.author_id") == F.col("u.user_id"),
        "left",
    )
    .withColumn("author_name", F.col("u.display_name"))
    .withColumn("author_email", F.col("u.user_email"))
    .select(
        "space_id",
        "conversation_id",
        "message_id",
        "author_id",
        "author_name",
        "author_email",
        "created_timestamp",
        "last_updated_timestamp",
        "content",
        "ingested_at",
        "payload_json"
    )
)

spark.sql(
    f"""
CREATE TABLE IF NOT EXISTS {MSG_TABLE} (
  space_id STRING,
  conversation_id STRING,
  message_id STRING,
  author_id STRING,
  author_name STRING,
  author_email STRING,
  created_timestamp TIMESTAMP,
  last_updated_timestamp TIMESTAMP,
  content STRING,
  ingested_at TIMESTAMP,
  payload_json STRING
) USING DELTA
PARTITIONED BY (space_id)
"""
)

df_enriched.createOrReplaceTempView("_msgs_incoming")
spark.sql(
    f"""
MERGE INTO {MSG_TABLE} t
USING _msgs_incoming s
ON t.message_id = s.message_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
"""
)

display(spark.table(MSG_TABLE).orderBy(F.desc("created_timestamp")).limit(20))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Gold Tables for Dashboard 

# COMMAND ----------

# MAGIC %sql
# MAGIC USE CATALOG ${catalog};
# MAGIC USE ${schema};

# COMMAND ----------

# DBTITLE 1,Total Conversations By Day
# MAGIC %sql
# MAGIC -- Total conversations by day (last 90d)
# MAGIC CREATE OR REPLACE TABLE g_conv_last_90d AS
# MAGIC SELECT
# MAGIC   c.space_id, 
# MAGIC   s.title,
# MAGIC   DATE_TRUNC('day', c.created_timestamp) AS day,
# MAGIC   COUNT(c.conversation_id) AS conversations
# MAGIC FROM genie_conversations c
# MAGIC JOIN genie_spaces s on c.space_id = s.space_id
# MAGIC WHERE c.created_timestamp >= DATEADD(day, -90, CURRENT_TIMESTAMP())
# MAGIC GROUP BY 1,2,3
# MAGIC ORDER BY 1;

# COMMAND ----------

# DBTITLE 1,Daily unique users (by creator) last 90d
# MAGIC %sql
# MAGIC -- Daily unique users (by creator) last 90d
# MAGIC CREATE OR REPLACE TABLE g_daily_unique_creators_last_90d AS
# MAGIC SELECT
# MAGIC   m.space_id,     
# MAGIC   s.title,
# MAGIC   DATE_TRUNC('day', m.created_timestamp) AS day,
# MAGIC   COUNT(DISTINCT author_id) AS unique_creators
# MAGIC FROM genie_messages m
# MAGIC JOIN genie_spaces s on m.space_id = s.space_id
# MAGIC WHERE m.created_timestamp >= DATEADD(day, -90, CURRENT_TIMESTAMP())
# MAGIC GROUP BY 1,2,3
# MAGIC ORDER BY 1;

# COMMAND ----------

# DBTITLE 1,Top users by conversations (last 90d)
# MAGIC %sql
# MAGIC -- Top users by conversations (last 90d)
# MAGIC CREATE OR REPLACE TABLE g_top_creators_90d AS
# MAGIC SELECT
# MAGIC   m.space_id,     
# MAGIC   s.title,
# MAGIC   m.author_name AS user,
# MAGIC   COUNT(DISTINCT conversation_id) AS conversation_count
# MAGIC FROM genie_messages m
# MAGIC JOIN genie_spaces s on m.space_id = s.space_id
# MAGIC WHERE m.created_timestamp >= DATEADD(day, -90, CURRENT_TIMESTAMP())
# MAGIC GROUP BY 1,2,3
# MAGIC ORDER BY 4 DESC;

# COMMAND ----------

# DBTITLE 1,Messages per conversation (last 90d)
# MAGIC %sql
# MAGIC -- Messages per conversation (last 90d)
# MAGIC CREATE OR REPLACE TABLE g_messages_per_conversation_90d AS
# MAGIC SELECT
# MAGIC   c.conversation_id,
# MAGIC   c.title AS title,
# MAGIC   m.author_name AS user,
# MAGIC   COUNT(m.message_id) AS messages,
# MAGIC   MIN(m.created_timestamp) AS first_msg_ts,
# MAGIC   MAX(m.created_timestamp) AS last_msg_ts,
# MAGIC   (UNIX_TIMESTAMP(MAX(m.created_timestamp)) - UNIX_TIMESTAMP(MIN(m.created_timestamp))) / 60.0 AS duration_min
# MAGIC FROM genie_conversations c
# MAGIC LEFT JOIN genie_messages m
# MAGIC   ON m.conversation_id = c.conversation_id
# MAGIC WHERE c.created_timestamp >= DATEADD(day, -30, CURRENT_TIMESTAMP())
# MAGIC GROUP BY c.conversation_id, c.title, m.author_name
# MAGIC ORDER BY duration_min DESC;

# COMMAND ----------

# DBTITLE 1,Conversation start hour histogram (last 90d)
# MAGIC %sql
# MAGIC -- Conversation start hour histogram (last 90d)
# MAGIC CREATE OR REPLACE TABLE g_conversation_hour_hist_90d AS
# MAGIC SELECT
# MAGIC   c.space_id,
# MAGIC   s.title,
# MAGIC   HOUR(c.created_timestamp) AS hour_of_day,
# MAGIC   COUNT(*) AS conversations
# MAGIC FROM genie_conversations c
# MAGIC JOIN genie_spaces s on c.space_id = s.space_id
# MAGIC WHERE c.created_timestamp >= DATEADD(day, -30, CURRENT_TIMESTAMP())
# MAGIC GROUP BY 1,2,3
# MAGIC ORDER BY 1;
