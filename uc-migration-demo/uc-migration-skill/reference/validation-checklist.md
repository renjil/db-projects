# Validation & reconciliation checklist

Run after migration, before cutover. `/uc-validate` automates most of this.

## Data parity
- [ ] **Row counts** match per table: `SELECT COUNT(*)` on `hive_metastore.<s>.<t>` vs `<catalog>.<s>.<t>`.
- [ ] **Aggregate checksums** on key numeric columns match (e.g. `SUM(amount)`, `SUM(exposure_amt)`).
- [ ] **Sample diff**: order-independent compare of a keyed sample (e.g. `EXCEPT` both directions on a subset).
- [ ] Partition/date-range coverage matches.

## Schema parity
- [ ] Column names, types, nullability match (allow intentional type tightening if planned).
- [ ] Table type as intended (managed Delta vs external).
- [ ] Views resolve and return the same shape.

## Access parity
- [ ] Every legacy grant has a UC equivalent (`SHOW GRANTS` on both, reconciled).
- [ ] Prerequisite `USE CATALOG`/`USE SCHEMA` grants present.
- [ ] No unintended broadening of access.

## Operational
- [ ] Migrated pipeline runs green on serverless via the DAB.
- [ ] Lineage shows in UC (system tables / catalog explorer).
- [ ] No remaining `hive_metastore`, `dbfs:/mnt`, or legacy-config references in code (grep).
- [ ] Rollback path documented (legacy objects retained until sign-off).

## Report
Emit a short table: object | legacy count | UC count | match? | notes. Flag any mismatch as a blocker.
