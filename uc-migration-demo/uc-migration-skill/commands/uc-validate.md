---
description: Reconcile migrated UC objects against the legacy HMS objects
argument-hint: [legacy schema, e.g. hive_metastore.portfolio] [uc schema, e.g. dev_catalog.portfolio]
---

Use the `uc-migration` skill and `reference/validation-checklist.md`.

Reconcile: legacy **$1** vs UC **$2** (arguments: `<legacy_schema> <uc_schema>`).

For every migrated object:
1. **Row counts** - compare `COUNT(*)` legacy vs UC.
2. **Aggregate checksums** - compare `SUM`/`MIN`/`MAX` on key numeric columns.
3. **Schema parity** - column names, types, nullability; table type as intended.
4. **Sample diff** - keyed `EXCEPT` both directions on a small sample; report any rows that differ.
5. **Grant parity** - `SHOW GRANTS` on both, reconcile each legacy ACL to a UC grant.
6. **Code hygiene** - grep the migrated code for remaining `hive_metastore`, `dbfs:/mnt`, or legacy configs.

Output a reconciliation table: object | legacy count | UC count | checksum match | schema match | grants match | status. Flag any mismatch as a **blocker** and do not recommend cutover until all pass. Remind that legacy objects should be retained until sign-off.
