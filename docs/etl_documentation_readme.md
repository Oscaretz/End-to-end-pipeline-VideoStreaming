# ETL Documentation

## Overview
This document provides comprehensive documentation for the ETL (Extract, Transform, Load) pipelines in the END-TO-END-PIPELINE-VIDEOS project. The pipelines are orchestrated using Apache Airflow and implement a Medallion Architecture pattern.

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Apache Airflow Scheduler                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
    ┌─────────────────────────────────────────────────────┐
    │              DAG 1: Layer Generator                 │
    │         Creates Database Schema Structure            │
    └─────────────────────────────────────────────────────┘
                              ↓
    ┌─────────────────────────────────────────────────────┐
    │              DAG 2: Data Ingesters                  │
    │           Raw Data → Bronze Layer                    │
    └─────────────────────────────────────────────────────┘
                              ↓
    ┌─────────────────────────────────────────────────────┐
    │         DAG 3: Bronze Transformers (JSON)           │
    │         JSON Processing → Bronze Layer               │
    └─────────────────────────────────────────────────────┘
                              ↓
    ┌─────────────────────────────────────────────────────┐
    │         DAG 3: Bronze Transformers (CSV)            │
    │         CSV Processing → Bronze Layer                │
    └─────────────────────────────────────────────────────┘
                              ↓
    ┌─────────────────────────────────────────────────────┐
    │         DAG 4: Silver & Gold Transformer            │
    │     Bronze → Silver → Gold (Full Pipeline)          │
    └─────────────────────────────────────────────────────┘
```

---

## DAGs Overview

### DAG 1: `dag_1_dw_layers_generator.py`
**Purpose:** Initialize database schemas and create table structures for all layers

**Schedule:** Manual trigger (run once at setup)

**Tasks:**
1. Create Bronze layer schemas
2. Create Silver layer schemas
3. Create Gold layer schemas
4. Set up indexes and constraints

**Dependencies:**
- PostgreSQL database connection
- MongoDB connection
- SQL DDL scripts in `/sql/relational/DDL/`

**Output:**
- Empty tables ready for data ingestion
- Proper indexes and foreign keys configured

---

### DAG 2: `dag_2_data_ingesters.py`
**Purpose:** Ingest raw data from external sources into Bronze layer

**Schedule:** `@daily` or configurable

**Tasks:**
1. **Read External Data**
   - Source: CSV files (users, viewing_sessions)
   - Source: JSON files (content metadata)
2. **Validate File Existence**
3. **Load to Bronze Layer**
   - Bronze PostgreSQL tables
   - Bronze MongoDB collections
4. **Log Ingestion Metadata**

**Key Scripts:**
- `src/etl/pipelines/externalDataReader.py`
- `src/etl/pipelines/dataIngestor.py`

**Error Handling:**
- Retry mechanism (3 attempts)
- Email alerts on failure
- Data validation checks

---

### DAG 3: `dag_3_data_transformer_bronze_json.py`
**Purpose:** Transform and load JSON data into Bronze layer

**Schedule:** Triggered after DAG 2 completion

**Tasks:**
1. **Extract JSON Content**
   - Parse nested JSON structures
   - Handle arrays and complex objects
2. **Flatten JSON Documents**
3. **Load to Bronze Tables**
   - `bronze_content` table (PostgreSQL)
   - `bronze_content_json` collection (MongoDB)
4. **Data Quality Checks**

**Key Scripts:**
- `src/etl/pipelines/json_loader.py`

**Transformations:**
- JSON flattening for relational storage
- Data type inference
- Null handling

---

### DAG 3 (Alternative): `dag_3_data_transformer_bronze.py`
**Purpose:** Transform and load CSV data into Bronze layer

**Schedule:** Triggered after DAG 2 completion

**Tasks:**
1. **Extract CSV Data**
   - Parse CSV headers
   - Handle encoding issues
2. **Load to Bronze Tables**
   - `bronze_users`
   - `bronze_viewing_sessions`
3. **Add Metadata Columns**
   - ingestion_timestamp
   - source_file

---

### DAG 4: `dag_4_data_transformer_silver.py`
**Purpose:** Transform Bronze → Silver → Gold (complete pipeline)

**Schedule:** `@daily` after Bronze layer completion

**Tasks:**
1. **Bronze to Silver Transformation**
   - Data cleaning and validation
   - Type casting
   - Deduplication
   - Business rule application
   
2. **Silver to Gold Transformation**
   - Aggregations and calculations
   - KPI generation
   - Denormalization for analytics

**SQL Scripts:**
- `sql/relational/bronze_to_silver.sql`
- `sql/relational/silver_to_gold.sql`

**Key Scripts:**
- `src/etl/pipelines/sql_runner.py`
- `src/etl/pipelines/sqlScriptExecutor.py`

**Transformations Applied:**

**Bronze → Silver:**
- Remove duplicates based on primary keys
- Convert string dates to TIMESTAMP
- Normalize categorical values
- Handle missing values
- Apply data quality rules

**Silver → Gold:**
- Calculate user engagement metrics
- Aggregate viewing statistics
- Generate content performance KPIs
- Create denormalized fact tables

---

## ETL Scripts Reference

### `dataIngestor.py`
**Purpose:** Core ingestion logic for loading raw data

**Functions:**
- `ingest_csv()`: Read and load CSV files
- `ingest_json()`: Read and load JSON files
- `validate_data()`: Pre-ingestion validation
- `log_ingestion()`: Audit logging

**Parameters:**
- `source_path`: Path to source file
- `target_table`: Bronze table name
- `file_type`: csv/json
- `batch_size`: Rows per batch (default: 1000)

---

### `externalDataReader.py`
**Purpose:** Read data from external sources with error handling

**Features:**
- Multiple file format support
- Retry mechanism
- Connection pooling
- Memory-efficient streaming

---

### `json_loader.py`
**Purpose:** Specialized JSON handling for nested structures

**Features:**
- Recursive JSON flattening
- Array handling
- Dynamic schema inference
- MongoDB integration

---

### `sql_runner.py`
**Purpose:** Execute SQL scripts for transformations

**Features:**
- Transaction management
- Error rollback
- Query logging
- Performance metrics

**Usage:**
```python
from src.etl.pipelines.sql_runner import SQLRunner

