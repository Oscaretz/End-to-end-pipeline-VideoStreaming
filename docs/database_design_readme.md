# Database Design

## Overview
This document describes the database architecture for the END-TO-END-PIPELINE-VIDEOS project, implementing a **Medallion Architecture** (Bronze, Silver, Gold) for data lakehouse patterns.

## Architecture Pattern: Medallion

The Medallion Architecture is a data design pattern used to logically organize data in a lakehouse, with the goal of incrementally improving the quality of data as it flows through each layer.

### 🥉 Bronze Layer (Raw Data)
**Purpose:** Landing zone for raw data ingestion

**Characteristics:**
- Exact replica of source data
- No transformations applied
- Maintains data lineage
- Append-only pattern
- Includes metadata (ingestion timestamp, source system)

**Tables:**
- `bronze_content`: Raw video content data from JSON files
- `bronze_users`: Raw user information from CSV
- `bronze_viewing_sessions`: Raw viewing session logs from CSV

**Data Quality:** Minimal validation, preserves source format

---

### 🥈 Silver Layer (Cleaned Data)
**Purpose:** Cleaned, conformed, and validated data

**Characteristics:**
- Data type conversions applied
- Null handling and validation
- Deduplication
- Business rules applied
- Normalized structure
- Efficient for queries

**Tables:**
- `silver_content`: Cleaned video content with proper data types
- `silver_users`: Validated user profiles with standardized formats
- `silver_viewing_sessions`: Processed sessions with timestamp normalization

**Transformations:**
- JSON flattening and parsing
- Date/timestamp standardization
- Data type casting
- Null value handling
- Primary/Foreign key validation

---

### 🥇 Gold Layer (Business-Level Aggregates)
**Purpose:** Analytics-ready, aggregated data for reporting and ML

**Characteristics:**
- Highly denormalized
- Business-level aggregations
- Optimized for read performance
- Ready for BI tools and dashboards
- Pre-calculated metrics

**Tables:**
- `gold_user_engagement`: User-level engagement metrics
- `gold_content_performance`: Content performance analytics
- `gold_viewing_patterns`: Aggregated viewing behavior insights

**Metrics & KPIs:**
- Total watch time per user
- Content completion rates
- Popular content rankings
- User engagement scores
- Peak viewing hours
- Content recommendations data

---

## Database Technologies

### PostgreSQL (Relational Data)
**Used for:** Structured data with defined schemas

**Layers:**
- ✅ Bronze Layer: Raw relational data
- ✅ Silver Layer: Cleaned structured data
- ✅ Gold Layer: Aggregated analytics tables

**Advantages:**
- ACID compliance
- Complex joins and aggregations
- Mature ecosystem
- Strong data integrity

---

### MongoDB (Document Store)
**Used for:** Semi-structured and nested JSON data

**Collections:**
- `bronze_content_json`: Raw nested video metadata
- `silver_content_normalized`: Flattened content documents

**Advantages:**
- Flexible schema
- Handles nested structures naturally
- Horizontal scalability
- JSON-native storage

---

## Data Flow

```
[Source Systems]
    ↓
[Bronze Layer] ← Raw Ingestion
    ↓
[Silver Layer] ← Cleaning & Validation
    ↓
[Gold Layer] ← Aggregation & Analytics
    ↓
[BI Tools / ML Models]
```

---

## Schema Evolution Strategy

**Bronze Layer:**
- Schema-on-read approach
- Supports all source changes automatically

**Silver Layer:**
- Schema-on-write with validation
- Versioned schemas for compatibility

**Gold Layer:**
- Fixed schemas optimized for queries
- Backward compatible changes only

---

## Data Retention Policy

| Layer  | Retention Period | Reason |
|--------|------------------|--------|
| Bronze | 90 days | Reprocessing capability |
| Silver | 1 year | Historical analysis |
| Gold   | 3 years | Long-term analytics & compliance |

---

## Naming Conventions

**Tables:** `{layer}_{entity}`
- Example: `bronze_users`, `silver_content`, `gold_user_engagement`

**Columns:**
- snake_case for all column names
- Suffix `_id` for identifiers
- Suffix `_at` for timestamps
- Suffix `_date` for dates

---

## Performance Optimization

**Indexing Strategy:**
- Primary keys on all ID columns
- Foreign keys for referential integrity
- Composite indexes on common query patterns
- Covering indexes for frequent aggregations

**Partitioning:**
- Time-based partitioning on viewing_sessions
- Range partitioning on content by release_date

---

## Security & Access Control

**Bronze Layer:** Data Engineering team only
**Silver Layer:** Analytics team (read-only)
**Gold Layer:** Business users & BI tools (read-only)

---

## Monitoring & Data Quality

**Metrics Tracked:**
- Row counts per layer
- Data freshness (lag from source)
- Null percentage per column
- Duplicate records detected
- Schema drift detection
