# Store Intelligence — Databricks Demo

A complete, deployable retail-operations demo on Databricks. Three personas
(Store Associate, Store Manager, Regional Manager) consume Silver/Gold Unity
Catalog tables built by a DLT pipeline, query a Genie Space in natural
language, see AI-generated sentiment from customer reviews, and view two
Lakeview dashboards.

## What's in this demo

- **Data**: synthetic retail data (10 stores, 200+ articles, 90 days of sales, inventory, write-offs, budgets, reviews) generated and loaded on serverless compute.
- **DLT Pipeline**: Silver → Gold transformations and metric views.
- **Jobs**: One orchestrator (`setup_all`) plus a scheduled Gold refresh.
- **Dashboards**: CFO Executive and Store Performance Lakeview dashboards.
- **Genie Space**: NL → SQL over Gold tables.
- **Streamlit App**: persona-based UI with KPI cards, charts, sentiment, and a Genie chat panel.
- **Row-Level Security**: a `silver_user_store_access` table + filters scope each persona's view.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Streamlit App (Databricks App, deployed by the bundle)                 │
│  Store Associate │ Store Manager │ Regional Manager                     │
├─────────────────────────────────────────────────────────────────────────┤
│  Genie Space   │   Lakeview Dashboards   │   Metric Views               │
├─────────────────────────────────────────────────────────────────────────┤
│  Gold Layer  (DLT pipeline)  +  AI Sentiment (Foundation Model API)     │
├─────────────────────────────────────────────────────────────────────────┤
│  Silver Layer  (SQL notebooks + serverless load_data notebook)          │
├─────────────────────────────────────────────────────────────────────────┤
│  Unity Catalog  (${catalog}.${schema})  •  SQL Warehouse  •  RLS        │
└─────────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

The customer only needs:

- **Databricks CLI** installed and authenticated against the target workspace. From a terminal:

  ```bash
  # Replace with your workspace URL and a profile name of your choice.
  databricks auth login \
    --host https://<your-workspace>.cloud.databricks.com \
    --profile <your-profile-name>

  # Verify the profile resolves to the expected workspace and user.
  databricks auth describe -p <your-profile-name>

  # (Optional) Make every subsequent CLI / bundle command use this profile by default.
  export DATABRICKS_CONFIG_PROFILE=<your-profile-name>
  ```

  The bundle uses whatever profile is set in `DATABRICKS_CONFIG_PROFILE` (or pass `-p <profile>` per command). Without one of these, the CLI uses the `DEFAULT` profile from `~/.databrickscfg`.

- **A pre-existing Unity Catalog** (customer brings their own — the bundle does not create it).
- **A SQL warehouse** (Serverless preferred). Note its ID.
- **Foundation Model API** access from the workspace (used by the sentiment view).

That's it. No local Python, no `pip install`, no `databricks api post`.

## One-time edit

Open `databricks.yml` and replace the three `CHANGE_ME_…` defaults under `variables:` with your real values:

| Variable | What |
|---|---|
| `catalog` | Existing UC catalog name. |
| `schema` | Schema the bundle will create inside that catalog. |
| `warehouse_id` | SQL warehouse ID. |

Then open `app-streamlit/app.yaml` and set the four env values there too (same `catalog`, `schema`, `warehouse_id`, plus `GENIE_SPACE_ID` once you have it from step 4). The Apps runtime reads `app.yaml` directly — it does not pick up bundle variables.

## Deployment

Three commands. One manual step.

| # | Action | Manual? |
|---|---|---|
| 1 | `databricks bundle deploy -t dev` | No — bundle creates the app resource (with its service principal), DLT pipeline, all jobs, and dashboards. |
| 2 | `databricks bundle run setup_all -t dev` | No — one orchestrator job runs the full chain on serverless: silver DDL → load data → sentiment → Gold ETL (DLT) → RLS (grants the app SP UC privileges + adds its RLS row) → Genie comments → metric views → CFO views. |
| 3 | Start the app, then push the Streamlit source — see snippet below. | No |
| 4 | **Create the Genie Space and grant the app SP access** — see snippet below. | **YES** |

### Step 3 — Start the app, then push source

`databricks apps deploy` requires the app to be in **RUNNING** state, so start it first:

```bash
# 1. Start the app's compute (no-op if already running).
databricks apps start 7eleven-store-intelligence

# 2. Push the Streamlit source from the bundle's workspace upload path.
databricks apps deploy 7eleven-store-intelligence \
  --source-code-path "/Workspace/Users/$(databricks current-user me -o json | jq -r .userName)/.bundle/7eleven-store-intelligence/dev/files/app-streamlit"
```

