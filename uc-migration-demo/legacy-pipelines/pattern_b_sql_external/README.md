# Pattern B - SQL-first, external tables on mounts, Hive ACLs

A SQL/DDL-driven pipeline (run via a Jobs task) using the Hive metastore, external tables on DBFS mount locations, and Hive-style GRANTs.

## Files
- `pipeline.sql` - DDL + transforms + Hive ACLs.
- `run_job.py` - legacy driver that executes the SQL and sets Hive-oriented configs.

## Non-UC-compatible patterns present (what the skill should find)
| # | Pattern in code | Why it's not UC-compatible | Target UC approach |
|---|---|---|---|
| B1 | `CREATE DATABASE ... LOCATION 'dbfs:/mnt/risk/warehouse'` | DB-level mount location | UC schema in a catalog with a governed managed location (or External Location) |
| B2 | `CREATE TABLE ... USING PARQUET LOCATION 'dbfs:/mnt/...'` (external) | External table on a mount | Register under UC via `SYNC TABLE` once location is an External Location, or CLONE into managed |
| B3 | `MSCK REPAIR TABLE` | Legacy partition discovery | Not needed with UC managed tables / Delta; drop or replace |
| B4 | 2-level names `risk_db.exposures_clean`, `USE risk_db` | 3-level namespace in UC | `USE CATALOG <catalog>; USE SCHEMA risk_db;` |
| B5 | `GRANT ... ON DATABASE/TABLE/VIEW ... TO \`group\`` | Hive ACLs | UC grants on `<catalog>.risk_db.*` + `USE CATALOG`/`USE SCHEMA` |
| B6 | `spark.conf.set("spark.databricks.hive.metastore...")`, `spark.sql.legacy.createHiveTableByDefault` | Legacy Hive configs | Remove; default to Delta + UC |
| B7 | `USING PARQUET` format | Non-Delta | Convert to Delta (`USING DELTA` / CTAS) for UC-managed best practice |

## Demo staging trick
Create `hive_metastore.risk_db` with these objects (point "mounts" at a Volume path you control), then migrate to a UC catalog. Views migrate by re-pointing to 3-level names.
