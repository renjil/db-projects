-- =====================================================================
-- Pattern B - Legacy SQL pipeline on hive_metastore
-- External tables on DBFS mounts + Hive-style ACLs
-- Target: non-UC workspace / hive_metastore
-- =====================================================================

-- Database created at a mount location (external managed location)
CREATE DATABASE IF NOT EXISTS risk_db
LOCATION 'dbfs:/mnt/risk/warehouse';

USE risk_db;

-- External table over files landed on a mount
CREATE TABLE IF NOT EXISTS risk_db.exposures_raw
USING PARQUET
LOCATION 'dbfs:/mnt/risk/landing/exposures';

-- Legacy metastore partition discovery
MSCK REPAIR TABLE risk_db.exposures_raw;

-- Derived table (managed by the database's mount location)
CREATE TABLE IF NOT EXISTS risk_db.exposures_clean AS
SELECT
    counterparty_id,
    asset_class,
    CAST(exposure_amt AS DOUBLE) AS exposure_amt,
    CAST(as_of_date  AS DATE)    AS as_of_date
FROM risk_db.exposures_raw
WHERE exposure_amt IS NOT NULL;

-- Gold view
CREATE OR REPLACE VIEW risk_db.exposures_by_class AS
SELECT asset_class, as_of_date, SUM(exposure_amt) AS total_exposure
FROM risk_db.exposures_clean
GROUP BY asset_class, as_of_date;

-- Legacy Hive-style ACLs
GRANT SELECT ON DATABASE risk_db TO `data-stewards`;
GRANT SELECT ON TABLE  risk_db.exposures_clean   TO `risk-analysts`;
GRANT SELECT ON VIEW   risk_db.exposures_by_class TO `risk-analysts`;
