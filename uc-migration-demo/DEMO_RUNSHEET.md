# Runsheet - HMS -> Unity Catalog migration demo (field-demo workspace)

**Goal:** reproduce the full legacy -> UC migration end to end in the **FE field-demo workspace**, driven by the `uc-migration` skill. No non-UC workspace needed - we stage the "before" state in the workspace-local `hive_metastore` catalog.

> Reproducible design choices: legacy tables are staged as **managed `hive_metastore` tables** so migration works via `DEEP CLONE` with **no external cloud credentials**. Source files land on a DBFS `/tmp` path to simulate a legacy "mount", and the migrated pipeline reads from a **UC Volume**. `SYNC` (external tables) is shown in the plan/code but not required for this in-workspace run - see the note in Part 5.

---

## Config (set once)

```bash
export DBX_HOST="https://<field-demo-workspace>.cloud.databricks.com"   # fill in
export DBX_PROFILE="fielddemo"
```
```
CATALOG      = acme_uc_demo          # target UC catalog (create, or swap for a writable one)
SCHEMA       = portfolio
LEGACY       = hive_metastore.portfolio
SQL_WAREHOUSE = <a Medium+ serverless SQL warehouse>   # for running SQL / validation
```

---

## Part 0 - Prereqs
- Databricks CLI + Claude Code installed.
- `uc-migration` skill installed (see `uc-migration-skill/INSTALL.md`).
- Auth: `databricks auth login --host "$DBX_HOST" --profile "$DBX_PROFILE"` then `databricks current-user me -p "$DBX_PROFILE"`.
- You can create a catalog in field-demo (or have a writable sandbox catalog to use instead of `ff_uc_demo`).
- A serverless SQL warehouse you can use (size Medium or above per house guidance).

---

## Part 1 - Stage the "before" state (run this notebook in the workspace)

Create a Python notebook in the field-demo workspace and run these cells. This builds a realistic legacy `hive_metastore.portfolio` estate plus the UC target shell.

```python
CATALOG = "acme_uc_demo"; SCHEMA = "portfolio"
DBFS_LANDING = "dbfs:/tmp/ff_uc_demo/landing/transactions"   # simulated legacy "mount"

# --- target UC shell ---
spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA  IF NOT EXISTS {CATALOG}.{SCHEMA}")
spark.sql(f"CREATE VOLUME  IF NOT EXISTS {CATALOG}.{SCHEMA}.landing")

# --- synthetic source data -> simulated mount (DBFS /tmp) ---
df = (spark.range(200000).selectExpr(
    "cast(id as string) as transaction_id",
    "cast(rand()*1000 as int) as account_id",
    "array('EQ','BOND','FX','CASH')[cast(rand()*4 as int)] as instrument",
    "array('BUY','SELL')[cast(rand()*2 as int)] as txn_type",
    "round(rand()*1000000, 2) as amount",
    "'AUD' as currency",
    "timestampadd(DAY, cast(rand()*180 as int), timestamp('2026-01-01')) as txn_ts"))
df.write.mode("overwrite").option("header", True).csv(DBFS_LANDING)

# also copy source into the UC Volume so the MIGRATED pipeline can read it
dbutils.fs.cp(DBFS_LANDING, f"/Volumes/{CATALOG}/{SCHEMA}/landing/transactions", recurse=True)

# --- legacy hive_metastore estate (managed tables) ---
spark.sql("CREATE SCHEMA IF NOT EXISTS hive_metastore.portfolio")
(spark.read.option("header", True).option("inferSchema", True).csv(DBFS_LANDING)
   .write.mode("overwrite").saveAsTable("hive_metastore.portfolio.transactions_raw"))

spark.sql("""CREATE OR REPLACE TABLE hive_metastore.portfolio.transactions_silver AS
  SELECT transaction_id, account_id, instrument, txn_type,
         cast(amount as double) amount, currency, cast(txn_ts as timestamp) txn_ts
  FROM hive_metastore.portfolio.transactions_raw WHERE amount IS NOT NULL""")

spark.sql("""CREATE OR REPLACE TABLE hive_metastore.portfolio.gold_daily AS
  SELECT instrument, to_date(txn_ts) dt, sum(amount) total_amount, count(*) txn_count
  FROM hive_metastore.portfolio.transactions_silver GROUP BY instrument, to_date(txn_ts)""")

# optional legacy grant (best-effort; skips if table ACLs not enabled on HMS)
try:
    spark.sql("GRANT SELECT ON TABLE hive_metastore.portfolio.transactions_silver TO `account users`")
except Exception as e:
    print("grant staging skipped:", e)

for t in ["transactions_raw","transactions_silver","gold_daily"]:
    print(t, spark.table(f"hive_metastore.portfolio.{t}").count())
```

You now have a live legacy estate in `hive_metastore.portfolio` and an empty UC target `ff_uc_demo.portfolio` with a `landing` volume.

---

## Part 2 - Run the migration with the skill (Claude Code, pointed at field-demo)

