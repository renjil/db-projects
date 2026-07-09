# Acme - UC Migration demo kit

A self-contained kit for demonstrating (and running) **AI-assisted Hive-metastore → Unity Catalog migration** with the Databricks agent skills, plus a purpose-built **`uc-migration` skill**.

## What's here

```
uc-migration-demo/
  legacy-pipelines/               # "before" state - non-UC reference pipelines (2 patterns)
    pattern_a_notebook_mounts/    # PySpark notebooks, DBFS mounts, managed HMS tables, 2-level names
    pattern_b_sql_external/       # SQL DDL, external tables on mounts, Hive-style ACLs
  uc-migration-skill/             # the custom skill + slash commands
    SKILL.md
    reference/                    # transform rules, migration mechanics, validation
    commands/                     # /uc-analyse, /uc-plan, /uc-migrate, /uc-validate
    INSTALL.md
```

## The demo idea (reproducible without a non-UC workspace)

Every UC-enabled workspace still exposes the legacy **`hive_metastore`** catalog. So you can stage the "before" state under `hive_metastore.*` in your UC demo workspace, then let the agent migrate it to a UC catalog - a genuine HMS→UC migration in one workspace. The code-rewrite half needs no runtime at all: feed the legacy source, watch the agent produce the UC-compatible version.

**Workflow the skill drives:** `/uc-analyse` (assess) → `/uc-plan` (plan) → `/uc-migrate` (convert + deploy) → `/uc-validate` (reconcile).

## How to use in the workshop

1. Install the skill (see `uc-migration-skill/INSTALL.md`).
2. Point the agent at a legacy pipeline: `/uc-analyse legacy-pipelines/pattern_a_notebook_mounts`.
3. `/uc-plan` to produce the migration plan.
4. `/uc-migrate` to generate UC-compatible code + SYNC/CLONE SQL + UC grants + a DAB.
5. `/uc-validate` to reconcile the migrated tables against the legacy ones.

> These legacy pipelines are intentionally written with common non-UC patterns. See each pattern's README for the specific incompatibilities the skill is expected to find and fix. Replace them with your own real reference pipelines when you're ready - the skill is designed to encode Acme house patterns.
