-- =====================================================
-- PROJECT: Flight Data Engineering
-- FILE: 08_analytical_marts.sql
-- DESCRIPTION: Analytical tables from real flight data
-- =====================================================

-- Prerequisite:
-- RAW.AIRLINE_PERFORMANCE must already contain
-- the Gold data loaded from AWS S3.

-- Create analytical table using real flight metrics

CREATE TABLE IF NOT EXISTS
    FLIGHT_DATA_DB.MARTS.AIRLINE_PERFORMANCE_REAL AS

SELECT
    AIRLINE,
    CANCELLED_FLIGHTS,
    DELAYED_FLIGHTS,
    CANCELLATION_RATE_PCT,
    AVG_ARR_DELAY

FROM FLIGHT_DATA_DB.RAW.AIRLINE_PERFORMANCE;

-- Validate analytical results

SELECT
    AIRLINE,
    CANCELLED_FLIGHTS,
    DELAYED_FLIGHTS,
    CANCELLATION_RATE_PCT,
    AVG_ARR_DELAY

FROM FLIGHT_DATA_DB.MARTS.AIRLINE_PERFORMANCE_REAL

ORDER BY CANCELLED_FLIGHTS DESC;

-- ============================================================
-- RBAC: Grant read-only access to the analytical mart
-- ============================================================

GRANT SELECT
ON TABLE FLIGHT_DATA_DB.MARTS.AIRLINE_PERFORMANCE_REAL
TO ROLE FLIGHT_ANALYST;
