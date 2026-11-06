# ❄️ Snowflake Integration | Flight Data Engineering

## Overview

This project extends an existing Python-based Data Engineering pipeline by integrating Snowflake with AWS S3.

The original pipeline processes over **7 million flight records from 2024** using a Medallion Architecture (Bronze, Silver, Gold).

This second phase focuses on cloud data integration, SQL, access control, auditing, automation, and interactive monitoring.

## Architecture

**Phase 1 — Python & AWS**

Flight Dataset → Python ETL → Bronze → Silver → Gold → AWS S3

**Phase 2 — Snowflake**

AWS S3 (Gold) → Storage Integration → External Stage → Snowflake RAW

**Governance & Monitoring**

Snowflake Query History → Audit Table → Monitoring View → Streamlit Dashboard

The flight analytics pipeline and the audit monitoring dashboard are separate components within the same project.

## Technologies

- Python
- SQL
- AWS S3
- AWS IAM
- Snowflake
- Snowpark
- Pandas
- Streamlit
- Git & GitHub

## Snowflake Components

### 1. Database Architecture

The project uses four schemas:

- `RAW`: Ingested data from AWS S3.
- `STAGING`: Data preparation and transformation.
- `MARTS`: Analytical tables and views.
- `AUDIT`: Query error monitoring.

### 2. AWS S3 Integration

Implemented a Snowflake Storage Integration using an AWS IAM role.

Configured an external stage and Parquet file format to access flight performance data stored in S3.

### 3. Data Ingestion

Used `COPY INTO` to load airline performance metrics from Parquet files into Snowflake.

### 4. Role-Based Access Control

Implemented a custom `FLIGHT_ANALYST` role with restricted access to analytical objects.

Tested access restrictions by disabling secondary roles.

### 5. Data Protection

Created a Secure View to expose masked passenger email addresses.

The masking is implemented through SQL expressions rather than Snowflake Dynamic Data Masking policies.

### 6. Query Auditing

Developed an auditing process using:

- Snowflake Query History
- SQL `MERGE`
- Error classification with `CASE WHEN`
- Audit tables and monitoring views

### 7. Task Automation

Created a Snowflake Task configured for hourly execution.

The task was tested successfully through manual execution and remains suspended to control trial credit consumption.

### 8. Streamlit Dashboard

Developed an interactive monitoring application featuring:

- Total error KPI
- Possible permission error KPI
- SQL syntax error KPI
- Error distribution charts
- Daily error visualization
- Filters by category, role, and date
- Query error details

The dashboard reads stored audit data and does not independently schedule audit collection.

## Project Structure

```text
snowflake/
├── sql/
│   ├── 01_database_setup.sql
│   ├── 02_s3_integration.sql
│   ├── 03_data_ingestion.sql
│   ├── 04_rbac_security.sql
│   ├── 05_audit_monitoring.sql
│   └── 06_tasks.sql
├── streamlit/
│   └── streamlit_app.py
└── README.md
```

## Current Status

**Implemented:**
- AWS S3 integration
- Parquet ingestion
- SQL transformations
- RBAC
- Secure Views
- Query auditing
- Snowflake Tasks
- Streamlit monitoring dashboard

**Planned improvements:**
- dbt transformations and tests
- Incremental ingestion with Streams
- Snowpipe exploration
- Query performance optimization
- Cost monitoring
- Dedicated least-privilege application role

## Notes

This is a personal learning and portfolio project.

The repository contains implementation scripts but does not include credentials, private audit records, or production data.

## SQL Execution Order

Run the SQL scripts in the following order:

1. `01_database_setup.sql`
2. `02_s3_integration.sql`
3. `03_data_ingestion.sql`
4. `08_analytical_marts.sql`
5. `07_secure_views.sql`
6. `04_rbac_security.sql`
7. `05_audit_monitoring.sql`
8. `06_tasks.sql`

### Prerequisites

- An active Snowflake account.
- An AWS S3 bucket containing the Gold Parquet files.
- An AWS IAM role configured for Snowflake access.
- A Snowflake warehouse.
- Appropriate privileges to create integrations, roles, and database objects.

### Important Notes

- Replace all infrastructure placeholders before execution.
- Configure the AWS IAM trust relationship before accessing S3.
- The RBAC script depends on the analytical table and secure view.
- The sample passenger table is intended for demonstration only.
- Existing MARTS tables are not replaced automatically.
- The Snowflake Task remains suspended until explicitly activated.
- Review warehouse costs before enabling scheduled execution.
