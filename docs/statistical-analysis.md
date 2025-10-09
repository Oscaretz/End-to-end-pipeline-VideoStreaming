# Streamlit Benchmark App Documentation - SQL vs NoSQL Comparative Analysis

## Overview

This document describes the architecture and design of the **Streamlit Benchmark App**, which compares the performance and use cases of relational (SQL/SQLite) and non-relational (NoSQL/pandas JSON) approaches. The app benchmarks query execution time, memory consumption, and analytical results across multiple business scenarios such as top products and sales trend analysis.

The goal of the project is to provide a **demonstrative tool** for understanding **when relational databases are more effective** and when **non-relational approaches provide advantages**.

---

## Application Components

### 1. Data Generation
**Technology**: Python + pandas  

Synthetic datasets are generated within the app to simulate an e-commerce scenario:
- Columns: `order_id`, `product`, `price`, `quantity`, `date`
- Adjustable dataset size via Streamlit slider (from 1,000 to 50,000 rows)
- Balanced structure for controlled experiments

![Data-generator](https://github.com/Oscaretz/End-to-end-pipeline-VideoStreaming/blob/widman/images/data-generator.png)


### 2. Relational Database Benchmark
**Technology**: SQLite (in-memory)  

Relational queries are executed against an in-memory SQLite database:
- SQL queries demonstrate **grouping, aggregation, and filtering**
- Example: calculating top-selling products or daily revenue
- Results include **query execution time** and **memory usage**

### 3. Non-Relational Benchmark
**Technology**: pandas (JSON-like simulation)  

NoSQL behavior is simulated using pandas operations:
- GroupBy and aggregation replicate JSON-style document queries
- Flexible schema representation supports semi-structured data
- Performance measured in terms of **execution time** and **memory usage**

---

## Analytical KPIs

The app benchmarks both models across key performance indicators:

1. **Top Products Analysis**
   - SQL: `GROUP BY product` with `SUM(price*quantity)`
   - NoSQL: pandas aggregation with `.groupby("product")`
   - KPI: Identify top 5 products by revenue

![Data-generator](https://github.com/Oscaretz/End-to-end-pipeline-VideoStreaming/blob/widman/images/top_products.png)


3. **Sales Trend Analysis**
   - SQL: Aggregation of revenue by `date`
   - NoSQL: pandas groupby over `date`
   - KPI: Evaluate temporal revenue patterns
  
![Data-generator](https://github.com/Oscaretz/End-to-end-pipeline-VideoStreaming/blob/widman/images/sales_trend.png)


4. **Performance Metrics**
   - Execution time per query (seconds)
   - Memory consumption (MB)
   - Visual comparisons via bar charts
![Data-generator](https://github.com/Oscaretz/End-to-end-pipeline-VideoStreaming/blob/widman/images/compute_consumption.png)


---

## Streamlit Interface

The Streamlit app is structured in the following sections:

- **Dataset Generation:** slider to select number of rows, preview of sample dataset
- **Relational DB Section:** SQL queries, execution metrics, top results
- **Non-Relational DB Section:** equivalent pandas aggregations, metrics, results
- **Performance Comparison:** bar charts comparing **time** and **memory usage**
- **Sales Trend Analysis:** side-by-side line charts for SQL and NoSQL
- **Insights Section:** textual guidance on when to use SQL vs NoSQL

---

## Technology Stack

| Layer               | Technology   | Purpose                                |
|---------------------|-------------|----------------------------------------|
| Data Generation     | Python + pandas | Create synthetic datasets             |
| Relational Benchmark| SQLite       | Execute SQL queries on tabular data    |
| Non-Relational Sim. | pandas (JSON) | Simulate NoSQL queries                |
| Visualization       | Streamlit + Plotly | UI, benchmarking charts, comparisons |

---

## Key Benefits

### Comparative Analysis
- Side-by-side demonstration of SQL vs NoSQL
- Clear visualization of **performance trade-offs**
- Realistic business KPIs for contextual understanding

### Educational Value
- Provides **learning tool** for database architecture decisions
- Showcases when relational systems excel (structured queries, joins)
- Demonstrates NoSQL advantages (flexibility, schema evolution)

### Lightweight Deployment
- Entire app runs locally with Streamlit
- SQLite in-memory for simplicity
- No external database configuration required

---

## Best Practices Applied

- **Benchmarking Framework:** consistent measurement of time and memory
- **Transparent Queries:** SQL and pandas queries shown in interface
- **Interactive UI:** allows dataset scaling and dynamic experimentation
- **Separation of Concerns:** distinct functions for SQL and NoSQL benchmarks
- **Reproducibility:** fixed data generation logic for consistent comparisons

---

## Future Enhancements

- Extend to **PostgreSQL** for production-grade SQL benchmarking
- Add **MongoDB or Redis integration** for true NoSQL backends
- Implement **joins and nested queries** for advanced SQL scenarios
- Add **nested JSON structures** to better represent NoSQL advantages
- Enhance visualization with **parallel coordinates** for performance profiling
- Integration with **cloud-hosted datasets** for large-scale benchmarking

---

