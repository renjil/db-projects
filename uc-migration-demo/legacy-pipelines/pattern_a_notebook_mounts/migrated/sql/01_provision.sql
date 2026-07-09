-- =====================================================================
-- Pattern A - UC scaffolding (admin, run once)
-- Catalog: renjiharold_demo  Schema: portfolio
-- =====================================================================

-- Catalog + schema
CREATE CATALOG IF NOT EXISTS renjiharold_demo;
CREATE SCHEMA  IF NOT EXISTS renjiharold_demo.portfolio;

-- ---------------------------------------------------------------------
-- Storage Credential + External Location for the landing container.
-- Replaces the inline fs.azure.account.key secret used by the old mount.
-- Fill in <access-connector-id> (Azure managed identity) per house convention.
-- ---------------------------------------------------------------------
-- CREATE STORAGE CREDENTIAL IF NOT EXISTS ff_landing_cred
--   WITH AZURE_MANAGED_IDENTITY (ACCESS_CONNECTOR_ID = '<access-connector-id>');

-- CREATE EXTERNAL LOCATION IF NOT EXISTS ff_landing_loc
--   URL 'abfss://landing@ffstorage.dfs.core.windows.net/'
--   WITH (STORAGE CREDENTIAL ff_landing_cred);

-- ---------------------------------------------------------------------
-- Landing Volume (replaces dbfs:/mnt/landing for CSV file reads).
-- Option A (recommended for demo): MANAGED volume, stage files into it.
-- Option B: EXTERNAL VOLUME over the abfss path (needs the location above).
-- ---------------------------------------------------------------------
CREATE VOLUME IF NOT EXISTS renjiharold_demo.portfolio.landing;
-- CREATE EXTERNAL VOLUME IF NOT EXISTS renjiharold_demo.portfolio.landing
--   LOCATION 'abfss://landing@ffstorage.dfs.core.windows.net/transactions';
