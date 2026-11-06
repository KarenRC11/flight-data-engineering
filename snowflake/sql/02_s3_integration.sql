-- =====================================================
-- PROJECT: Flight Data Engineering
-- PHASE 2: Snowflake Integration
-- FILE: 02_s3_integration.sql
-- DESCRIPTION: AWS S3 integration and external stage
-- =====================================================

-- 1. Create storage integration
-- Replace the IAM role ARN with your own role.

CREATE STORAGE INTEGRATION IF NOT EXISTS FLIGHT_S3_INT
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = 'S3'
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN = '<YOUR_AWS_IAM_ROLE_ARN>'
    STORAGE_ALLOWED_LOCATIONS = (
        's3://<YOUR_BUCKET>/flight-data-engineering/gold/'
    );

-- 2. Create Parquet file format

CREATE FILE FORMAT IF NOT EXISTS
    FLIGHT_DATA_DB.RAW.PARQUET_FORMAT
    TYPE = PARQUET;

-- 3. Create external stage

CREATE STAGE IF NOT EXISTS
    FLIGHT_DATA_DB.RAW.FLIGHT_GOLD_STAGE
    URL = 's3://<YOUR_BUCKET>/flight-data-engineering/gold/'
    STORAGE_INTEGRATION = FLIGHT_S3_INT
    FILE_FORMAT = FLIGHT_DATA_DB.RAW.PARQUET_FORMAT;

-- 4. Verify files in S3

LIST @FLIGHT_DATA_DB.RAW.FLIGHT_GOLD_STAGE;