runner = SQLRunner(connection_string)
runner.execute_script('bronze_to_silver.sql')
```

---

### `sqlScriptExecutor.py`
**Purpose:** Batch SQL script execution with dependencies

**Features:**
- Script dependency resolution
- Parallel execution where possible
- Rollback on failure
- Execution history tracking

---

### `layerSchemasGenerator.py`
**Purpose:** Generate table schemas programmatically

**Features:**
- DDL generation from config
- Multi-database support (PostgreSQL, MongoDB)
- Index creation
- Constraint management

---

## Configuration

### Environment Variables (`.env`)
```bash
# Database Connections
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=video_analytics
POSTGRES_USER=etl_user
POSTGRES_PASSWORD=secure_password

MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=video_content

# Airflow
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow

# Data Paths
RAW_DATA_PATH=/data/raw
PROCESSED_DATA_PATH=/data/processed
```

### Airflow Variables
```python
# Set via Airflow UI or CLI
airflow variables set bronze_batch_size 1000
airflow variables set silver_batch_size 5000
airflow variables set enable_data_quality_checks True
```

---

## Data Quality Checks

### Bronze Layer Checks
- ✅ File exists and is readable
- ✅ Non-empty dataset
- ✅ Expected columns present
- ✅ No completely null rows

### Silver Layer Checks
- ✅ Primary key uniqueness
- ✅ Foreign key integrity
- ✅ Data type validation
- ✅ Range checks on numeric fields
- ✅ Date validity
- ✅ Required fields not null

### Gold Layer Checks
- ✅ Aggregation accuracy
- ✅ No negative metrics
- ✅ Logical consistency (e.g., completion rate ≤ 100%)
- ✅ Expected row counts

---

## Error Handling & Monitoring

### Retry Strategy
```python
default_args = {
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'retry_exponential_backoff': True,
}
```

### Alerting
- Email notifications on DAG failure
- Slack integration for critical errors
- PagerDuty for production incidents

### Monitoring Metrics
- DAG execution duration
- Task success/failure rates
- Data volume processed
- Data quality score
- Pipeline latency (end-to-end)

---

## Performance Optimization

### Best Practices Implemented
1. **Batch Processing:** Process data in chunks (1000-5000 rows)
2. **Parallel Tasks:** Independent tasks run concurrently
3. **Incremental Loading:** Only process new/changed data
4. **Connection Pooling:** Reuse database connections
5. **Indexing:** Strategic indexes on join/filter columns
6. **Partitioning:** Time-based partitions for large tables

### Optimization Tips
- Use `COPY` instead of `INSERT` for bulk loads
- Create temporary tables for complex transformations
- Use `EXPLAIN ANALYZE` to optimize slow queries
- Monitor query execution times
- Archive old Bronze layer data

---

## Testing Strategy

### Unit Tests
Located in `/tests/unit/`
- Test individual functions
- Mock external dependencies
- Validate transformations

### Integration Tests
Located in `/tests/integration/`
- Test DAG execution
- Validate data flow between layers
- Check database connectivity

### Data Quality Tests
Located in `/tests/data_quality/`
- Schema validation
- Data integrity checks
- Business rule validation

**Run Tests:**
```bash
pytest tests/
pytest tests/unit/ -v
pytest tests/integration/ --slow
```

---

## Deployment

### Local Development
```bash
# Start Airflow
docker-compose up -d

# Access Airflow UI
http://localhost:8080

# Trigger DAG
airflow dags trigger dag_1_dw_layers_generator
```

### Production Deployment
1. Build Docker images
2. Deploy to Kubernetes/ECS
3. Configure secrets management
4. Set up monitoring dashboards
5. Enable backup strategies

---

## Troubleshooting

### Common Issues

**Problem:** DAG not appearing in Airflow UI
- **Solution:** Check DAG file syntax, ensure it's in `/dags/` folder, restart webserver

**Problem:** Database connection timeout
- **Solution:** Verify connection strings, check network connectivity, increase timeout values

**Problem:** Out of memory during large file processing
- **Solution:** Reduce batch size, increase worker memory, implement streaming

**Problem:** Data quality check failures
- **Solution:** Review source data, update validation rules, check transformation logic

---

## Maintenance

### Daily Tasks
- Monitor DAG execution status
- Review error logs
- Check data quality metrics

### Weekly Tasks
- Analyze pipeline performance
- Review and optimize slow queries
- Update data quality rules

### Monthly Tasks
- Archive old Bronze layer data
- Review and update documentation
- Performance benchmarking
- Dependency updates

---

## Future Enhancements

- [ ] Implement Change Data Capture (CDC)
- [ ] Add real-time streaming pipelines (Kafka)
- [ ] Implement data lineage tracking
- [ ] Add ML model training pipeline
- [ ] Implement data versioning (DVC)
- [ ] Add data catalog (DataHub/Amundsen)
- [ ] Implement cost optimization strategies
- [ ] Add automated data quality reporting

---

## Contact & Support

**Data Engineering Team:**
- Pipeline Issues: data-eng@company.com
- Documentation: Update via Git PRs
- Slack Channel: #data-engineering

**On-Call Rotation:**
- PagerDuty escalation policy configured
- Runbook: `/docs/runbooks/etl-incident-response.md`