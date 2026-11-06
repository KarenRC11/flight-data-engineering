-- =====================================================
-- PROJECT: Flight Data Engineering
-- FILE: 07_secure_views.sql
-- DESCRIPTION: Secure views and data protection
-- =====================================================

-- DEMO DATA ONLY
-- The passenger records below are fictional.

-- 1. Create sample passenger table

CREATE TABLE IF NOT EXISTS
    FLIGHT_DATA_DB.RAW.PASSENGERS (
        PASSENGER_ID INTEGER,
        FULL_NAME VARCHAR(100),
        EMAIL VARCHAR(200),
        COUNTRY VARCHAR(50)
    );

-- 2. Create secure view with masked emails

CREATE OR REPLACE SECURE VIEW
    FLIGHT_DATA_DB.MARTS.V_PASSENGERS_SECURE AS

SELECT
    PASSENGER_ID,
    FULL_NAME,
    CONCAT(
        '*****@',
        SPLIT_PART(EMAIL, '@', 2)
    ) AS MASKED_EMAIL,
    COUNTRY

FROM FLIGHT_DATA_DB.RAW.PASSENGERS;

-- 3. Validate secure view

SELECT *
FROM FLIGHT_DATA_DB.MARTS.V_PASSENGERS_SECURE;
