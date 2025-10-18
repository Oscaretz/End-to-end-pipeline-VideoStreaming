# 📺 Video Streaming Data Pipeline

End-to-end data pipeline for video streaming platform analytics, implemented with Medallion architecture (Bronze → Silver → Gold) and orchestrated via Apache Airflow.

## 📋 Table of Contents

- [Architecture](#-architecture)
- [Data Layers](#-data-layers)
- [SQL Scripts](#-sql-scripts)
- [Configuration](#-configuration)
- [Airflow Execution](#-airflow-execution)
- [Analytics & Queries](#-analytics--queries)

## 🏗 Architecture

The project implements a **Medallion** data architecture with three layers:

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Bronze  │ --> │  Silver  │ --> │   Gold   │
│  (Raw)   │     │ (Clean)  │     │(Business)│
└──────────┘     └──────────┘     └──────────┘
```

### Database: `mssql_db`

**Schemas:**
- `bronze`: Raw data from original sources
- `silver`: Cleaned and filtered data
- `gold`: Aggregated metrics and business-ready analytics

## 📊 Data Layers

### Bronze Layer (Raw Data)
Main tables:
- `bronze.users`: User information
- `bronze.content`: Content catalog
- `bronze.viewing_sessions`: Viewing sessions

### Silver Layer (Clean Data)
Applied transformations:
- **`silver_users`**: Users with more than 100 hours of viewing time
- **`silver_viewing_sessions`**: Valid sessions from active users
- **`silver_content`**: Content viewed by active users

### Gold Layer (Analytics)
Analytical tables:
- **`gold_user_analytics`**: Complete user metrics
- **`gold_content_performance`**: Content performance analysis
- **`gold_country_insights`**: Country-level insights
- **`gold_genre_analytics`**: Genre performance metrics
- **`gold_executive_summary`**: Executive KPIs
- **`gold_user_segmentation`**: User segmentation analysis

## 🔧 SQL Scripts

### 1. `schemasCreationQuery.sql`
Creates database and required schemas.

```sql
-- Creates: mssql_db
-- Schemas: bronze, silver, gold
```

**Execution:** First time or after database reset

---

### 2. `bronze_to_silver.sql`
Cleans and filters data from Bronze to Silver.

#### Transformations:

**Users (`silver_users`)**
- ✅ Filter: > 100 hours of viewing time
- ✅ Data type conversion
- ✅ Duplicate removal

**Sessions (`silver_viewing_sessions`)**
- ✅ Active users only (join with silver_users)
- ✅ Duration > 0 minutes
- ✅ Non-null ID validation

**Content (`silver_content`)**
- ✅ Content viewed by active users only
- ✅ Rating normalization (0-5 scale)
- ✅ Default values for missing fields

---

### 3. `silver_to_gold.sql`
Generates aggregated analytical tables.

#### Generated Tables:

**`gold_user_analytics`**
- Metrics: total sessions, average duration, unique content watched
- Segmentation: Power User, Heavy User, Regular User, Light User
- Days since signup calculation

**`gold_content_performance`**
- Total and unique views
- Average completion rate
- ROI per production budget
- Rating categorization

**`gold_country_insights`**
- Total users per country
- Average viewing hours
- Average user age
- Unique content consumed

**`gold_genre_analytics`**
- Genre-based content analysis
- Total and average investment
- Average genre rating
- Watch time metrics

**`gold_executive_summary`**
- Platform KPIs
- Active users (100h+)
- Total sessions
- Average engagement

**`gold_user_segmentation`**
- User distribution by segment
- Average metrics per segment
- Percentage of users in each category

---

### 4. `queries.sql`
Advanced analytical queries for business insights.

#### Available Analytics:

1. **Top 5 most-watched content by country**
   - Uses window functions (ROW_NUMBER)
   - Grouped by country

2. **Retention analysis by subscription type**
   - Calculates % of retained users
   - Compares subscription types

3. **Revenue analysis by genre**
   - Requires: `price_per_hour` column
   - Calculates total revenue per genre

4. **Seasonal viewing patterns**
   - Monthly analysis
   - Average duration and total sessions

5. **Device preference correlation with completion rates**
   - Device-engagement correlation
   - Ordered by completion rate

## ⚙️ Configuration

### Requirements
- SQL Server 2019+
- Apache Airflow 2.0+
- Python 3.8+
- Airflow connection configured: `mssql_default`

### Environment Variables
```bash
AIRFLOW_HOME=/path/to/airflow
SQL_CONN_ID=mssql_default
```

---

**Last updated:** October 2024  
**Version:** 1.0  
**Maintained by:** Data Engineering Team
