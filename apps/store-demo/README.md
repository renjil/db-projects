# 7-Eleven Store Intelligence — Databricks Demo

A complete, deployable retail-operations demo on Databricks. Three personas
(Store Associate, Store Manager, Regional Manager) consume Silver/Gold Unity
Catalog tables built by a DLT pipeline, query a Genie Space in natural
language, see AI-generated sentiment from customer reviews, and view two
Lakeview dashboards.

## What's in this demo

- **Data**: synthetic retail data (10 stores, 200+ articles, 90 days of sales, inventory, write-offs, budgets, reviews) generated locally and loaded into Silver tables.
- **DLT Pipeline**: Silver → Gold transformations and metric views.
- **Jobs**: Daily Gold refresh, one-shot RLS setup, one-shot CFO views setup.
- **Dashboards**: CFO Executive and Store Performance Lakeview dashboards.
- **Genie Space**: NL → SQL over Gold tables (manual creation step).
- **Streamlit App**: persona-based UI with KPI cards, charts, sentiment, and a Genie chat panel.
- **Row-Level Security**: a `silver_user_store_access` table + filters scope each persona's view.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Streamlit App (Databricks App)                                         │
│  Store Associate │ Store Manager │ Regional Manager                     │
├─────────────────────────────────────────────────────────────────────────┤
│  Genie Space   │   Lakeview Dashboards   │   Metric Views               │
├─────────────────────────────────────────────────────────────────────────┤
│  Gold Layer  (DLT pipeline)  +  AI Sentiment (Foundation Model API)     │
├─────────────────────────────────────────────────────────────────────────┤
│  Silver Layer  (DDL + load_data.py)                                     │
├─────────────────────────────────────────────────────────────────────────┤
│  Unity Catalog  ($catalog.$schema)  •  SQL Warehouse  •  RLS            │
└─────────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Databricks workspace with Unity Catalog.
- A running **SQL warehouse** (note its ID).
- **Foundation Model API** access from that warehouse (used by the sentiment view).
- **Databricks CLI** authenticated (`databricks auth login`). Note your profile name.
- Python 3.9+ with `pandas` and `pyarrow` installed locally (for the fast Parquet load path).

## One-time variable setup

Edit `databricks.yml` and set the four variables for your workspace (catalog, schema, warehouse_id, genie_space_id). `genie_space_id` is filled in at step 9 — leave the placeholder for now.

```bash
export DATABRICKS_PROFILE=DEFAULT             # or your CLI profile name
export DATABRICKS_CATALOG=retail_demo
export DATABRICKS_SCHEMA=store_demo
export DATABRICKS_WAREHOUSE_ID=<your-warehouse-id>
```

The bundle and `load_data.py` both read these. Create the catalog/schema once if they don't already exist:

```bash
databricks sql-api execute -p $DATABRICKS_PROFILE \
  --warehouse-id $DATABRICKS_WAREHOUSE_ID \
  --statement "CREATE CATALOG IF NOT EXISTS $DATABRICKS_CATALOG; \
               CREATE SCHEMA  IF NOT EXISTS $DATABRICKS_CATALOG.$DATABRICKS_SCHEMA;"
```

## Deployment sequence

Run these steps in order. Each command is copy-pasteable. **Manual** steps are clearly marked.

