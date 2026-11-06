-- =====================================================
-- PROJECT: Flight Data Engineering
-- PHASE 2: Snowflake Integration
-- FILE: 04_rbac_security.sql
-- DESCRIPTION: Role-Based Access Control (RBAC)
-- =====================================================

-- 1. Create analyst role

CREATE ROLE IF NOT EXISTS FLIGHT_ANALYST;

-- 2. Grant warehouse access

GRANT USAGE
ON WAREHOUSE COMPUTE_WH
TO ROLE FLIGHT_ANALYST;

-- 3. Grant database access

GRANT USAGE
ON DATABASE FLIGHT_DATA_DB
TO ROLE FLIGHT_ANALYST;

-- 4. Grant access to MARTS schema

GRANT USAGE
ON SCHEMA FLIGHT_DATA_DB.MARTS
TO ROLE FLIGHT_ANALYST;

-- 5. Grant SELECT on analytical table

GRANT SELECT
ON TABLE FLIGHT_DATA_DB.MARTS.AIRLINE_PERFORMANCE
TO ROLE FLIGHT_ANALYST;

-- 6. Grant access to secure view

GRANT SELECT
ON VIEW FLIGHT_DATA_DB.MARTS.V_PASSENGERS_SECURE
TO ROLE FLIGHT_ANALYST;

-- =====================================================
-- SECURITY VALIDATION
-- =====================================================

-- Execute these commands separately in Snowflake
-- after assigning FLIGHT_ANALYST to a test user.

-- USE ROLE FLIGHT_ANALYST;
-- USE SECONDARY ROLES NONE;

-- Expected: Access allowed
-- SELECT *
-- FROM FLIGHT_DATA_DB.MARTS.AIRLINE_PERFORMANCE;

-- Expected: Access denied
-- SELECT *
-- FROM FLIGHT_DATA_DB.RAW.PASSENGERS;

-- Restore your administrative role when finished.
