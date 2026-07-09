---
name: uc-migration
description: >-
  Migrate legacy Hive metastore pipelines and datasets to Unity Catalog using your organizations
  house patterns. Use when converting non-UC pipelines/notebooks/SQL to UC-compatible code,
  assessing or planning a Hive-metastore-to-Unity-Catalog migration, mapping DBFS mounts to
  Volumes or External Locations, translating Hive ACLs to UC grants, or running SYNC/DEEP CLONE.
  Triggers on "migrate to UC", "UC compatible", "hive metastore to unity catalog",
  "make this pipeline UC ready", "upgrade to unity catalog".
---

# Unity Catalog Agentic Migration

Convert legacy Hive-metastore (HMS) pipelines and datasets to Unity Catalog, following proven reference patterns. This skill encodes the house approach so every engineer's migration is consistent, reviewable, and reconciled.

## When to use
- A pipeline/notebook/SQL uses `hive_metastore`, 2-level names, DBFS mounts, or Hive ACLs and needs to become UC-compatible.
- You want an assessment or a migration plan before touching code.
- You need the mechanical conversion (code rewrite + `SYNC`/`DEEP CLONE` + UC grants + a DAB).

## The 4-phase workflow (slash commands)
1. **`/uc-analyse <path>`** - read-only assessment of a legacy pipeline: inventory tables (managed vs external), mounts, `hive_metastore` refs, 2-level names, Hive grants, incompatible APIs/configs; output a complexity/risk rating.
2. **`/uc-plan <path>`** - produce a migration plan: catalog/schema target mapping, per-table `SYNC` vs `DEEP CLONE` vs CTAS decision, mount → Volume/External Location mapping, grant translation, ordered steps, and rollback.
3. **`/uc-migrate <path>`** - execute the conversion: rewrite code to UC-compatible, generate `SYNC`/`CLONE` SQL and UC grants, package as a DAB. Deployment/run is gated on explicit human approval.
4. **`/uc-validate <legacy> <uc>`** - reconcile: row counts, schema parity, sample checks, and grant parity between legacy and UC.

Use them in order; each is safe to run repeatedly. `/uc-analyse` and `/uc-plan` never change anything.

## House conventions (fill these in for your organization)
Set these once so the agent applies them consistently. Replace the placeholders:
- Target catalogs: `<dev_catalog>`, `<prod_catalog>` (e.g. per-domain catalogs).
- Schema mapping: HMS `db` → UC `catalog.db` (keep schema names unless there's a house rule).
- Managed storage / External Locations: `<external_location_name>` mapping for re-homed mount paths.
- Group naming: how Hive groups map to UC principals/account groups.
- Table format: default to **Delta** for UC-managed tables.
- Tagging/ownership standards to apply on migrated objects.

## Core rules (details in reference/)
- Names: 2-level → 3-level. `USE CATALOG <catalog>; USE SCHEMA <schema>;` then fully-qualify `catalog.schema.table`.
- Mounts: `dbfs:/mnt/...` → **Volume** (for file reads/writes) or **External Location** (for external tables). Never carry mounts into UC.
- Tables: **external** HMS tables → `SYNC TABLE`/`SYNC SCHEMA` (metadata-only, keeps data in place). **Managed** HMS tables cannot be `SYNC`ed → `DEEP CLONE`/CTAS into UC-managed (or use UCX managed-table upgrade).
- Grants: Hive table/db ACLs → UC `GRANT ... ON <catalog>.<schema>.<obj>` plus `USE CATALOG`/`USE SCHEMA`.
- Configs: remove legacy Hive configs (`spark.databricks.hive.metastore.*`, `spark.sql.legacy.createHiveTableByDefault`, glue catalog flags).
- See `reference/transform-rules.md`, `reference/migration-mechanics.md`, `reference/validation-checklist.md`.

## Complement, don't reinvent
- For **assessment at scale**, drive or consume **UCX** (`databrickslabs/ucx`) rather than re-deriving the inventory by hand. This skill can read UCX assessment output and turn it into the plan.
- Deploy migrated assets with the standard `databricks-dabs` / `databricks-pipelines` / `databricks-jobs` skills.

## Guardrails (must follow)
- `/uc-analyse` and `/uc-plan` are **read-only**. Never mutate anything in these phases.
- `/uc-migrate` must present the code diff and the SQL it will run, and **wait for explicit approval before deploying or running**. Never `DROP` or overwrite legacy tables.
- Always keep the legacy objects until `/uc-validate` passes (parallel-run, then cut over).
- Prefer `SYNC` (non-destructive, data stays put) over copying data unless a managed table requires a clone.
- Reconcile row counts and schema before declaring success.
