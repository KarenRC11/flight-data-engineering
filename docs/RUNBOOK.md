# RUNBOOK — Flight Data Engineering 2024

## 1. Overview

This runbook describes the operational procedures required to execute, validate, troubleshoot, and re-run the Flight Data Engineering 2024 pipeline.

The pipeline processes flight data through the following layers:

Source
  |
  v
Extract
  |
  v
Bronze (Raw)
  |
  v
Silver (Curated)
  |
  v
Gold (Serving)
  |
  v
Amazon S3

The project uses Python and Amazon S3 as the primary cloud storage layer.

---

## 2. Prerequisites

Before running the pipeline, verify that the following requirements are available:

- Python 3.10+
- Git
- AWS CLI
- AWS credentials configured
- Access to the project repository
- Access to the configured S3 bucket
- Python virtual environment

Verify Python:

python --version

Verify AWS CLI:

aws --version

Verify AWS credentials:

aws sts get-caller-identity

---

## 3. Environment Setup

Clone the repository:

git clone https://github.com/KarenRC11/flight-data-engineering.git

cd flight-data-engineering-2024

Create the virtual environment:

make venv

Activate it:

source .venv/bin/activate

Install dependencies:

make install

---

## 4. Project Structure

The main project directories are:

flight-data-engineering-2024/
|
├── architecture/
│   └── architecture.md
|
├── data_contract/
│   └── schema/
│       ├── bronze.json
│       ├── silver.json
│       ├── gold_airline_performance.json
│       ├── gold_airport_performance.json
│       └── gold_route_performance.json
|
├── docs/
│   └── RUNBOOK.md
|
├── src/
│   └── pipeline/
│       ├── extract/
│       ├── transform/
│       ├── load/
│       ├── main.py
│       ├── silver.py
│       ├── gold.py
│       ├── airport_performance.py
│       └── route_performance.py
|
├── tests/
├── data/
├── Makefile
├── README.md
└── requirements.txt

---

## 5. Standard Pipeline Execution

The official local entry point is:

make run

Equivalent command:

python -m pipeline.main

The logical pipeline flow is:

Extract
   |
   v
Bronze
   |
   v
Silver
   |
   +----> Gold: Airline Performance
   |
   +----> Gold: Airport Performance
   |
   +----> Gold: Route Performance

---

## 6. Gold Upload to Amazon S3

Gold datasets can be uploaded to Amazon S3 using:

python -m pipeline.load.upload

Expected output includes:

Subiendo Gold a S3...
Total archivos subidos: 3
Gold subido a S3: 3 archivos

The upload process preserves the Gold directory structure.

---

## 7. Validate S3 Output

List the Gold datasets:

aws s3 ls s3://flight-data-engineering-karen-2026/flight-data-engineering/gold/ --recursive

Expected datasets:

flight-data-engineering/gold/
├── airline_performance/
│   └── airline_performance.parquet
├── airport_performance/
│   └── airport_performance.parquet
└── route_performance/
    └── route_performance.parquet

---

## 8. Local Data Validation

Check the generated Gold directory:

find data/gold -type f

Expected outputs:

data/gold/airline_performance/airline_performance.parquet
data/gold/airport_performance/airport_performance.parquet
data/gold/route_performance/route_performance.parquet

---

## 9. Testing

Run the automated tests:

make test

A successful execution indicates that the current test suite completed without failures.

---

## 10. Code Validation

Run the compilation check:

make lint

No Python syntax errors should be reported.

---

## 11. Re-running the Pipeline

The pipeline can be re-executed after code changes or failures.

Run:

make run

Then upload the Gold datasets:

python -m pipeline.load.upload

---

## 12. Re-running Individual Gold Processes

Airline performance:

python -c "from pipeline.gold import create_airline_performance; create_airline_performance()"

Airport performance:

python -c "from pipeline.airport_performance import create_airport_performance; create_airport_performance()"

Route performance:

python -c "from pipeline.route_performance import create_route_performance; create_route_performance()"

After regeneration:

python -m pipeline.load.upload

---

## 13. Backfill Procedure

A backfill consists of reprocessing historical data for a specific period.

The pipeline uses event_date as the logical partitioning column.

Expected structure:

silver/
└── dataset/
    ├── event_date=2024-01-01/
    ├── event_date=2024-01-02/
    └── event_date=2024-01-03/

For a backfill:

1. Identify the affected date range.
2. Verify that the corresponding input data is available.
3. Re-run the extraction and transformation process.
4. Validate the resulting Silver partitions.
5. Regenerate the affected Gold datasets.
6. Upload the updated Gold outputs to S3.
7. Validate the final S3 objects.

---

## 14. Troubleshooting

### 14.1 Pipeline module cannot be found

If Python reports:

ModuleNotFoundError: No module named 'pipeline'

Verify that the virtual environment is active:

source .venv/bin/activate

Verify the current directory:

pwd

The command should be executed from the project root.

### 14.2 AWS credentials error

Verify:

aws sts get-caller-identity

If this command fails, check the AWS CLI configuration and credentials.