| #  | Step | Command | Manual? |
|----|------|---------|---------|
| 1  | Validate bundle | `databricks bundle validate -t dev` | No |
| 2  | Create Silver tables | `databricks sql-api execute -p $DATABRICKS_PROFILE --warehouse-id $DATABRICKS_WAREHOUSE_ID --file src/sql/01_silver_ddl.sql --parameters catalog=$DATABRICKS_CATALOG schema=$DATABRICKS_SCHEMA` | No |
| 3  | Create Gold tables  | `databricks sql-api execute -p $DATABRICKS_PROFILE --warehouse-id $DATABRICKS_WAREHOUSE_ID --file src/sql/02_gold_ddl.sql --parameters catalog=$DATABRICKS_CATALOG schema=$DATABRICKS_SCHEMA` | No |
| 4  | Generate + load Silver data | `python src/setup/load_data.py` | No |
| 5  | Create sentiment view (uses Foundation Model API) | `databricks sql-api execute -p $DATABRICKS_PROFILE --warehouse-id $DATABRICKS_WAREHOUSE_ID --file src/sql/03_sentiment_setup.sql --parameters catalog=$DATABRICKS_CATALOG schema=$DATABRICKS_SCHEMA` | No |
| 6  | Deploy DLT pipeline, jobs, dashboards | `databricks bundle deploy -t dev` | No |
| 7  | Populate Gold layer | `databricks bundle run gold_etl -t dev` | No |
| 8  | Apply Row-Level Security | `databricks bundle run setup_rls -t dev` | No |
| 9  | **Create Genie Space** in the UI → Genie → New Space. Add the 17 Gold tables listed in `src/sql/05_genie_setup.sql`. Copy the new Space ID and set it on the `genie_space_id` variable in `databricks.yml`. | (UI) | **YES** |
| 10 | Apply table COMMENTs for Genie | `databricks sql-api execute -p $DATABRICKS_PROFILE --warehouse-id $DATABRICKS_WAREHOUSE_ID --file src/sql/05_genie_setup.sql --parameters catalog=$DATABRICKS_CATALOG schema=$DATABRICKS_SCHEMA` | No |
| 11 | Create metric views | `databricks sql-api execute -p $DATABRICKS_PROFILE --warehouse-id $DATABRICKS_WAREHOUSE_ID --file src/sql/06_metric_views.sql --parameters catalog=$DATABRICKS_CATALOG schema=$DATABRICKS_SCHEMA` | No |
| 12 | Create CFO views    | `databricks bundle run setup_cfo_views -t dev` | No |
| 13 | **Edit `app-streamlit/app.yaml`** — replace the four `<YOUR_…>` placeholders (warehouse, catalog, schema, Genie Space ID) with your values from steps 1 and 9. | (file edit) | **YES** |
| 14 | Deploy the Streamlit app | `databricks apps deploy --source-code-path app-streamlit --app-name 7eleven-store-intelligence` | No |
| 15 | **Grant app's service principal RLS access** — see snippet below. | (SQL) | **YES** |

### Step 15 — RLS grant for the app service principal

The app runs as a service principal that needs at least one row in `silver_user_store_access` to see any data. Get its email, then insert grants:

```bash
SP_ID=$(databricks apps get 7eleven-store-intelligence -p $DATABRICKS_PROFILE \
        --output json | jq -r '.service_principal_name')

databricks sql-api execute -p $DATABRICKS_PROFILE \
  --warehouse-id $DATABRICKS_WAREHOUSE_ID \
  --statement "INSERT INTO $DATABRICKS_CATALOG.$DATABRICKS_SCHEMA.silver_user_store_access \
               (user_email, store_id, role, access_level, granted_at, granted_by, is_active) \
               SELECT '$SP_ID', store_id, 'App Service Principal', 'READ', \
                      current_timestamp(), 'system', true \
               FROM $DATABRICKS_CATALOG.$DATABRICKS_SCHEMA.silver_stores WHERE is_active = TRUE;"
```

## Dependency chain (at a glance)

```
 1 validate
   │
 2 silver DDL  ─►  3 gold DDL  ─►  4 load data  ─►  5 sentiment view
                                                     │
                                                     ▼
                                          6 bundle deploy (DLT, jobs, dashboards)
                                                     │
                                                     ▼
                                            7 run gold_etl
                                                     │
                                                     ▼
                                            8 run setup_rls
                                                     │
                                                     ▼
                                      9 [MANUAL] create Genie Space ──► fills genie_space_id
                                                     │
                                                     ▼
                                          10 apply Genie COMMENTs
                                                     │
                                                     ▼
                                          11 metric views  ─►  12 CFO views
                                                                  │
                                                                  ▼
                                                       13 [MANUAL] edit app.yaml
                                                                  │
                                                                  ▼
                                                          14 deploy app
                                                                  │
                                                                  ▼
                                                       15 [MANUAL] grant app SP RLS
```

