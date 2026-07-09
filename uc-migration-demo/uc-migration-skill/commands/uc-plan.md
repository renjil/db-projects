---
description: Produce a UC migration plan for a legacy pipeline (read-only, no changes)
argument-hint: [path to legacy pipeline / notebook / SQL / directory]
---

Use the `uc-migration` skill and the assessment from `/uc-analyse`. This command is **read-only** - produce a plan only, make no changes.

Plan the migration for: **$ARGUMENTS**

Deliver:
1. **Target mapping**: HMS `db.table` → `<catalog>.<schema>.<table>` for every object (use the house convention placeholders; ask if the target catalog is unset).
2. **Per-table method**: `SYNC` (external) vs `DEEP CLONE`/CTAS (managed) vs recreate (view). Justify each.
3. **Storage mapping**: each mount → target **Volume** or **External Location** (+ storage credential note).
4. **Grant translation**: each Hive ACL → UC grant statement(s), including prerequisite `USE CATALOG`/`USE SCHEMA`.
5. **Code changes**: bulleted list of the rewrites required (namespaces, mounts, configs, formats).
6. **Ordered runbook**: the exact sequence (catalog/schema/locations → SYNC/CLONE → grants → deploy DAB → validate → cutover).
7. **Rollback**: how to revert; confirm legacy objects are retained until validation.

Reference `reference/transform-rules.md` and `reference/migration-mechanics.md`. Present the plan for review. End with: "Run `/uc-migrate $ARGUMENTS` to execute (with approval)."
