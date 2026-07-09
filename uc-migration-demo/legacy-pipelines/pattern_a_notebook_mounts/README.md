# Pattern A - PySpark notebooks, DBFS mounts, managed HMS tables

A common "notebooks + mounts" medallion pipeline written for the workspace-local Hive metastore.

## Files
- `01_bronze_ingest.py` - mounts storage, ingests CSV, writes a managed HMS table.
- `02_silver_gold.py` - cleanses to silver (managed), aggregates to gold (external parquet on a mount), applies a Hive-style grant.

## Non-UC-compatible patterns present (what the skill should find)
| # | Pattern in code | Why it's not UC-compatible | Target UC approach |
|---|---|---|---|
| A1 | `dbutils.fs.mount(...)` + `dbfs:/mnt/landing` | Mounts aren't governed by UC | External Location + Storage Credential, or a UC **Volume** for file reads |
| A2 | 2-level names `portfolio.transactions_raw`, `USE portfolio` | UC uses a 3-level namespace | `USE CATALOG <catalog>; USE SCHEMA portfolio;` and `catalog.portfolio.transactions_raw` |
| A3 | `saveAsTable("portfolio.transactions_raw")` (managed HMS) | Managed HMS tables can't be `SYNC`ed | `DEEP CLONE` / CTAS into a UC managed table (or UCX managed-table upgrade) |
| A4 | Gold external table on `dbfs:/mnt/curated/...` | External table on a mount path | `SYNC TABLE` after re-homing location to an External Location, or write to a UC managed table |
| A5 | `GRANT SELECT ON TABLE portfolio.transactions_silver TO \`portfolio-analysts\`` | Hive table ACL | UC `GRANT SELECT ON TABLE <catalog>.portfolio.transactions_silver` + `USE CATALOG`/`USE SCHEMA` grants |
| A6 | Secret-key storage config in mount | Not needed under UC | Storage Credential managed by UC |

## Demo staging trick
Stage this under `hive_metastore.portfolio.*` in your UC workspace (create the DB/tables in `hive_metastore`, write files to a Volume you treat as the "mount"), then migrate to a UC catalog. No non-UC workspace required.