From the `uc-migration-demo/` folder in Claude Code (auth profile = `fielddemo`):

```
/uc-analyse  legacy-pipelines/pattern_a_notebook_mounts
```
Read-only assessment: inventory, mounts, 2-level names, grants, incompatibilities, risk rating.

```
/uc-plan     legacy-pipelines/pattern_a_notebook_mounts
```
Confirm the target mapping is `hive_metastore.portfolio.*` -> `ff_uc_demo.portfolio.*`, DEEP CLONE for the managed tables, mount -> Volume, grant translation, ordered runbook. (When it asks for the target catalog, answer `ff_uc_demo`.)

```
/uc-migrate  legacy-pipelines/pattern_a_notebook_mounts
```
It will: rewrite the code into `migrated/` (3-level names, Volume paths, no mounts/configs), generate the CLONE SQL + UC grants, and scaffold a DAB. **It stops for your approval.** Review the diff and SQL.

---

## Part 3 - Apply the data migration (reliable path: run the generated SQL)

Take the CLONE + grant SQL the agent produced and run it in a **SQL editor / notebook** on your warehouse (this is the most reliable path; the agent can also execute it if a warehouse is wired up, but copy-run avoids surprises live):

```sql
CREATE TABLE IF NOT EXISTS ff_uc_demo.portfolio.transactions_raw    DEEP CLONE hive_metastore.portfolio.transactions_raw;
CREATE TABLE IF NOT EXISTS ff_uc_demo.portfolio.transactions_silver DEEP CLONE hive_metastore.portfolio.transactions_silver;
CREATE TABLE IF NOT EXISTS ff_uc_demo.portfolio.gold_daily          DEEP CLONE hive_metastore.portfolio.gold_daily;

-- translated grants
GRANT USE CATALOG ON CATALOG ff_uc_demo TO `account users`;
GRANT USE SCHEMA  ON SCHEMA  ff_uc_demo.portfolio TO `account users`;
GRANT SELECT      ON TABLE   ff_uc_demo.portfolio.transactions_silver TO `account users`;
```

---

## Part 4 - (Optional) run the migrated pipeline end to end

Deploy the DAB the agent generated and run it, so you show the *rewritten* pipeline producing UC tables from the Volume:
```bash
cd migrated/<bundle-dir>
databricks bundle validate  -p fielddemo
databricks bundle deploy -t dev -p fielddemo
databricks bundle run <pipeline_name> -t dev -p fielddemo
```
Then in the UI show the pipeline graph + query `ff_uc_demo.portfolio.gold_daily`.

---

## Part 5 - Validate / reconcile

```
/uc-validate hive_metastore.portfolio ff_uc_demo.portfolio
```
Confirms row counts, aggregate checksums, schema parity, grant parity, and greps the migrated code for leftover `hive_metastore` / `dbfs:/mnt` / legacy configs. Everything should match.

Quick manual check:
```sql
SELECT 'legacy' src, count(*) FROM hive_metastore.portfolio.transactions_silver
UNION ALL
SELECT 'uc'    src, count(*) FROM ff_uc_demo.portfolio.transactions_silver;
```

> **Note on SYNC vs CLONE:** in this in-workspace demo the tables are managed, so we use `DEEP CLONE` (no external storage needed). In a real migration, *external* HMS tables migrate with `SYNC TABLE` once their location is a UC External Location - the skill's plan/output shows this path too. Call that out verbally; don't try to `SYNC` a DBFS-root table (UC external tables can't live on DBFS root).

---

## Part 6 - Reset (so you can rerun cleanly)

```python
spark.sql("DROP SCHEMA IF EXISTS hive_metastore.portfolio CASCADE")
spark.sql("DROP SCHEMA IF EXISTS ff_uc_demo.portfolio CASCADE")
dbutils.fs.rm("dbfs:/tmp/ff_uc_demo", recurse=True)
# spark.sql("DROP CATALOG IF EXISTS ff_uc_demo CASCADE")   # only if you created it just for the demo
```
Also remove the generated `migrated/` folder and `databricks bundle destroy -t dev` if you deployed.

---

## Dry-run checklist (day before)
- [ ] Part 1 notebook runs clean; counts print for all 3 tables.
- [ ] `/uc-analyse` and `/uc-plan` produce sensible output pointing at `ff_uc_demo.portfolio`.
- [ ] `/uc-migrate` writes `migrated/` and proposes CLONE SQL + grants (review the diff).
- [ ] CLONE SQL runs; UC tables populated.
- [ ] `/uc-validate` all-green.
- [ ] Full run timed (aim ~15 min); UI tabs pre-opened; fallback recording ready.

## Talking points
- The legacy estate is real (`hive_metastore`), so this is a genuine HMS->UC migration, not a mock.
- The agent applied *Acme patterns* via the custom skill - consistent, reviewable, reconciled.
- Read-only analyse/plan first, human-approved migrate, validated before cutover - safe by design.
- Same skill scales to your real reference pipelines; seed it with them next.