Do not store AWS credentials inside the repository.

### 14.3 S3 AccessDenied

If an upload returns AccessDenied, verify that the AWS identity has permission to write to the configured bucket.

### 14.4 S3 bucket does not exist

Verify the available buckets:

aws s3 ls

Then verify the target prefix:

aws s3 ls s3://flight-data-engineering-karen-2026/flight-data-engineering/

### 14.5 No Parquet files found

Verify:

find data/silver -type f

Expected structure:

data/silver/
└── event_date=YYYY-MM-DD/
    └── *.parquet

If Silver is empty, re-run the preceding pipeline stages.

### 14.6 Pipeline produces incorrect results

Check:

1. Input dataset.
2. Silver partitions.
3. Data types.
4. Data quality rules.
5. Enrichment catalogs.
6. Gold aggregation logic.

Compare the generated output with the expected data contract.

---

## 15. Data Quality Checks

Before considering an execution successful, verify:

- Required columns are present.
- event_date contains valid dates.
- Airport codes are populated.
- Carrier codes are populated.
- Numeric columns contain valid numeric values.
- Silver partitions are generated correctly.
- Gold datasets contain records.
- Gold metrics contain valid numerical values.
- S3 objects exist after upload.

Data contracts are stored in:

data_contract/schema/

---

## 16. Gold Dataset Validation

### Airline Performance

Required fields:

op_unique_carrier
total_flights
cancelled_flights
diverted_flights
delayed_flights
avg_arr_delay
cancellation_rate
delay_rate

### Airport Performance

Required fields:

airport
total_departures
cancelled_departures
diverted_departures
delayed_arrivals
total_arrivals
arrival_delay_rate
cancellation_rate
avg_arrival_delay

### Route Performance

Required fields:

origin
dest
total_flights
cancelled_flights
diverted_flights
delayed_flights
avg_arrival_delay
avg_distance
delay_rate
cancellation_rate

---

## 17. Operational Checklist

Before execution:

- Virtual environment activated.
- Dependencies installed.
- AWS credentials available.
- Input data available.
- S3 bucket accessible.

After execution:

- Bronze generated.
- Silver partitions generated.
- Gold datasets generated.
- Tests pass.
- Code compilation succeeds.
- Gold datasets uploaded to S3.
- S3 objects verified.

---

## 18. Recovery Procedure

If the pipeline fails:

1. Identify the failed stage.
2. Review the terminal output.
3. Verify input files.
4. Verify local directory structure.
5. Verify AWS credentials if the failure occurs during upload.
6. Re-run only the affected stage when possible.
7. Validate the resulting dataset.
8. Re-upload Gold datasets if necessary.

The pipeline is designed with separate processing stages so individual Gold datasets can be regenerated independently.

---

## 19. Deployment and Automation

The current implementation is designed to run locally and upload the resulting datasets to Amazon S3.

The architecture is prepared for future cloud automation using AWS managed services such as:

- AWS Glue
- AWS Lambda
- AWS Step Functions
- Amazon MWAA
- Amazon CloudWatch
- Amazon Athena

These services are considered future evolution paths rather than mandatory dependencies of the current implementation.

---

## 20. Security Guidelines

Never commit:

.env
AWS credentials
Access keys
Secret keys
Private keys
Service account credentials

The repository .gitignore excludes sensitive credential files.

AWS authentication should be handled through the AWS CLI configuration, environment variables, IAM roles, or another approved credential mechanism.

---

## 21. Performance Considerations

The current implementation uses Python and Pandas with chunked processing to avoid loading the complete input dataset into memory at once.

The pipeline is suitable for the current project dataset and provides a migration path toward distributed processing.

For substantially larger datasets, future implementations may use:

- AWS Glue
- PySpark
- Amazon EMR
- Distributed Parquet processing

The current architecture intentionally avoids introducing distributed processing complexity where it is not required by the current dataset size.

---

## 22. Git Workflow

Check the repository:

git status

Review changes:

git diff

Stage changes:

git add <file>

Create a commit:

git commit -m "Description of change"

Push to GitHub:

git push origin main

Verify:

git status

Expected result:

nothing to commit, working tree clean

---

## 23. Final Operational Flow

The recommended operational sequence is:

source .venv/bin/activate

make install

make test

make lint

make run

python -m pipeline.load.upload

aws s3 ls s3://flight-data-engineering-karen-2026/flight-data-engineering/gold/ --recursive

A successful execution should result in:

Bronze generated
Silver generated
Gold generated
Tests passed
Compilation successful
Gold uploaded to S3
S3 objects verified

---

## 24. Summary

This runbook provides the operational procedures for the Flight Data Engineering 2024 project.

It covers:

- Environment setup.
- Pipeline execution.
- Testing.
- Code validation.
- Gold generation.
- S3 uploads.
- Backfill procedures.
- Troubleshooting.
- Data quality validation.
- Recovery procedures.
- Security guidelines.
- Performance considerations.
- Git workflow.

The document should be updated whenever the pipeline architecture, execution commands, cloud infrastructure, or operational procedures change.
