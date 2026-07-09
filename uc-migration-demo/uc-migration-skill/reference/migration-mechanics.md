# Migration mechanics - SYNC, CLONE, mounts, grants

The concrete Databricks operations the skill emits. Always `DRY RUN` first where supported.

## SYNC (external tables/views - metadata only, data stays in place)
Use for HMS **external** tables and views. Non-destructive; creates UC objects pointing at the same storage.

```sql
-- Preview at schema level
SYNC SCHEMA <catalog>.<schema> FROM hive_metastore.<schema> DRY RUN;

-- Apply for a whole schema
SYNC SCHEMA <catalog>.<schema> FROM hive_metastore.<schema>;

-- Or a single table
SYNC TABLE <catalog>.<schema>.<table> FROM hive_metastore.<schema>.<table>;
```
Prerequisite: the underlying location must be governed by an **External Location** (re-home mount paths to `abfss://`/`s3://` first). SYNC does **not** work for managed tables.

## DEEP CLONE / CTAS (managed tables)
Use for HMS **managed** tables (or to land as UC-managed Delta).

```sql
-- Managed Delta copy (data copied into UC managed storage)
CREATE TABLE <catalog>.<schema>.<table>
DEEP CLONE hive_metastore.<schema>.<table>;

-- Or CTAS when converting format / reshaping
CREATE TABLE <catalog>.<schema>.<table> USING DELTA AS
SELECT * FROM hive_metastore.<schema>.<table>;
```
For large estates, prefer the **UCX** managed-table upgrade workflow.

## Mounts → Volumes / External Locations
```sql
-- Storage credential + external location (admin, once)
CREATE STORAGE CREDENTIAL <cred> ... ;
CREATE EXTERNAL LOCATION <loc> URL 'abfss://<container>@<acct>.dfs.core.windows.net/<path>'
  WITH (STORAGE CREDENTIAL <cred>);

-- Volume for file reads/writes previously done on a mount
CREATE VOLUME <catalog>.<schema>.<volume>;   -- managed
-- or EXTERNAL VOLUME ... LOCATION '<abfss uri>'
```
Then rewrite code from `dbfs:/mnt/...` to `/Volumes/<catalog>/<schema>/<volume>/...` (or the external URI for external tables).

## Grants (Hive ACL → UC)
```sql
GRANT USE CATALOG ON CATALOG <catalog> TO `<group>`;
GRANT USE SCHEMA  ON SCHEMA  <catalog>.<schema> TO `<group>`;
GRANT SELECT      ON TABLE   <catalog>.<schema>.<table> TO `<group>`;
```
Enumerate legacy grants (`SHOW GRANTS ON ...` in hive_metastore) and translate each. Map Hive group names to UC account groups per house convention.

## Order of operations
1. Create/confirm catalog, schemas, external locations, volumes.
2. `SYNC` external tables/views; `CLONE`/CTAS managed tables.
3. Apply UC grants.
4. Rewrite + deploy the pipeline (DAB) writing to UC.
5. Parallel-run, then `/uc-validate`.
6. Cut over; retire legacy only after validation passes.
