# Architecture — Flight Data Engineering 2024

## 1. Overview

This project implements an end-to-end batch data engineering pipeline for processing flight data from 2024.

The pipeline follows a Medallion Architecture:

```text
Sources
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
Enrichment
   |
   v
Gold (Serving)
   |
   v
Amazon S3
```

The implementation uses Python and Amazon Web Services (AWS), with Parquet as the primary storage format.

The pipeline processes approximately 7 million flight records and applies chunk-based processing, date partitioning, data quality validations, catalog enrichment, and analytical aggregations.

---

## 2. Logical Architecture

The logical data flow is:

```text
Flight Data Source
        |
        v
   Extraction
        |
        v
      Bronze
        |
        | Cleaning
        | Type conversion
        | Data Quality
        v
      Silver
        |
        | Airport enrichment
        | Airline enrichment
        v
   Silver Enriched
        |
        | Aggregations
        | Business metrics
        v
       Gold
        |
        v
    Amazon S3
```

### Main datasets

The pipeline uses three logical sources:

* Flight data
* Airport catalog
* Airline catalog

The flight dataset contains the transactional flight information, while the airport and airline catalogs are used during the enrichment stage.

---

## 3. AWS Architecture

AWS is the cloud provider selected for this project.

The main cloud storage layer is Amazon S3.

```text
                         ┌─────────────────────┐
                         │   Flight CSV Source │
                         └──────────┬──────────┘
                                    |
                                    v
                         ┌─────────────────────┐
                         │       Python        │
                         │      Extract        │
                         └──────────┬──────────┘
                                    |
                                    v
                  ┌─────────────────────────────────┐
                  │          Amazon S3               │
                  │            Bronze                │
                  │                                 │
                  │ flights/event_date=YYYY-MM-DD/ │
                  └──────────────┬──────────────────┘
                                 |
                                 v
                  ┌─────────────────────────────────┐
                  │          Transformation         │
                  │             Python              │
                  │                                 │
                  │ Cleaning / typing / DQ / chunks │
                  └──────────────┬──────────────────┘
                                 |
                                 v
                  ┌─────────────────────────────────┐
                  │          Amazon S3               │
                  │            Silver                │
                  │                                 │
                  │ flights/event_date=YYYY-MM-DD/ │
                  └──────────────┬──────────────────┘
                                 |
                                 v
                  ┌─────────────────────────────────┐
                  │           Enrichment             │
                  │                                 │
                  │ Airports + Airlines catalogs    │
                  └──────────────┬──────────────────┘
                                 |
                                 v
                  ┌─────────────────────────────────┐
                  │              Gold               │
                  │                                 │
                  │ airline_performance             │
                  │ airport_performance              │
                  │ route_performance                │
                  └──────────────┬──────────────────┘
                                 |
                                 v
                         ┌─────────────────┐
                         │   Amazon S3     │
                         │  Gold / Serving │
                         └─────────────────┘
```

---

## 4. AWS Service Mapping

| Logical Layer   | AWS Service / Technology    | Purpose                        |
| --------------- | --------------------------- | ------------------------------ |
| Source          | Local CSV / external source | Original flight data           |
| Extract         | Python                      | Data ingestion                 |
| Bronze          | Amazon S3                   | Raw data storage               |
| Transform       | Python / Pandas             | Cleaning and transformation    |
| Silver          | Amazon S3 + Parquet         | Curated datasets               |
| Enrichment      | Python / Pandas             | Airport and airline enrichment |
| Gold            | Amazon S3 + Parquet         | Analytical datasets            |
| Version control | Git / GitHub                | Source code management         |
| Testing         | Pytest                      | Automated tests                |
| CI              | GitHub Actions              | Continuous validation          |

The current implementation uses Python and Pandas for transformations. The architecture is designed so that the transformation layer can be migrated to a distributed processing framework such as PySpark/AWS Glue if future data volumes require it.

---

## 5. Data Partitioning

The pipeline partitions flight data by event date.

The partitioning convention is:

```text
event_date=YYYY-MM-DD/
```

Example:

```text
bronze/flights/event_date=2024-01-01/
bronze/flights/event_date=2024-01-02/
bronze/flights/event_date=2024-01-03/
```

The same logical partitioning strategy is applied to Silver.

Partitioning allows the pipeline and future analytical queries to process only the required dates instead of scanning the entire dataset.

---

## 6. Processing Strategy

The pipeline processes large files incrementally using chunks.

The enrichment process uses a chunk size of:

```text
100,000 records
```

This avoids loading the entire dataset into memory during transformation.

The pipeline processes more than seven million flight records while controlling memory consumption through chunk-based processing.

This approach provides a practical balance between processing performance and resource consumption in a single-machine environment.

---

## 7. Why Pandas Instead of PySpark?

The project processes approximately 7 million records, which is a significant volume but remains manageable in a single-machine environment when using chunk-based processing.

Pandas was selected because:

* The project can process the dataset locally without requiring a distributed cluster.
* Chunk-based processing limits memory consumption.
* Development and testing are simpler.
* The current dataset does not require distributed computing to complete the ETL process.
* The project remains reproducible in a local development environment.

The architecture remains compatible with a future migration to PySpark and AWS Glue.

If the dataset grows substantially, processing becomes distributed, or transformation requirements exceed the resources of a single machine, PySpark/AWS Glue would be an appropriate evolution of the transformation layer.

---

## 8. Gold Layer

