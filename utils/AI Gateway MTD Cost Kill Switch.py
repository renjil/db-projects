# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
# MAGIC %md
# MAGIC # AI Gateway - Cost-Based Kill Switch
# MAGIC
# MAGIC Checks month-to-date (MTD) spend on a Databricks AI Gateway endpoint and, if it exceeds a configured USD threshold,
# MAGIC PATCHes the endpoint's rate limit to **0 TPM** so all subsequent inference calls are blocked.
# MAGIC
# MAGIC **Designed to run as a parameterised job** - one task per endpoint, each with its own threshold.
# MAGIC
# MAGIC ## Parameters
# MAGIC
# MAGIC | Widget | Purpose |
# MAGIC |---|---|
# MAGIC | `endpoint_name` | AI Gateway endpoint to monitor and gate (e.g. `rh-claude`) |
# MAGIC | `cost_threshold_usd` | If MTD spend exceeds this value (USD), apply the kill switch |
# MAGIC | `dry_run` | `true` = only report, do NOT call the API. `false` = enforce. |
# MAGIC
# MAGIC ## Behavior
# MAGIC
# MAGIC - Reads `system.billing.usage` joined to `system.billing.list_prices` for **1st-of-current-month -> today**.
# MAGIC - Filters on `usage_metadata.ai_gateway.endpoint_name` (the AI Gateway endpoint name, not the destination model).
# MAGIC - If over threshold and `dry_run=false`, PATCHes `/api/ai-gateway/v2/endpoints/<name>` to `{key: ENDPOINT, renewal_period: MINUTE, tokens: 0}`.
# MAGIC - When the kill switch is active, callers receive **HTTP 403 `PERMISSION_DENIED`** (not 429).
# MAGIC - Propagation is roughly 10 seconds.
# MAGIC
# MAGIC ## Notes
# MAGIC
# MAGIC - System billing data has a delay of up to a few hours. The check is a safety net, not a real-time meter.
# MAGIC - To restore the endpoint after a kill, run the `Unblock` cell at the bottom of this notebook with a non-zero TPM.

# COMMAND ----------

# MAGIC %md ## 1. Parameters

# COMMAND ----------

dbutils.widgets.text("endpoint_name", "rh-claude", "AI Gateway Endpoint Name")
dbutils.widgets.text("cost_threshold_usd", "100.00", "Cost Threshold (USD, MTD)")
dbutils.widgets.dropdown("dry_run", "true", ["true", "false"], "Dry Run (do not call API)")

endpoint_name = dbutils.widgets.get("endpoint_name").strip()
cost_threshold_usd = float(dbutils.widgets.get("cost_threshold_usd"))
dry_run = dbutils.widgets.get("dry_run").lower() == "true"

ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
workspace_url = ctx.apiUrl().get()
api_token = ctx.apiToken().get()

print(f"Endpoint        : {endpoint_name}")
print(f"Cost threshold  : ${cost_threshold_usd:,.2f} USD (month-to-date)")
print(f"Dry run         : {dry_run}")
print(f"Workspace       : {workspace_url}")

# COMMAND ----------

# MAGIC %md ## 2. Compute MTD cost for the endpoint
# MAGIC
# MAGIC Joins `system.billing.usage` to `system.billing.list_prices` so DBU usage is converted to USD via the **effective list price**
# MAGIC at the time the usage was incurred (handles mid-month price changes correctly).

# COMMAND ----------

cost_df = spark.sql(
    """
    SELECT
      u.usage_metadata.ai_gateway.endpoint_name AS endpoint_name,
      u.sku_name,
      u.usage_unit,
      SUM(u.usage_quantity)                                                   AS total_units,
      SUM(u.usage_quantity * COALESCE(p.pricing.effective_list.default,
                                       p.pricing.default))                    AS total_cost_usd,
      MIN(u.usage_date)                                                       AS first_usage_date,
      MAX(u.usage_date)                                                       AS last_usage_date
    FROM system.billing.usage u
    LEFT JOIN system.billing.list_prices p
      ON  u.sku_name   = p.sku_name
      AND u.cloud      = p.cloud
      AND u.usage_unit = p.usage_unit
      AND u.usage_end_time >= p.price_start_time
      AND (p.price_end_time IS NULL OR u.usage_end_time < p.price_end_time)
    WHERE u.usage_metadata.ai_gateway.endpoint_name = :endpoint_name
      AND u.usage_date >= date_trunc('MONTH', current_date())
      AND u.usage_date <= current_date()
    GROUP BY u.usage_metadata.ai_gateway.endpoint_name, u.sku_name, u.usage_unit
    ORDER BY total_cost_usd DESC
    """,
    args={"endpoint_name": endpoint_name},
)

display(cost_df)

