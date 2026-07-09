---
description: Assess a legacy Hive-metastore pipeline for UC migration (read-only)
argument-hint: [path to legacy pipeline / notebook / SQL / directory]
---

Use the `uc-migration` skill. This command is **read-only** - do not change any file, code, or Databricks object.

Analyse the legacy pipeline at: **$ARGUMENTS**

Produce an assessment:
1. **Inventory** every dataset the code reads/writes. For each: name (as written), whether it is a **managed** or **external** HMS table (infer from `LOCATION` / `saveAsTable` / DB location), and format.
2. **Storage**: list all `dbfs:/mnt/...` mounts and `dbutils.fs.mount` calls, and which datasets depend on them.
3. **Namespace**: list all 2-level names and `USE <db>` statements.
4. **Grants**: list every Hive ACL (`GRANT ... ON DATABASE/TABLE/VIEW`).
5. **Incompatible APIs/configs**: `MSCK REPAIR`, legacy Hive Spark configs, direct `/dbfs/mnt` access, `USING PARQUET`, etc.
6. **Complexity/risk rating** (Low/Medium/High) with the top 3 risk factors.

Output as a concise table plus a short summary. End with: "Run `/uc-plan $ARGUMENTS` to produce a migration plan." Do not propose or make changes yet.
