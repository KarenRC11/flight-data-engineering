-- =====================================================
-- PROJECT: Flight Data Engineering
-- FILE: 09_dynamic_masking.sql
-- DESCRIPTION: Tag-based dynamic data masking for PII
-- =====================================================
--
-- WHY THIS EXTENDS 07_secure_views.sql
--
-- 07 masks the email with a fixed SQL expression inside a Secure View.
-- That protects the view, but:
--   * the raw column is still readable by anyone with SELECT on RAW,
--   * nobody can see the real value, not even an authorized role,
--   * every new view or new PII column needs the masking rewritten.
--
-- Here the protection moves to the column itself:
--   1. A tag classifies the column (PII_TYPE = 'EMAIL' | 'NAME').
--   2. One masking policy is attached to the tag.
--   3. Any column that receives the tag is masked automatically,
--      in every table and view that reads it.
--   4. Masking depends on the role running the query: PII_READER
--      sees real values, everyone else sees masked values.
--
-- REQUIREMENTS
--   * Enterprise Edition or higher (Snowflake trial accounts
--     normally run Enterprise).
--   * Run as a role able to create roles, tags and policies and to
--     apply them (ACCOUNTADMIN for this demo). In production this
--     would be a dedicated governance role with
--     APPLY MASKING POLICY and APPLY TAG ON ACCOUNT.
--   * Run after 07_secure_views.sql and 04_rbac_security.sql.
--
-- All passenger data is fictional.
-- =====================================================


-- 1. Governance schema: tags and policies live apart from the data

CREATE SCHEMA IF NOT EXISTS FLIGHT_DATA_DB.GOVERNANCE;


-- 2. Fictional sample data (07 creates the table but leaves it empty).
--    NOT EXISTS keeps the script safe to re-run.

INSERT INTO FLIGHT_DATA_DB.RAW.PASSENGERS
    (PASSENGER_ID, FULL_NAME, EMAIL, COUNTRY)
SELECT column1, column2, column3, column4
FROM VALUES
    (1, 'Maria Lopez',    'maria.lopez@example.com',  'Mexico'),
    (2, 'John Carter',    'john.carter@example.com',  'United States'),
    (3, 'Ana Fernandez',  'ana.fernandez@example.com', 'Mexico'),
    (4, 'Luis Hernandez', 'luis.h@example.org',        'Guatemala')
WHERE NOT EXISTS (
    SELECT 1 FROM FLIGHT_DATA_DB.RAW.PASSENGERS
);


-- 3. Role that is allowed to see unmasked PII.
--    It inherits FLIGHT_ANALYST, so it can read everything an
--    analyst reads, plus the real PII values.

CREATE ROLE IF NOT EXISTS PII_READER;

GRANT ROLE FLIGHT_ANALYST TO ROLE PII_READER;

-- Deliberately NOT granted to SYSADMIN. Custom roles usually roll up
-- to SYSADMIN, but ACCOUNTADMIN inherits SYSADMIN, so that would give
-- every administrator access to personal data. PII_READER is granted
-- only to the specific users who need it, which keeps that access
-- explicit and auditable (SHOW GRANTS OF ROLE PII_READER).


-- 4. Classification tag

CREATE TAG IF NOT EXISTS FLIGHT_DATA_DB.GOVERNANCE.PII_TYPE
    ALLOWED_VALUES 'EMAIL', 'NAME'
    COMMENT = 'Personal data classification. Columns with this tag are masked.';


-- 5. One masking policy for every string PII column.
--
--    IS_ROLE_IN_SESSION (not CURRENT_ROLE) respects the role hierarchy
--    and secondary roles: a role that inherits PII_READER also sees
--    real values, which is how access is granted in practice.
--
--    SYSTEM$GET_TAG_ON_CURRENT_COLUMN lets the same policy mask each
--    kind of PII differently.

