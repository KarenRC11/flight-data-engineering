-- =====================================================
-- PROJECT: Flight Data Engineering
-- PHASE 2: Snowflake Integration
-- FILE: 06_tasks.sql
-- DESCRIPTION: Automated query error auditing
-- =====================================================

-- PREREQUISITE:
-- Execute 05_audit_monitoring.sql first.
--
-- This task uses an existing warehouse.
-- It remains SUSPENDED until explicitly activated.

-- 1. Create scheduled task

CREATE TASK IF NOT EXISTS
    FLIGHT_DATA_DB.AUDIT.TASK_QUERY_ERRORS

    WAREHOUSE = COMPUTE_WH
    SCHEDULE = '60 MINUTES'

AS

MERGE INTO FLIGHT_DATA_DB.AUDIT.QUERY_ERRORS AS TARGET

USING (
    SELECT
        QUERY_ID,
        USER_NAME,
        ROLE_NAME,
        START_TIME,
        QUERY_TYPE,
        ERROR_CODE,
        ERROR_MESSAGE,
        QUERY_TEXT

    FROM TABLE(
        FLIGHT_DATA_DB.INFORMATION_SCHEMA.QUERY_HISTORY(
            DATEADD('hour', -2, CURRENT_TIMESTAMP()),
            CURRENT_TIMESTAMP(),
            10000
        )
    )

    WHERE EXECUTION_STATUS = 'FAILED_WITH_ERROR'

) AS SOURCE

ON TARGET.QUERY_ID = SOURCE.QUERY_ID

WHEN NOT MATCHED THEN INSERT (
    QUERY_ID,
    USER_NAME,
    ROLE_NAME,
    START_TIME,
    QUERY_TYPE,
    ERROR_CODE,
    ERROR_MESSAGE,
    QUERY_TEXT
)
VALUES (
    SOURCE.QUERY_ID,
    SOURCE.USER_NAME,
    SOURCE.ROLE_NAME,
    SOURCE.START_TIME,
    SOURCE.QUERY_TYPE,
    SOURCE.ERROR_CODE,
    SOURCE.ERROR_MESSAGE,
    SOURCE.QUERY_TEXT
);

-- =====================================================
-- TASK VALIDATION
-- =====================================================

-- 2. Check task configuration

SHOW TASKS LIKE 'TASK_QUERY_ERRORS'
IN SCHEMA FLIGHT_DATA_DB.AUDIT;

-- 3. Execute task manually (optional)
-- EXECUTE TASK FLIGHT_DATA_DB.AUDIT.TASK_QUERY_ERRORS;

-- 4. Review execution history

SELECT
    NAME,
    STATE,
    SCHEDULED_TIME,
    COMPLETED_TIME,
    ERROR_MESSAGE

FROM TABLE(
    FLIGHT_DATA_DB.INFORMATION_SCHEMA.TASK_HISTORY(
        TASK_NAME => 'TASK_QUERY_ERRORS',
        RESULT_LIMIT => 10
    )
)

ORDER BY SCHEDULED_TIME DESC;

-- =====================================================
-- SCHEDULING CONTROL
-- =====================================================

-- Activate automatic execution only when needed:
-- ALTER TASK FLIGHT_DATA_DB.AUDIT.TASK_QUERY_ERRORS RESUME;

-- Suspend automatic execution:
-- ALTER TASK FLIGHT_DATA_DB.AUDIT.TASK_QUERY_ERRORS SUSPEND;
