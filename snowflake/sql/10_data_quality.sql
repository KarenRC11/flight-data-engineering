-- =====================================================
-- PROJECT: Flight Data Engineering
-- FILE: 10_data_quality.sql
-- DESCRIPTION: Data quality monitoring with Data Metric Functions
-- =====================================================
--
-- The Python pipeline validates data before it reaches S3
-- (transform/quality.py and the Gold data contracts). This script
-- adds a second check inside Snowflake, on the tables people query:
-- the warehouse measures its own data and keeps a history of results.
--
-- Covers the README roadmap item:
--   "Incorporar validaciones de calidad en Snowflake".
--
-- REQUIREMENTS
--   * Enterprise Edition or higher.
--   * The role that owns the table needs EXECUTE DATA METRIC FUNCTION
--     ON ACCOUNT. If step 3 fails with a privilege error, run as
--     ACCOUNTADMIN:
--       GRANT EXECUTE DATA METRIC FUNCTION ON ACCOUNT TO ROLE <owner_role>;
--       GRANT DATABASE ROLE SNOWFLAKE.DATA_METRIC_USER TO ROLE <owner_role>;
--   * To read the results view (step 6):
--       GRANT APPLICATION ROLE SNOWFLAKE.DATA_QUALITY_MONITORING_VIEWER
--           TO ROLE <role>;
--   * Run after 08_analytical_marts.sql.
--
-- COST
--   TRIGGER_ON_CHANGES evaluates only when the table changes
--   (a new load). The mart is static between loads, so it consumes
--   nothing while idle; no hourly schedule needed.
-- =====================================================


-- 1. Custom DMF: percentages outside the 0-100 range

CREATE SCHEMA IF NOT EXISTS FLIGHT_DATA_DB.GOVERNANCE;

CREATE DATA METRIC FUNCTION IF NOT EXISTS
    FLIGHT_DATA_DB.GOVERNANCE.PCT_OUT_OF_RANGE(
        ARG_T TABLE(ARG_C FLOAT)
    )
    RETURNS NUMBER
    COMMENT = 'Rows whose percentage is below 0 or above 100.'
AS
$$
    SELECT COUNT_IF(ARG_C < 0 OR ARG_C > 100)
    FROM ARG_T
$$;


-- 2. Custom DMF: negative counts (cancelled or delayed flights)

CREATE DATA METRIC FUNCTION IF NOT EXISTS
    FLIGHT_DATA_DB.GOVERNANCE.NEGATIVE_COUNT(
        ARG_T TABLE(ARG_C NUMBER)
    )
    RETURNS NUMBER
    COMMENT = 'Rows with a negative value in a count column.'
AS
$$
    SELECT COUNT_IF(ARG_C < 0)
    FROM ARG_T
$$;


-- 3. Evaluate whenever the mart changes

ALTER TABLE FLIGHT_DATA_DB.MARTS.AIRLINE_PERFORMANCE_REAL
    SET DATA_METRIC_SCHEDULE = 'TRIGGER_ON_CHANGES';


-- 4. Attach the checks, each with an explicit expectation.
--    An expectation turns a metric into a pass/fail rule.
--    Note: a DMF can be attached to the same column only once, so
--    re-running this step fails. Drop the association first (see
--    MANAGEMENT at the end) if you need to recreate it.

-- The table is not empty
ALTER TABLE FLIGHT_DATA_DB.MARTS.AIRLINE_PERFORMANCE_REAL
    ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.ROW_COUNT ON ()
    EXPECTATION mart_not_empty (VALUE > 0);

-- Every row identifies an airline
ALTER TABLE FLIGHT_DATA_DB.MARTS.AIRLINE_PERFORMANCE_REAL
    ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (AIRLINE)
    EXPECTATION airline_not_null (VALUE = 0);

-- One row per airline (the grain of the mart)
ALTER TABLE FLIGHT_DATA_DB.MARTS.AIRLINE_PERFORMANCE_REAL
    ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.DUPLICATE_COUNT ON (AIRLINE)
    EXPECTATION airline_unique (VALUE = 0);

-- Cancellation rate is a valid percentage
ALTER TABLE FLIGHT_DATA_DB.MARTS.AIRLINE_PERFORMANCE_REAL
    ADD DATA METRIC FUNCTION FLIGHT_DATA_DB.GOVERNANCE.PCT_OUT_OF_RANGE
        ON (CANCELLATION_RATE_PCT)
    EXPECTATION cancellation_pct_in_range (VALUE = 0);

-- Counts cannot be negative
ALTER TABLE FLIGHT_DATA_DB.MARTS.AIRLINE_PERFORMANCE_REAL
    ADD DATA METRIC FUNCTION FLIGHT_DATA_DB.GOVERNANCE.NEGATIVE_COUNT
        ON (CANCELLED_FLIGHTS)
    EXPECTATION cancelled_not_negative (VALUE = 0);

ALTER TABLE FLIGHT_DATA_DB.MARTS.AIRLINE_PERFORMANCE_REAL
    ADD DATA METRIC FUNCTION FLIGHT_DATA_DB.GOVERNANCE.NEGATIVE_COUNT
        ON (DELAYED_FLIGHTS)
    EXPECTATION delayed_not_negative (VALUE = 0);


-- =====================================================
-- VALIDATION
-- =====================================================

-- 5. Evaluate every expectation right now, without waiting for
--    a change on the table. Useful after the first setup.

SELECT *
FROM TABLE(
    SYSTEM$EVALUATE_DATA_QUALITY_EXPECTATIONS(
        REF_ENTITY_NAME => 'FLIGHT_DATA_DB.MARTS.AIRLINE_PERFORMANCE_REAL'
    )
);

-- Run a single metric manually
SELECT FLIGHT_DATA_DB.GOVERNANCE.PCT_OUT_OF_RANGE(
    SELECT CANCELLATION_RATE_PCT
    FROM FLIGHT_DATA_DB.MARTS.AIRLINE_PERFORMANCE_REAL
) AS PCT_OUT_OF_RANGE;


-- 6. Measurement history (filled by scheduled runs).
--    Results can take a few minutes to appear after a change.

SELECT
    MEASUREMENT_TIME,
    TABLE_NAME,
    METRIC_NAME,
    ARGUMENT_NAMES,
    VALUE
FROM SNOWFLAKE.LOCAL.DATA_QUALITY_MONITORING_RESULTS
WHERE TABLE_DATABASE = 'FLIGHT_DATA_DB'
  AND TABLE_NAME = 'AIRLINE_PERFORMANCE_REAL'
ORDER BY MEASUREMENT_TIME DESC;


-- =====================================================
-- MANAGEMENT
-- =====================================================

-- Stop all scheduled checks on the table (saves credits):
-- ALTER TABLE FLIGHT_DATA_DB.MARTS.AIRLINE_PERFORMANCE_REAL
--     SET DATA_METRIC_SCHEDULE = '';

-- Remove one check:
-- ALTER TABLE FLIGHT_DATA_DB.MARTS.AIRLINE_PERFORMANCE_REAL
--     DROP DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (AIRLINE);