The Gold layer contains analytical datasets designed for downstream consumption.

### Airline Performance

Contains metrics such as:

* Total flights
* Cancelled flights
* Diverted flights
* Delayed flights
* Average arrival delay
* Cancellation rate
* Delay rate

### Airport Performance

Contains metrics such as:

* Total departures
* Cancelled departures
* Diverted departures
* Delayed arrivals
* Arrival delay rate
* Cancellation rate
* Average arrival delay

### Route Performance

Contains metrics such as:

* Origin airport
* Destination airport
* Total flights
* Cancelled flights
* Diverted flights
* Delayed flights
* Average arrival delay
* Average distance
* Delay rate
* Cancellation rate

---

## 9. Data Quality

The Silver transformation includes validation and standardization processes before data is used by the Gold layer.

The pipeline validates and transforms flight records before generating analytical datasets.

Automated tests are executed through:

```bash
make test
```

Compilation validation is executed through:

```bash
make lint
```

The pipeline also reports processing results and generated outputs during execution.

---

## 10. Error Handling

The pipeline validates that expected input files and directories exist before processing.

Examples include:

* Missing input files
* Missing directories
* Invalid processing paths
* Failed file operations

The transformation pipeline reports processing results and generated chunks.

The S3 upload module also validates that the local files or directories exist before attempting an upload.

This allows execution results to be verified after each stage.

---

## 11. Risks and Mitigations

### Source schema changes

**Risk:** The source dataset may change column names, data types, or required fields.

**Mitigation:** Define explicit schemas and validate required columns before processing.

### Corrupted or incomplete files

**Risk:** A source file may be incomplete or unreadable.

**Mitigation:** Validate files before processing and report failed files separately.

### Memory limitations

**Risk:** Loading the complete dataset into memory may cause excessive memory consumption.

**Mitigation:** Process data using chunks and partition data by event date.

### Duplicate records

**Risk:** Reprocessing or duplicated source records may generate duplicate data.

**Mitigation:** Apply deduplication rules during the Silver transformation.

### Cloud storage failures

**Risk:** Upload operations to S3 may fail.

**Mitigation:** Validate upload results and use repeatable upload or synchronization operations.

### Data quality issues

**Risk:** Invalid or missing values may affect analytical results.

**Mitigation:** Apply validation and standardization during the Silver layer before generating Gold datasets.

---

## 12. Observability

The current pipeline provides basic execution observability through console logs.

Examples include:

```text
Records processed
Files with errors
Chunks generated
Files uploaded
Gold datasets generated
```

For a production deployment, the pipeline could be extended with:

* Amazon CloudWatch Logs
* CloudWatch metrics
* Alerts for failed executions
* Processing duration metrics
* Number of records processed per partition
* Number of rejected records

---

## 13. Security Considerations

The project avoids storing cloud credentials inside the repository.

Credentials should be provided through the AWS CLI credential configuration, environment variables, or IAM roles.

Sensitive files such as:

```text
.env
credentials/
*.key
*.pem
```

are excluded through `.gitignore`.

For a production deployment, IAM roles with least-privilege permissions should be used for S3 access.

---

## 14. Scalability

The current architecture is designed to scale through several mechanisms:

1. Date-based partitioning.
2. Parquet columnar storage.
3. Chunk-based processing.
4. Separation between Bronze, Silver, and Gold.
5. Cloud storage using Amazon S3.
6. Ability to migrate transformations to PySpark/AWS Glue.

The current implementation is appropriate for the available dataset and development environment.

A future production implementation could introduce distributed processing and managed orchestration without changing the logical Bronze → Silver → Gold architecture.

---

## 15. Reproducibility

The project provides standardized commands through the Makefile.

Install dependencies:

```bash
make install
```

Run tests:

```bash
make test
```

Validate source compilation:

```bash
make lint
```

Run the pipeline:

```bash
make run
```

The main entry point is:

```bash
python -m pipeline.main
```

Gold datasets can also be uploaded to Amazon S3 through:

```bash
python -m pipeline.load.upload
```

---

## 16. Architecture Decisions

Key technical decisions:

* **AWS S3** was selected as the cloud storage layer.
* **Parquet** was selected as the primary analytical storage format.
* **Event-date partitioning** was selected to organize flight data and reduce unnecessary scans.
* **Pandas with chunk processing** was selected instead of distributed processing because the current dataset can be processed efficiently in a single-machine environment.
* **Bronze/Silver/Gold separation** was implemented to isolate raw, curated, and analytical data responsibilities.
* **Catalog enrichment** was implemented to improve the analytical value of the flight dataset.
* **Python modules** were separated by pipeline responsibility to improve maintainability and testability.

---

## 17. Future Improvements

Potential future improvements include:

* AWS Glue for distributed transformations.
* PySpark for larger datasets.
* Amazon Athena for serverless SQL analytics.
* AWS Step Functions or MWAA for workflow orchestration.
* Amazon CloudWatch for centralized observability.
* Automated data contract validation.
* Additional data quality metrics.
* Automated deployment infrastructure using Terraform.

---

## 18. Summary

The project implements a complete batch data engineering pipeline for flight data using Python and AWS.

The pipeline processes more than seven million records through Bronze, Silver, and Gold layers, applies data quality and enrichment processes, generates analytical datasets, and stores cloud-ready outputs in Amazon S3.

The architecture is intentionally designed to support future migration toward distributed processing and managed AWS services while maintaining clear separation of responsibilities.
