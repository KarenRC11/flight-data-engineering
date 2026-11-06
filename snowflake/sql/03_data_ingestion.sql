-- =====================================================
-- PROJECT: Flight Data Engineering
-- PHASE 2: Snowflake Integration
-- FILE: 03_data_ingestion.sql
-- DESCRIPTION: Load airline performance data from S3
-- =====================================================

-- 1. Create destination table

CREATE TABLE IF NOT EXISTS
    FLIGHT_DATA_DB.RAW.AIRLINE_PERFORMANCE (
        AIRLINE VARCHAR(10),
        CANCELLED_FLIGHTS INTEGER,
        DELAYED_FLIGHTS INTEGER,
        CANCELLATION_RATE_PCT FLOAT,
        AVG_ARR_DELAY FLOAT
    );

-- 2. Load Parquet data from AWS S3

COPY INTO FLIGHT_DATA_DB.RAW.AIRLINE_PERFORMANCE
FROM (
    SELECT
        $1:op_unique_carrier::VARCHAR,
        $1:cancelled_flights::INTEGER,
        $1:delayed_flights::INTEGER,
        $1:cancellation_rate::FLOAT * 100,
        $1:avg_arr_delay::FLOAT
    FROM @FLIGHT_DATA_DB.RAW.FLIGHT_GOLD_STAGE/airline_performance/
)
FILE_FORMAT = (
    FORMAT_NAME = 'FLIGHT_DATA_DB.RAW.PARQUET_FORMAT'
)
ON_ERROR = 'ABORT_STATEMENT';

-- 3. Validate loaded data

SELECT
    AIRLINE,
    CANCELLED_FLIGHTS,
    DELAYED_FLIGHTS,
    CANCELLATION_RATE_PCT,
    AVG_ARR_DELAY
FROM FLIGHT_DATA_DB.RAW.AIRLINE_PERFORMANCE
ORDER BY CANCELLED_FLIGHTS DESC;
