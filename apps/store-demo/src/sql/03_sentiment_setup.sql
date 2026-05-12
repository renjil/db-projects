-- ============================================================================
-- 7-Eleven Store Intelligence Demo - Sentiment Analysis Setup
-- Catalog/Schema: passed in as ${catalog}.${schema}
-- ============================================================================
-- This file creates the customer reviews table, AI sentiment view, and
-- aggregated sentiment table for the Store Intelligence Platform.
--
-- Prerequisites:
--   - Run 01_silver_ddl.sql first to create the schema
--   - Foundation Model API enabled (for vw_review_sentiment_ai)
-- ============================================================================

-- ============================================================================
-- SILVER LAYER: Customer Reviews (Source Data)
-- ============================================================================

CREATE TABLE IF NOT EXISTS ${catalog}.${schema}.silver_customer_reviews (
    review_id INT GENERATED ALWAYS AS IDENTITY,
    store_id INT NOT NULL,
    store_code STRING NOT NULL,
    review_date DATE NOT NULL,
    review_source STRING NOT NULL,  -- 'Google', 'Yelp', 'Survey', etc.
    rating INT,                      -- 1-5 stars
    review_text STRING NOT NULL,
    customer_name STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
USING delta
COMMENT 'Customer reviews from various sources (Google, Yelp, surveys) for sentiment analysis';

-- ============================================================================
-- AI VIEW: Real-time Sentiment Analysis using Foundation Model API
-- ============================================================================
-- This view uses ai_query() to analyze review sentiment in real-time.
-- Note: Queries against this view will incur Foundation Model API costs.

CREATE OR REPLACE VIEW ${catalog}.${schema}.vw_review_sentiment_ai AS
SELECT
    review_id,
    store_id,
    store_code,
    review_date,
    review_source,
    rating,
    review_text,
    customer_name,
    ai_query(
        'databricks-meta-llama-3-3-70b-instruct',
        CONCAT(
            'Analyze this customer review and respond with ONLY a JSON object in this exact format: ',
            '{"sentiment": "positive/neutral/negative", "themes": ["theme1", "theme2"]}. ',
            'Review: ', review_text
        )
    ) AS ai_analysis
FROM ${catalog}.${schema}.silver_customer_reviews;

-- ============================================================================
-- GOLD LAYER: Aggregated Store Sentiment Summary
-- ============================================================================
-- Pre-computed sentiment metrics per store for dashboard display.
-- This table should be refreshed periodically (e.g., daily) by processing
-- the AI sentiment analysis results.

CREATE TABLE IF NOT EXISTS ${catalog}.${schema}.gold_store_sentiment (
    store_id INT NOT NULL,
    store_code STRING NOT NULL,
    store_name STRING,
    overall_rating DECIMAL(2,1),     -- Average star rating (1.0-5.0)
    sentiment_score INT,              -- Aggregated sentiment (0-100)
    review_count INT,                 -- Total reviews analyzed
    positive_pct DECIMAL(4,1),        -- % positive reviews
    neutral_pct DECIMAL(4,1),         -- % neutral reviews
    negative_pct DECIMAL(4,1),        -- % negative reviews
    top_positive_themes STRING,       -- JSON array of common positive themes
    top_negative_themes STRING,       -- JSON array of common negative themes
    trend_direction STRING,           -- 'improving', 'stable', 'declining'
    nps_score INT,                    -- Net Promoter Score (-100 to 100)
    last_updated DATE
)
USING delta
COMMENT 'Aggregated customer sentiment metrics per store for dashboard display';

-- ============================================================================
-- HELPER PROCEDURE: Refresh Gold Sentiment Table
-- ============================================================================
-- Call this procedure to refresh the gold_store_sentiment table from the
-- AI-analyzed reviews. This processes the vw_review_sentiment_ai view and
-- aggregates results per store.

-- Note: Uncomment and customize this procedure based on your requirements.
-- The procedure below is a template that parses the AI JSON response and
-- aggregates sentiment by store.

/*
CREATE OR REPLACE PROCEDURE ${catalog}.${schema}.refresh_store_sentiment()
BEGIN
    MERGE INTO ${catalog}.${schema}.gold_store_sentiment AS target
    USING (
        WITH parsed_sentiment AS (
            SELECT
                store_id,
                store_code,
                rating,
                review_text,
                TRY_CAST(GET_JSON_OBJECT(ai_analysis, '$.sentiment') AS STRING) AS sentiment,
                GET_JSON_OBJECT(ai_analysis, '$.themes') AS themes
            FROM ${catalog}.${schema}.vw_review_sentiment_ai
        ),
        store_agg AS (
            SELECT
                ps.store_id,
                ps.store_code,
                s.store_name,
                ROUND(AVG(ps.rating), 1) AS overall_rating,
                COUNT(*) AS review_count,
                ROUND(100.0 * SUM(CASE WHEN ps.sentiment = 'positive' THEN 1 ELSE 0 END) / COUNT(*), 1) AS positive_pct,
                ROUND(100.0 * SUM(CASE WHEN ps.sentiment = 'neutral' THEN 1 ELSE 0 END) / COUNT(*), 1) AS neutral_pct,
                ROUND(100.0 * SUM(CASE WHEN ps.sentiment = 'negative' THEN 1 ELSE 0 END) / COUNT(*), 1) AS negative_pct
            FROM parsed_sentiment ps
            LEFT JOIN ${catalog}.${schema}.silver_stores s ON ps.store_id = s.store_id
            GROUP BY ps.store_id, ps.store_code, s.store_name
        )
        SELECT
            *,
            CAST(positive_pct - negative_pct AS INT) AS sentiment_score,
            CAST((positive_pct - negative_pct) AS INT) AS nps_score,
            'stable' AS trend_direction,  -- TODO: Calculate from historical data
            NULL AS top_positive_themes,   -- TODO: Aggregate themes
            NULL AS top_negative_themes,
            CURRENT_DATE() AS last_updated
        FROM store_agg
    ) AS source
    ON target.store_id = source.store_id
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *;
END;
*/

-- ============================================================================
-- SAMPLE DATA INSERT (for testing)
-- ============================================================================
-- See 03_generate_synthetic_data.py for programmatic data generation
-- or use the INSERT statements below for quick testing.

-- Sample insert (uncomment to use):
/*
INSERT INTO ${catalog}.${schema}.silver_customer_reviews
(store_id, store_code, review_date, review_source, rating, review_text, customer_name) VALUES
(1, 'SEV-TX-001', '2024-01-15', 'Google', 5, 'Great store! Staff was very friendly.', 'John M.'),
(1, 'SEV-TX-001', '2024-01-18', 'Yelp', 4, 'Love this location. Fresh coffee!', 'Sarah K.');
*/

-- ============================================================================
-- GRANTS (adjust based on your security requirements)
-- ============================================================================
-- GRANT SELECT ON TABLE ${catalog}.${schema}.silver_customer_reviews TO `data_analysts`;
-- GRANT SELECT ON VIEW ${catalog}.${schema}.vw_review_sentiment_ai TO `data_analysts`;
-- GRANT SELECT ON TABLE ${catalog}.${schema}.gold_store_sentiment TO `app_service_principal`;
