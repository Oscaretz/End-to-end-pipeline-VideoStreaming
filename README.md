# End-to-end-pipeline

### Members of the Team Project:
1. David
2. Oscar
3. Moi
4. Braulio
5. Gerardo
6. Luis

### Diagrams (SQL/NOSQL). [URL](https://lucid.app/lucidchart/ee34690f-7172-449a-80f3-de2d7002e1c3/edit?view_items=EPsPDx5t0L41%2CEPsPiBVdl89u%2CEPsPuXG9BhAP&invitationId=inv_915b0c61-eb64-47a8-9224-390d582777b2)

# Tasks:

## New More urgent Tasks:
* Implement DBT in Docker.
* Decision of what data to use.
* New Diagrams creation for the new data.
* Insertion & Parsing Script to SQL MsSQLServer DB Bronze layer. (Moi)
* Cleaning data from Layer Bronze and inserting them into Silver layer. (Moi)
* Creation of Data Warehouse Model. (Moi)
* Selection of Tables and Fields and inserting them into Gold layer. (Moi)

## General Tasks:
* Creation of cool readme.
* Creation and developing of Notebook with Analysis of Data from Gold layer. (Braulio)
* Creation of Dashboards and Visualizations. (Braulio)

## Extra tasks:
* Creation of Kubernetes env option. (Oscar)
* Play with Terraform and our Infrastructure. (David)


# Video Streaming Analytics Pipeline

## Project Overview

Complete ETL pipeline for streaming platform data analytics, implementing medallion architecture (Bronze → Silver → Gold) using Apache Airflow, SQL Server, and Docker.

## System Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Raw Data      │    │    Bronze    │    │     Silver      │    │      Gold       │
│                 │    │    Layer     │    │     Layer       │    │     Layer       │
├─────────────────┤    ├──────────────┤    ├─────────────────┤    ├─────────────────┤
│ users.csv       │───▶│bronze.users  │───▶│silver_users     │───▶│gold_user_       │
│ viewing_        │    │bronze.viewing│    │silver_viewing_  │    │analytics        │
│ sessions.csv    │───▶│_sessions     │───▶│sessions         │───▶│gold_content_    │
│ content.json    │───▶│bronze.content│    │silver_content   │    │performance      │
└─────────────────┘    └──────────────┘    └─────────────────┘    │+ 4 more tables  │
                                                                   └─────────────────┘
```

## Data Layer Structure

### Bronze Layer (Raw Data)
- **bronze.users**: User information from CSV files
- **bronze.viewing_sessions**: Viewing sessions from CSV files
- **bronze.content**: Content catalog from JSON (movies and series)

### Silver Layer (Cleaned Data)
- **silver_users**: Active users filtered (100+ hours of viewing)
- **silver_viewing_sessions**: Valid sessions from active users only
- **silver_content**: Content with normalized metrics

### Gold Layer (Business Metrics)
- **gold_user_analytics**: Complete user analysis with segmentation
- **gold_content_performance**: Content performance and ROI metrics
- **gold_country_insights**: Comparative analysis by country
- **gold_genre_analytics**: Performance and trends by genre
- **gold_executive_summary**: Executive KPIs for dashboards
- **gold_user_segmentation**: User segment distribution

## Technical Components

### Airflow DAGs

1. **dag_1_csv_loader** - Loads CSV files to Bronze layer
2. **dag_2_json_content_loader** - Processes JSON content to Bronze layer
3. **dag_3_data_transformer_bronze** - Bronze → Silver transformation
4. **dag_4_silver_to_gold** - Silver → Gold transformation

### Processing Scripts

- **sql_runner.py**: SQL script executor with connection handling
- **json_loader.py**: Specialized JSON file processor
- **config.py**: Database connection configurations

### SQL Scripts

- **bronze_to_silver.sql**: Data cleaning and filtering transformations
- **silver_to_gold.sql**: Business analytics metrics generation

## Installation and Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.8+
- Apache Airflow
- SQL Server 2019

### Environment Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd End-to-end-pipeline-VideoStreaming

# 2. Start services
docker-compose up -d

# 3. Verify active services
docker ps
```

### Environment Variables

```env
MSSQL_SERVER=mssql_db
MSSQL_DATABASE=mssql_db
MSSQL_USER=sa
MSSQL_PASSWORD=your_secure_password
MSSQL_PORT=1433
```

## Project Structure