CREATE MASKING POLICY IF NOT EXISTS
    FLIGHT_DATA_DB.GOVERNANCE.MASK_PII_STRING
    AS (VAL STRING) RETURNS STRING ->
    CASE
        WHEN IS_ROLE_IN_SESSION('PII_READER')
            THEN VAL

        -- maria.lopez@example.com -> *****@example.com
        WHEN SYSTEM$GET_TAG_ON_CURRENT_COLUMN('FLIGHT_DATA_DB.GOVERNANCE.PII_TYPE') = 'EMAIL'
            THEN REGEXP_REPLACE(VAL, '^[^@]+', '*****')

        -- Maria Lopez -> M*****
        WHEN SYSTEM$GET_TAG_ON_CURRENT_COLUMN('FLIGHT_DATA_DB.GOVERNANCE.PII_TYPE') = 'NAME'
            THEN LEFT(VAL, 1) || '*****'

        ELSE '*** MASKED ***'
    END
    COMMENT = 'Masks PII by tag value unless the session has PII_READER.';


-- 6. Attach the policy to the tag (tag-based masking)

ALTER TAG FLIGHT_DATA_DB.GOVERNANCE.PII_TYPE
    SET MASKING POLICY FLIGHT_DATA_DB.GOVERNANCE.MASK_PII_STRING;


-- 7. Classify the columns. From here on, masking is automatic.

ALTER TABLE FLIGHT_DATA_DB.RAW.PASSENGERS
    MODIFY COLUMN EMAIL SET TAG FLIGHT_DATA_DB.GOVERNANCE.PII_TYPE = 'EMAIL';

ALTER TABLE FLIGHT_DATA_DB.RAW.PASSENGERS
    MODIFY COLUMN FULL_NAME SET TAG FLIGHT_DATA_DB.GOVERNANCE.PII_TYPE = 'NAME';


-- 8. Governed view: plain SELECT, no masking logic inside.
--    The policy on the base columns does the work.

CREATE OR REPLACE SECURE VIEW
    FLIGHT_DATA_DB.MARTS.V_PASSENGERS_GOVERNED AS

SELECT
    PASSENGER_ID,
    FULL_NAME,
    EMAIL,
    COUNTRY

FROM FLIGHT_DATA_DB.RAW.PASSENGERS;

GRANT SELECT
ON VIEW FLIGHT_DATA_DB.MARTS.V_PASSENGERS_GOVERNED
TO ROLE FLIGHT_ANALYST;


-- =====================================================
-- AUDIT: which columns are classified and protected
-- =====================================================

-- Tags on the table's columns
SELECT
    COLUMN_NAME,
    TAG_NAME,
    TAG_VALUE
FROM TABLE(
    FLIGHT_DATA_DB.INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS(
        'FLIGHT_DATA_DB.RAW.PASSENGERS', 'table'
    )
);

-- Policies in effect on the table (through the tag)
SELECT
    POLICY_NAME,
    POLICY_KIND,
    REF_COLUMN_NAME,
    TAG_NAME,
    POLICY_STATUS
FROM TABLE(
    FLIGHT_DATA_DB.INFORMATION_SCHEMA.POLICY_REFERENCES(
        REF_ENTITY_NAME => 'FLIGHT_DATA_DB.RAW.PASSENGERS',
        REF_ENTITY_DOMAIN => 'table'
    )
);


-- =====================================================
-- SECURITY VALIDATION
-- =====================================================
-- Grant both roles to a test user first, e.g.:
--   GRANT ROLE PII_READER TO USER <your_user>;
-- FLIGHT_ANALYST is inherited through PII_READER.
--
-- Run each block separately.

-- A) Analyst: masked values
-- USE ROLE FLIGHT_ANALYST;
-- USE SECONDARY ROLES NONE;
-- SELECT * FROM FLIGHT_DATA_DB.MARTS.V_PASSENGERS_GOVERNED;
-- Expected: M***** | *****@example.com

-- B) PII reader: real values, same view, same query
-- USE ROLE PII_READER;
-- USE SECONDARY ROLES NONE;
-- SELECT * FROM FLIGHT_DATA_DB.MARTS.V_PASSENGERS_GOVERNED;
-- Expected: Maria Lopez | maria.lopez@example.com

-- C) Administrator without PII_READER: masked as well.
--    Being admin does not grant access to personal data.
-- USE ROLE ACCOUNTADMIN;
-- USE SECONDARY ROLES NONE;
-- SELECT * FROM FLIGHT_DATA_DB.RAW.PASSENGERS;

-- Restore your usual role and secondary roles when finished.
-- USE SECONDARY ROLES ALL;
