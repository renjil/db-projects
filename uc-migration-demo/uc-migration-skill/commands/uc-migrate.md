---
description: Convert a legacy pipeline to UC-compatible code + SQL + DAB (deploy is approval-gated)
argument-hint: [path to legacy pipeline / notebook / SQL / directory]
---

Use the `uc-migration` skill and the plan from `/uc-plan`. Follow the skill guardrails strictly.

Execute the migration for: **$ARGUMENTS**

Do the following, then STOP for review before any deploy/run:
1. **Rewrite the code** to UC-compatible per `reference/transform-rules.md`: 3-level names, Volumes/External Locations instead of mounts, remove legacy configs/`MSCK`, Delta by default. Write the migrated files to a new `migrated/` folder alongside the source - **never overwrite the legacy files**.
2. **Generate the SQL**: `SYNC`/`DEEP CLONE`/CTAS statements (with `DRY RUN` variants where supported) per `reference/migration-mechanics.md`.
3. **Generate UC grants** translating every legacy ACL.
4. **Package a DAB** (use `databricks-dabs`) with dev/prod targets on serverless, writing to the target UC catalog.
5. **Show the diff** (legacy → migrated) and the exact SQL/DAB you propose to run.

Then present a clear summary and **ask for explicit approval** before running anything. Only after approval:
- run the `DRY RUN` SQL, report results, then the real `SYNC`/`CLONE` + grants,
- `databricks bundle validate` → `deploy -t dev` → `run`.

Never `DROP`/overwrite legacy objects. After deploy, tell the user to run `/uc-validate` for reconciliation.
