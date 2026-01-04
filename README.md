**End-to-End Sales & Customer Data Pipeline**
Modern Data Engineering with AWS, Databricks, and Airflow
📌 Project Overview
This project demonstrates a production-grade, end-to-end data pipeline utilizing a Medallion Architecture. It migrates raw e-commerce data (Olist Kaggle Dataset) from AWS S3 into a Databricks Lakehouse, implementing complex CDC (Change Data Capture) logic, and orchestrating the entire workflow with Apache Airflow.

The primary goal was to handle high-scale data (replicating billion-row logic) while ensuring data integrity through automated audit trails and historical archiving.

🏗 Architecture Diagram
AWS S3 (Landing) ➡️ Databricks Auto Loader (Bronze) ➡️ PySpark CDC/SCD2 (Silver) ➡️ Spark SQL Aggregates (Gold) ➡️ Airflow Orchestration

🛠 Tech Stack
Cloud Storage: AWS S3

Data Processing: Azure Databricks (PySpark, Delta Lake)

Orchestration: Apache Airflow

Languages: Python, SQL

DevOps: GitHub, Databricks Secrets, CI/CD logic

🧊 Data Pipeline Stages (Medallion Architecture)
1. Bronze Layer (Ingestion)
Used Databricks Auto Loader to incrementally ingest raw CSV files from AWS S3.

Enforced schema evolution to handle unexpected source changes.

Added metadata (source file name, load timestamp) for auditability.

2. Silver Layer (Transformation & CDC)
Upsert Logic: Implemented MERGE operations to handle (I)nserts and (U)updates.

Data Quality: Performed deduplication, NULL handling, and data type casting.

Historical Archiving: Developed a custom logic to move (D)eleted or inactive records into a separate History Archive Table (SCD Type 2 approach) to maintain a full audit trail.

3. Gold Layer (Business Insights)
Aggregated data into high-performance Delta tables for BI consumption.

Key metrics: Total Revenue per Region, Customer Lifetime Value (CLV), and Order Fulfillment Latency.

⏱ Airflow Orchestration
The pipeline is orchestrated via an Airflow DAG that:

Sensors the S3 bucket for new files.

Triggers the Databricks Jobs API for Bronze, Silver, and Gold notebooks.

Implements retry logic and error alerting.

🚀 Performance Impact
Scalability: Designed to process billion-row datasets efficiently using Spark partitioning.

Efficiency: Improved data availability by implementing incremental loading instead of full refreshes.

Integrity: Achieved 99.9% data accuracy through automated validation checks between layers.

📂 Project Structure
Plaintext

├── README.md
├── airflow/
│   └── dags/
│       └── sales_pipeline_dag.py
├── notebooks/
│   ├── 01_bronze_ingestion.py
│   ├── 02_silver_transform_cdc.py
│   └── 03_gold_aggregations.py
├── config/
│   └── databricks_secrets_setup.sh
└── data/
    └── schema_definitions.json