```
End-to-end-pipeline-VideoStreaming/
├── dags/
│   ├── dag_1_csv_loader.py
│   ├── dag_2_json_content_loader.py
│   ├── dag_3_data_transformer_bronze.py
│   └── dag_4_silver_to_gold.py
├── scripts/
│   ├── sql_runner.py
│   └── json_loader.py
├── sql/
│   ├── bronze_to_silver.sql
│   └── silver_to_gold.sql
├── data/
│   ├── users.csv
│   ├── viewing_sessions.csv
│   └── content.json
├── mssql-data/          # Data persistence
├── docker-compose.yaml
├── config.py
└── README.md
```

## Execution Order

### Step 1: Data Loading (Bronze Layer)
```bash
# Execute DAGs in Airflow UI:
1. dag_1_csv_loader         # Loads users.csv and viewing_sessions.csv
2. dag_2_json_content_loader # Loads content.json
```

### Step 2: Data Transformations
```bash
3. dag_3_data_transformer_bronze # Bronze → Silver
4. dag_4_silver_to_gold         # Silver → Gold
```

## Business Metrics Generated

### User Analytics
- Automatic segmentation (Power/Heavy/Regular/Light User)
- User engagement metrics
- Demographic analysis by country

### Content Performance
- Content ROI (views vs production budget)
- Average completion rates
- Rating-based categorization

### Executive KPIs
- Total active users (100+ hours)
- Available content catalog
- Total viewing sessions
- Average user engagement

## Data Verification

### Database Connection
```bash
# Verify created tables
docker exec -it mssql_db /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P 'your_secure_password' -C -Q "USE mssql_db; SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'bronze' OR TABLE_NAME LIKE 'silver_%' OR TABLE_NAME LIKE 'gold_%' ORDER BY TABLE_SCHEMA, TABLE_NAME;"
```

### Data Validation
```sql
-- Records summary by layer
SELECT 
    'Bronze Users' as layer, COUNT(*) as records FROM bronze.users
UNION ALL SELECT 'Silver Users', COUNT(*) FROM silver_users  
UNION ALL SELECT 'Gold Analytics', COUNT(*) FROM gold_user_analytics;
```

## Dashboard Access

### Connection Configuration
- **Host**: localhost:1433 (or server IP)
- **Database**: mssql_db
- **Username**: sa
- **Password**: your_secure_password

### Recommended Tables for Visualization
- `gold_executive_summary` → Main metrics
- `gold_user_segmentation` → Distribution charts
- `gold_country_insights` → Geographic analysis
- `gold_content_performance` → Content rankings

## Technologies Used

- **Orchestration**: Apache Airflow
- **Database**: Microsoft SQL Server 2019
- **Containers**: Docker & Docker Compose
- **Languages**: Python, SQL
- **Architecture**: Medallion (Bronze/Silver/Gold)

## Troubleshooting

### SQL Server Connection Issues
```bash
# Restart SQL Server container
docker restart mssql_db

# Check logs
docker logs mssql_db --tail 50
```

### Airflow DAG Issues
```bash
# Access Airflow logs
docker logs airflow_webserver
docker logs airflow_scheduler
```

## Data Persistence

Data persists in `./mssql-data/` thanks to the Docker Compose volume configuration. Data remains available even after container restarts.

## Pipeline Results

- **Bronze**: 3 tables with raw data
- **Silver**: 3 tables with cleaned data (users with 100+ hours)
- **Gold**: 6 analytical tables ready for dashboards
- **Total**: 4,271 active users, 300 content items, 191,807 sessions

## Key Features

### Business Logic Implementation
- User filtering by engagement threshold (100+ viewing hours)
- Content ROI calculations (views per million budget)
- Automatic user segmentation based on viewing patterns
- Geographic insights for market analysis
- Genre performance analytics

### Data Quality Measures
- Data type validation and conversion
- NULL value handling
- Duplicate record removal
- Business rule enforcement

### Scalability Design
- Modular DAG structure
- Parameterized configurations
- Volume-based data persistence
- Container orchestration ready

## Academic Project Context

This pipeline demonstrates implementation of modern data engineering principles including:
- ETL/ELT methodologies
- Medallion architecture patterns
- Data warehouse dimensional modeling
- Business intelligence preparation
- Infrastructure as Code (IaC)

The project showcases skills in data pipeline orchestration, SQL-based transformations, containerized deployment, and business analytics preparation suitable for streaming platform decision-making.

## DASHBOARD LINK

https://advanced-data-visualization-storytelling.streamlit.app/