## Manual intervention summary

Three explicit manual steps + one prerequisite:

| Step | What | Why it can't be automated |
|------|------|---------------------------|
| **9**  | Create the Genie Space in the UI; copy its ID into `databricks.yml`. | Genie Space creation isn't yet part of Asset Bundles. |
| **13** | Edit `app-streamlit/app.yaml` to set 4 env vars to your real IDs. | `app.yaml` is read by the Apps runtime, not by the bundle. |
| **15** | Run the RLS INSERT for the app's service principal. | The SP doesn't exist until the app is deployed. |
| (prereq) | Enable Foundation Model API access on your SQL warehouse. | Workspace-admin action, must be done before step 5. |

## Project layout

```
apps/store-demo/
├── README.md                       # this file
├── databricks.yml                  # DAB bundle config + variables
├── .gitignore
│
├── resources/                      # DAB resource definitions
│   ├── pipelines.yml               # DLT pipeline: gold_etl
│   ├── jobs.yml                    # refresh_gold_layer, setup_rls, setup_cfo_views
│   └── dashboards.yml              # CFO Executive + Store Performance
│
├── src/
│   ├── setup/                      # one-time bootstrap
│   │   ├── load_data.py            # generate + load Silver
│   │   └── _data_generator.py      # internal: data-generation routines
│   ├── sql/                        # ordered SQL — some run directly, some via jobs
│   │   ├── 01_silver_ddl.sql
│   │   ├── 02_gold_ddl.sql
│   │   ├── 03_sentiment_setup.sql
│   │   ├── 04_row_level_security.sql       (run by setup_rls job)
│   │   ├── 05_genie_setup.sql
│   │   ├── 06_metric_views.sql
│   │   └── 07_cfo_views.sql                (run by setup_cfo_views job)
│   └── dlt/                        # DLT pipeline source
│       ├── 01_silver_to_gold.sql
│       └── 02_metrics_view.sql
│
├── dashboard/
│   ├── cfo_executive.lvdash.json
│   └── store_performance.lvdash.json
│
└── app-streamlit/                  # Databricks App
    ├── app.py
    ├── app.yaml                    # ← edit before `databricks apps deploy`
    ├── requirements.txt
    ├── assets/  utils/  components/
```

## Troubleshooting

| Symptom | Cause / Fix |
|---------|-------------|
| App shows "No store assigned" | Step 15 wasn't run — grant the app's service principal access in `silver_user_store_access`. |
| `vw_review_sentiment_ai` errors with permission denied | Foundation Model API not enabled on the warehouse — ask a workspace admin. |
| `databricks bundle validate` fails on resources | Ensure all four variables in `databricks.yml` are set; check that `src/sql/04_row_level_security.sql` and `src/sql/07_cfo_views.sql` paths in `resources/jobs.yml` resolve. |
| `load_data.py` fast path fails on volume creation | Re-run with `--method api` to use the JSON-INSERT fallback. |
| `databricks fs cp` fails | Make sure you have `WRITE VOLUME` permission on the schema, or use `--method api`. |

## Teardown

```bash
databricks bundle destroy -t dev -p $DATABRICKS_PROFILE
databricks apps delete 7eleven-store-intelligence -p $DATABRICKS_PROFILE
databricks sql-api execute -p $DATABRICKS_PROFILE \
  --warehouse-id $DATABRICKS_WAREHOUSE_ID \
  --statement "DROP SCHEMA IF EXISTS $DATABRICKS_CATALOG.$DATABRICKS_SCHEMA CASCADE;"
```

Delete the Genie Space manually in the UI.

## License

Internal Databricks demo — not for external distribution.
