-- =====================================================================
-- Pattern A - Grant translation (Hive ACL -> UC), idempotent
-- Legacy: GRANT SELECT ON TABLE portfolio.transactions_silver TO `portfolio-analysts`
-- Map `portfolio-analysts` to the matching UC account group per house convention.
-- =====================================================================

GRANT USE CATALOG ON CATALOG renjiharold_demo                       TO `portfolio-analysts`;
GRANT USE SCHEMA  ON SCHEMA  renjiharold_demo.portfolio             TO `portfolio-analysts`;
GRANT SELECT      ON TABLE   renjiharold_demo.portfolio.transactions_silver TO `portfolio-analysts`;
