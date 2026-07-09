-- =====================================================================
-- Pattern A - Table migration HMS -> UC
-- Non-destructive: creates NEW UC objects; legacy hive_metastore.portfolio.* untouched.
-- =====================================================================

-- ---------------------------------------------------------------------
-- transactions_raw  (MANAGED HMS -> UC managed Delta via DEEP CLONE)
-- SYNC does NOT work on managed tables; data is copied into UC storage.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS renjiharold_demo.portfolio.transactions_raw
DEEP CLONE hive_metastore.portfolio.transactions_raw;

-- ---------------------------------------------------------------------
-- transactions_silver  (MANAGED HMS -> UC managed Delta via DEEP CLONE)
-- CLONE gives parallel-run parity; the deployed pipeline also regenerates it.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS renjiharold_demo.portfolio.transactions_silver
DEEP CLONE hive_metastore.portfolio.transactions_silver;

-- ---------------------------------------------------------------------
-- gold_daily  (EXTERNAL PARQUET on mount -> UC managed Delta via CTAS)
-- Converts PARQUET -> DELTA and drops the dbfs:/mnt/curated dependency.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS renjiharold_demo.portfolio.gold_daily
USING DELTA AS
SELECT * FROM hive_metastore.portfolio.gold_daily;

-- ---------------------------------------------------------------------
-- SYNC fallback (only if gold_daily data must stay in place on its current
-- storage instead of CTAS). Requires the location to be an External Location
-- first. Preview with DRY RUN before applying.
-- ---------------------------------------------------------------------
-- SYNC TABLE renjiharold_demo.portfolio.gold_daily
--   FROM hive_metastore.portfolio.gold_daily DRY RUN;
-- SYNC TABLE renjiharold_demo.portfolio.gold_daily
--   FROM hive_metastore.portfolio.gold_daily;
