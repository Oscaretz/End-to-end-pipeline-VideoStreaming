# Airflow DAGs Documentation

This document describes the Apache Airflow DAGs used to orchestrate the video streaming data pipeline. The pipeline implements a Medallion architecture (Bronze → Silver → Gold) for data warehousing and analytics.

## Table of Contents

- [Overview](#overview)
- [DAG Architecture](#dag-architecture)
- [DAG Details](#dag-details)
- [Execution Order](#execution-order)
- [Configuration](#configuration)
- [Dependencies](#dependencies)

## Overview

The pipeline consists of 5 main DAGs that handle:
1. Data warehouse schema creation
2. Data ingestion from multiple sources
3. Bronze to Silver transformation
4. JSON content loading
5. Silver to Gold analytics generation

All DAGs are configured with manual triggering (`schedule_interval=None`) and do not perform catchup operations.

## DAG Architecture

```
DAG 1: Schema Creation
   ↓
DAG 2: Data Ingestion (CSV + JSON)
   ↓
DAG 3a: Bronze → Silver (SQL Transform)
DAG 3b: JSON Content Loader
   ↓
DAG 4: Silver → Gold (Analytics)
```

## DAG Details

### DAG 1: `dag_1_dw_layers_generator`

**Purpose:** Creates the initial data warehouse structure with Bronze, Silver, and Gold schemas.

**File:** `dag_1_dw_layers_generator.py`

**Tasks:**
- `create_data_warehouse_task`: Executes `generate_layer_schemas()` to create database schemas

**Configuration:**
- Owner: airflow
- Start Date: 2025-05-01
- Retries: 1
- Schedule: Manual trigger only

**When to run:** 
- First time setup
- After database reset
- When schema modifications are needed

---

### DAG 2: `dag_2_data_ingesters`

**Purpose:** Ingests raw data from CSV and JSON files into Bronze layer tables.

**File:** `dag_2_data_ingesters.py`

**Tasks:**

1. **`create_schemas_task`**
   - Creates database schemas before ingestion
   - Ensures database structure exists

2. **`ingest_to_mongo_task`**
   - Ingests `content.json` to MongoDB
   - Handles JSON content data

3. **`ingest_to_mssql_task_1`**
   - Ingests `users.csv` to MS SQL Server
   - Loads user information to bronze.users

4. **`ingest_to_mssql_task_2`**
   - Ingests `viewing_sessions.csv` to MS SQL Server
   - Loads viewing session data to bronze.viewing_sessions

**Task Dependencies:**
```
create_schemas_task >> [ingest_to_mongo_task, ingest_to_mssql_task_1, ingest_to_mssql_task_2]
ingest_to_mongo_task >> ingest_to_mssql_task_1 >> ingest_to_mssql_task_2
```

**Configuration:**
- Owner: airflow
- Start Date: 2025-05-01
- Retries: 1
- Schedule: Manual trigger only

**Data Sources:**
- `/opt/airflow/data/portfolio/content.json`
- `/opt/airflow/data/portfolio/users.csv`
- `/opt/airflow/data/portfolio/viewing_sessions.csv`

---

### DAG 3a: `dag_3_data_transformer_bronze`

**Purpose:** Transforms raw Bronze data into cleaned Silver layer tables.

**File:** `dag_3_data_transformer_bronze.py`

**Tasks:**

1. **`start_bronze_transformation`** (DummyOperator)
   - Marks start of transformation process

2. **`bronze_to_silver_sql`**
   - Executes `/opt/airflow/sql/bronze_to_silver.sql`
   - Applies data cleaning and filtering rules
   - Creates:
     - `silver_users` (users with >100h watch time)
     - `silver_viewing_sessions` (valid sessions)
     - `silver_content` (content viewed by active users)

3. **`bronze_transformation_complete`** (DummyOperator)
   - Marks completion of transformation

**Task Dependencies:**
```
start_task >> bronze_to_silver_task >> end_task
```

**Configuration:**
- Owner: data_engineer
- Start Date: 2025-05-01
- Retries: 1
- Schedule: Manual trigger only

---

### DAG 3b: `dag_3_json_content_loader`

**Purpose:** Loads JSON content data directly into the bronze.content table.

**File:** `dag_3_data_transformer_bronze_json.py`

**Tasks:**

1. **`start_json_loading`** (DummyOperator)
   - Marks start of JSON loading process

2. **`load_content_json`**
   - Executes `load_content_json()` function
   - Reads `/opt/airflow/data/portfolio/content.json`
   - Inserts content data into `bronze.content` table

3. **`json_loading_complete`** (DummyOperator)
   - Marks completion of loading

**Task Dependencies:**
```
start_task >> load_json_task >> end_task
```

**Configuration:**
- Owner: data_engineer
- Start Date: 2025-05-01
- Retries: 1
- Schedule: Manual trigger only

---

### DAG 4: `dag_4_silver_to_gold`

**Purpose:** Generates business analytics and aggregated metrics in the Gold layer.

**File:** `dag_4_data_transformer_silver.py`

**Tasks:**

1. **`start_gold_transformation`** (DummyOperator)
   - Marks start of analytics generation

2. **`silver_to_gold_sql`**
   - Executes `/opt/airflow/sql/silver_to_gold.sql`
   - Creates analytical tables:
     - `gold_user_analytics` (user metrics and segmentation)
     - `gold_content_performance` (content KPIs)
     - `gold_country_insights` (geographic analysis)
     - `gold_genre_analytics` (genre performance)
     - `gold_executive_summary` (executive KPIs)
     - `gold_user_segmentation` (segment distribution)

3. **`gold_transformation_complete`** (DummyOperator)
   - Marks completion of analytics

**Task Dependencies:**
```
start_task >> silver_to_gold_task >> end_task
```

**Configuration:**
- Owner: data_engineer
- Start Date: 2025-05-01
- Retries: 1
- Schedule: Manual trigger only

## Execution Order

To run the complete pipeline from scratch:

```
Step 1: Trigger dag_1_dw_layers_generator
        (Creates database schemas)
        ↓
Step 2: Trigger dag_2_data_ingesters
        (Ingests CSV and JSON data)
        ↓
Step 3: Trigger dag_3_json_content_loader
        (Loads content data to Bronze)
        ↓
Step 4: Trigger dag_3_data_transformer_bronze
        (Cleans data to Silver layer)
        ↓
Step 5: Trigger dag_4_silver_to_gold
        (Generates Gold analytics)
```

## Configuration

### Required Python Modules

```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy import DummyOperator
```

### Custom Scripts

All DAGs depend on custom Python scripts located in `/opt/airflow/scripts/`:

- `layerSchemasGenerator.py`: Creates database schemas
- `dataIngestor.py`: Handles CSV and JSON ingestion
- `sql_runner.py`: Executes SQL transformation scripts
- `json_loader.py`: Loads JSON content data

### Configuration Files

- `config.py`: Contains database connection configurations
  - `get_mssql_config()`: MS SQL Server connection parameters
  - `get_mongo_config()`: MongoDB connection parameters

### File Paths

**SQL Scripts:**
- `/opt/airflow/sql/bronze_to_silver.sql`
- `/opt/airflow/sql/silver_to_gold.sql`

**Data Files:**
- `/opt/airflow/data/portfolio/content.json`
- `/opt/airflow/data/portfolio/users.csv`
- `/opt/airflow/data/portfolio/viewing_sessions.csv`

## Dependencies

### System Requirements
- Apache Airflow 2.0+
- Python 3.8+
- MS SQL Server 2019+
- MongoDB 4.4+

### Python Path Configuration

All DAGs include:
```python
import sys
sys.path.append('/opt/airflow')
```

This ensures custom scripts are importable from the Airflow environment.

### Airflow Connections

The following connections must be configured in Airflow:
- `mssql_default`: MS SQL Server connection
- `mongo_default`: MongoDB connection (if applicable)

## Common Operations

### Trigger DAG Manually

```bash
airflow dags trigger dag_1_dw_layers_generator
airflow dags trigger dag_2_data_ingesters
airflow dags trigger dag_3_data_transformer_bronze
airflow dags trigger dag_3_json_content_loader
airflow dags trigger dag_4_silver_to_gold
```

### View DAG Status

```bash
airflow dags list
airflow dags state dag_1_dw_layers_generator
```

### View Task Logs

```bash
airflow tasks logs dag_2_data_ingesters ingest_to_mssql_task_1 2025-05-01
```

## Error Handling

All DAGs are configured with:
- **Retries:** 1 attempt
- **Retry Delay:** Default (5 minutes)
- **Catchup:** Disabled

If a task fails:
1. Check Airflow logs for the specific task
2. Verify database connectivity
3. Ensure data files exist in specified paths
4. Confirm SQL scripts are syntactically correct

## Best Practices

1. **Run DAGs in sequence:** Follow the execution order to ensure data integrity
2. **Monitor logs:** Check Airflow UI for task execution details
3. **Validate data:** Verify record counts after each layer transformation
4. **Backup before transforms:** Silver and Gold layers drop/recreate tables
5. **Test in dev first:** Validate changes in a non-production environment

## Maintenance

### Updating SQL Scripts

After modifying SQL transformation scripts:
1. Update the corresponding SQL file in `/opt/airflow/sql/`
2. Test the SQL script manually first
3. Trigger the appropriate DAG
4. Verify output in Gold layer tables

### Adding New Data Sources

To add new ingestion tasks:
1. Add new task to `dag_2_data_ingesters.py`
2. Update task dependencies
3. Ensure data file is accessible in `/opt/airflow/data/portfolio/`
4. Test ingestion with a subset of data first

## Troubleshooting

### Common Issues

**Issue:** Schema creation fails
- **Solution:** Check if database `mssql_db` exists and user has CREATE SCHEMA permissions

**Issue:** File not found during ingestion
- **Solution:** Verify file paths and ensure data files are mounted in the Airflow container

**Issue:** SQL transformation fails
- **Solution:** Ensure Bronze tables are populated before running Silver transformations

**Issue:** Task stuck in "running" state
- **Solution:** Check database locks, restart Airflow scheduler if needed

## Contact

For questions or issues with the DAGs, contact the Data Engineering team.

---

**Last Updated:** October 2024  
**Version:** 1.0  
**Maintained By:** Data Engineering Team