(If your CLI isn't using `DATABRICKS_CONFIG_PROFILE`, append `-p <your-profile>` to both commands.)

### Step 4 — Create the Genie Space, grant the app SP, then re-deploy

In the Databricks UI:

1. **Genie → New Space** → name it (e.g. "Intelligent Store Assistant").
2. **Add the 17 Gold tables** listed in the comment block at the top of `src/sql/04_genie_setup.sql` (`gold_daily_store_summary`, `gold_category_performance`, `gold_article_apsd`, … 17 total).
3. **Open the Space's "Share" / permissions dialog** and grant the **app's service principal** at least **`CAN RUN`** on the Space. Without this, the app gets a permission error when calling Genie even if `GENIE_SPACE_ID` is set. Find the SP from:
   ```bash
   databricks apps get 7eleven-store-intelligence \
     -o json | jq -r '.service_principal_client_id, .service_principal_name'
   ```
   In the Share dialog, type either the UUID or the SP display name (`app-<id> 7eleven-store-intelligence`) and pick `CAN RUN`.
4. **Copy the Space ID** from its URL (the long hex after `/spaces/`) into `app-streamlit/app.yaml` as `GENIE_SPACE_ID`.
5. Re-run `databricks bundle deploy -t dev` (uploads the updated `app.yaml`) then re-run the `databricks apps deploy` line from step 3 (so the app picks up the new env var).

## Dependency chain (at a glance)

```
 [1] bundle deploy
       │  registers: app (+ its SP), DLT pipeline, all jobs, dashboards
       ▼
 [2] bundle run setup_all
       │  silver DDL → load data → sentiment → gold_etl (DLT) → RLS
       │  → genie comments → metric views → CFO views
       │  (RLS task auto-grants the app SP UC privileges + RLS row)
       ▼
 [3] apps deploy (push Streamlit source)
       │
       ▼
 [4] (MANUAL) create Genie Space, set GENIE_SPACE_ID in app-streamlit/app.yaml,
              re-run bundle deploy + apps deploy
       │
       ▼
   App is live; each persona sees their scoped data.
```

## Project layout

```
apps/store-demo/
├── README.md                       # this file
├── databricks.yml                  # bundle config + variables
├── .gitignore
│
├── resources/                      # everything the bundle deploys
│   ├── pipelines.yml               # DLT pipeline: gold_etl
│   ├── jobs.yml                    # setup_all orchestrator + refresh_gold_layer
│   ├── dashboards.yml              # CFO Executive + Store Performance
│   └── apps.yml                    # Streamlit app + env-var + warehouse binding
│
├── src/
│   ├── setup/
│   │   ├── load_data.py            # NOTEBOOK: generates data, writes Silver via Spark
│   │   └── _data_generator.py      # library imported by load_data
│   ├── sql/                        # SQL NOTEBOOKS — each runs on the warehouse
│   │   ├── 01_silver_ddl.sql       (silver_ddl task)
│   │   ├── 02_gold_ddl.sql         (gold_ddl task)
│   │   ├── 03_sentiment_setup.sql  (sentiment task)
│   │   ├── 04_row_level_security.sql (rls task)
│   │   ├── 05_genie_setup.sql      (genie_comments task)
│   │   ├── 06_metric_views.sql     (metric_views task)
│   │   └── 07_cfo_views.sql        (cfo_views task)
│   └── dlt/                        # DLT pipeline source
│       ├── 01_silver_to_gold.sql
│       └── 02_metrics_view.sql
│
├── dashboard/
│   ├── cfo_executive.lvdash.json
│   └── store_performance.lvdash.json
│
└── app-streamlit/                  # Streamlit app source (deployed by bundle)
    ├── app.py
    ├── requirements.txt
    └── assets/  utils/  components/
```

## How it works

**Why SQL notebooks instead of a Python wrapper?** Each `.sql` file is a Databricks SQL notebook — the `-- Databricks notebook source` header + `CREATE WIDGET TEXT catalog/schema` declarations let the notebook run natively on a SQL warehouse with `${catalog}` / `${schema}` substituted from the job's `base_parameters`. No custom statement parser, no Python wrapper.

**Why one orchestrator job?** `setup_all` chains every setup step via `depends_on:`. The customer runs one `databricks bundle run`, the workspace handles ordering, and any failure stops the chain cleanly.

**Why is `load_data.py` a notebook?** It generates ~140k rows of synthetic data on serverless compute and writes via Spark — no local Python, no `databricks fs cp`, no UC Volume upload step.

## Troubleshooting

| Symptom | Cause / Fix |
|---------|-------------|
| App shows "No store assigned" | Step 4 wasn't run — grant the app's service principal access. |
| App's Genie tab shows "Genie Space not configured" | `GENIE_SPACE_ID` in `app-streamlit/app.yaml` is still the placeholder, or the app wasn't re-deployed after editing it. Fix: edit `app.yaml`, then `databricks bundle deploy -t dev` followed by the step-3 `databricks apps deploy` command. |
| `vw_review_sentiment_ai` errors with permission denied | Foundation Model API not enabled on the warehouse — ask a workspace admin. |
| `setup_all` fails on `silver_ddl` with SCHEMA_NOT_FOUND | The catalog doesn't exist yet, or your user lacks `CREATE SCHEMA` on it. Verify the catalog and your privileges. The schema itself is created idempotently by the task. |
| `setup_all` task fails on serverless | Open the job run in the UI to see the failing task. SQL notebook tasks run on the SQL warehouse; `load_data` runs on serverless compute. |

## Teardown

```bash
databricks bundle destroy -t dev
```

Then delete the Genie Space manually in the UI (not yet a bundle resource).

## License

Internal Databricks demo — not for external distribution.
