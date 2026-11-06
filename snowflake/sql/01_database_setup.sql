-- =====================================================
-- PROJECT: Flight Data Engineering
-- PHASE 2: Snowflake Integration
-- FILE: 01_database_setup.sql
-- DESCRIPTION: Database and schema initialization
-- =====================================================

-- Create project database
CREATE DATABASE IF NOT EXISTS FLIGHT_DATA_DB;

-- Create data architecture schemas
CREATE SCHEMA IF NOT EXISTS FLIGHT_DATA_DB.RAW;

CREATE SCHEMA IF NOT EXISTS FLIGHT_DATA_DB.STAGING;

CREATE SCHEMA IF NOT EXISTS FLIGHT_DATA_DB.MARTS;

-- Create monitoring and auditing schema
CREATE SCHEMA IF NOT EXISTS FLIGHT_DATA_DB.AUDIT;