# COMMAND ----------

row = cost_df.agg({"total_cost_usd": "sum"}).first()
total_cost_usd = float(row[0] or 0.0)

period_start = spark.sql("SELECT date_trunc('MONTH', current_date()) AS d").first()[0]
period_end   = spark.sql("SELECT current_date() AS d").first()[0]

print(f"MTD window      : {period_start} -> {period_end}")
print(f"MTD cost        : ${total_cost_usd:,.4f} USD")
print(f"Threshold       : ${cost_threshold_usd:,.2f} USD")
print(f"Over threshold? : {total_cost_usd > cost_threshold_usd}")

if cost_df.count() == 0:
    print("\nNo billing rows found for this endpoint this month.")
    print("Reasons this can happen:")
    print("  - The endpoint has never been called this month.")
    print("  - Usage tracking is not enabled on the endpoint.")
    print("  - Billing data ingestion delay (up to a few hours).")
    print("  - The endpoint name was created in the UI but renamed since billing rows were emitted.")

# COMMAND ----------

# MAGIC %md ## 3. Enforce - PATCH `tokens: 0` if over threshold

# COMMAND ----------

import json
import time
import urllib.request
import urllib.error


def get_endpoint(workspace_url: str, token: str, name: str) -> dict:
    req = urllib.request.Request(
        f"{workspace_url.rstrip('/')}/api/ai-gateway/v2/endpoints/{name}",
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def set_tpm(workspace_url: str, token: str, name: str, tpm: int) -> dict:
    body = json.dumps(
        {
            "config": {
                "rate_limits": [
                    {"key": "ENDPOINT", "renewal_period": "MINUTE", "tokens": int(tpm)}
                ]
            }
        }
    ).encode()
    req = urllib.request.Request(
        f"{workspace_url.rstrip('/')}/api/ai-gateway/v2/endpoints/{name}?update_mask=config.rate_limits",
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="PATCH",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def current_rate_limit(endpoint_obj: dict) -> dict:
    return (endpoint_obj.get("config", {}).get("rate_limits") or [{}])[0]


try:
    current = get_endpoint(workspace_url, api_token, endpoint_name)
except urllib.error.HTTPError as e:
    print(f"GET failed: HTTP {e.code} - {e.read().decode()[:500]}")
    raise
except Exception as e:
    print(f"GET failed: {e}")
    raise

print(f"Current rate limit on '{endpoint_name}': {current_rate_limit(current)}")

if total_cost_usd > cost_threshold_usd:
    print(
        f"\nMTD cost ${total_cost_usd:,.4f} EXCEEDS threshold ${cost_threshold_usd:,.2f}."
    )
    if dry_run:
        print("[dry_run=true] - NOT calling the API. Set dry_run=false to enforce.")
        dbutils.notebook.exit(
            json.dumps(
                {
                    "endpoint": endpoint_name,
                    "mtd_cost_usd": round(total_cost_usd, 4),
                    "threshold_usd": cost_threshold_usd,
                    "action": "would_block",
                    "dry_run": True,
                }
            )
        )
    else:
        print("Applying kill switch: PATCH tokens=0 ...")
        result = set_tpm(workspace_url, api_token, endpoint_name, 0)
        new_limit = current_rate_limit(result.get("response", result))
        print(f"PATCH OK. New rate limit: {new_limit}")
        print("Allow ~10s for propagation. Callers will receive HTTP 403 PERMISSION_DENIED.")
        dbutils.notebook.exit(
            json.dumps(
                {
                    "endpoint": endpoint_name,
                    "mtd_cost_usd": round(total_cost_usd, 4),
                    "threshold_usd": cost_threshold_usd,
                    "action": "blocked",
                    "applied_rate_limit": new_limit,
                }
            )
        )
else:
    print(
        f"\nMTD cost ${total_cost_usd:,.4f} is within threshold ${cost_threshold_usd:,.2f}. No action."
    )
    dbutils.notebook.exit(
        json.dumps(
            {
                "endpoint": endpoint_name,
                "mtd_cost_usd": round(total_cost_usd, 4),
                "threshold_usd": cost_threshold_usd,
                "action": "no_change",
            }
        )
    )

# COMMAND ----------

# MAGIC %md ## 4. (Optional) Unblock - restore TPM after a kill
# MAGIC
# MAGIC Run this cell **manually** when you want to restore an endpoint that was blocked.
# MAGIC Change `restore_tpm` to your desired TPM value (e.g. 5000).

# COMMAND ----------

# Uncomment and run manually to restore.
# restore_tpm = 5000
# result = set_tpm(workspace_url, api_token, endpoint_name, restore_tpm)
# print("Restored rate limit:", current_rate_limit(result.get("response", result)))
