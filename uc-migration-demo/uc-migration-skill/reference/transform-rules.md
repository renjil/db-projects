# Transform rules - legacy HMS code → UC-compatible

Apply these rewrites. Show the diff; do not change behavior beyond the migration.

## 1. Namespace: 2-level → 3-level
- `USE db;` → `USE CATALOG <catalog>; USE SCHEMA db;`
- `spark.sql("USE db")` → set catalog + schema, or fully-qualify.
- `spark.table("db.tbl")` → `spark.table("<catalog>.db.tbl")`
- `saveAsTable("db.tbl")` → `saveAsTable("<catalog>.db.tbl")`
- SQL `FROM db.tbl` / `CREATE TABLE db.tbl` → `<catalog>.db.tbl`
- Remove reliance on the session default database; fully qualify where practical.

## 2. Storage: mounts → Volumes / External Locations
- File reads/writes on `dbfs:/mnt/<x>/...` → a UC **Volume** path: `/Volumes/<catalog>/<schema>/<volume>/...`
- External-table locations on mounts → an **External Location** (backed by a Storage Credential); reference the `abfss://`/`s3://` URI, not the mount.
- Remove `dbutils.fs.mount(...)` / `dbutils.fs.unmount(...)` calls entirely.
- Remove inline storage keys/SAS in configs - UC uses the Storage Credential.

## 3. Tables
- **External** HMS table (has `LOCATION`) → keep data in place, register via `SYNC TABLE` (see migration-mechanics.md). Re-home the location to an External Location first if it's on a mount.
- **Managed** HMS table (`saveAsTable` with no location, or DB-location managed) → `DEEP CLONE` or CTAS into a UC-managed table. Default format **Delta**.
- `USING PARQUET` → prefer `USING DELTA` for UC-managed (CTAS converts).
- `MSCK REPAIR TABLE` → drop (not needed for Delta/UC-managed).

## 4. Grants
- `GRANT SELECT ON TABLE db.tbl TO \`grp\`` → `GRANT SELECT ON TABLE <catalog>.db.tbl TO \`grp\``
- `GRANT SELECT ON DATABASE db TO \`grp\`` → `GRANT USE SCHEMA ON SCHEMA <catalog>.db TO \`grp\`` (+ table-level SELECT as needed)
- Add the prerequisite `GRANT USE CATALOG ON CATALOG <catalog> TO \`grp\``.
- Map Hive group names to UC account groups per house convention.

## 5. Configs / APIs to remove or replace
- Remove `spark.databricks.hive.metastore.*`, `spark.sql.legacy.createHiveTableByDefault`, glue-catalog flags.
- Replace direct `/dbfs/mnt/...` local-file access with Volume paths.
- Views: recreate with 3-level references; ensure upstream objects are migrated first.

## 6. Deployment
- Package the migrated pipeline as a **DAB** (`databricks-dabs`) with dev/prod targets on serverless.
- Keep the legacy pipeline intact until validation passes.
