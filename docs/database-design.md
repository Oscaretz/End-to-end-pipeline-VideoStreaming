# Database Design Documentation  
E-Commerce Analytics Project  

## Overview  

This document describes the overall database design for the E-Commerce Analytics Project. The schema integrates multiple data domains including sales, product catalog, warehouse operations, and expenses. The database structure supports the full data lifecycle across all layers of the ETL pipeline, from ingestion to analytics, ensuring consistency, traceability, and analytical readiness.

## Design Principles  

- Normalization and consistency across all data domains  
- Traceability of each record through identifiers and timestamps  
- Data integrity through standardization and validation  
- Analytical readiness for reporting and BI consumption  

## Entity Overview  

| Table Name | Business Domain | Description |
|-------------|-----------------|--------------|
| AmazonSales | E-commerce transactions | Amazon order records with detailed attributes such as fulfillment, SKU, category, and shipping information. |
| CloudWarehouse | Inventory operations | Warehouse operations data capturing inbound or outbound stock movement and pricing. |
| ExpenseIIGF | Financials | Expense logs detailing business costs like materials or packaging. |
| InternationalSales | Global transactions | International customer orders with currency conversions and product details. |
| May2022 | Product catalog (latest) | Catalog with product metadata, pricing, and channel-specific MRPs. |
| PL_March2021 | Product catalog (historical) | Earlier catalog version used for comparison and trend analysis. |
| SaleReport | Inventory status | Stock report by SKU, category, size, and color for availability tracking. |

## Table Structures  

### 1. AmazonSales  

**Primary Key:** Order_ID  

| Column | Data Type | Description |
|---------|------------|-------------|
| Order_ID | nvarchar | Unique order identifier |
| Date | nvarchar | Order date |
| Status | nvarchar | Order status |
| Fulfilment | nvarchar | Fulfillment type |
| Sales_Channel_ | nvarchar | Platform source |
| ship-service-level | nvarchar | Shipping tier |
| Style | nvarchar | Product style code |
| SKU | nvarchar | Stock Keeping Unit |
| Category | nvarchar | Product category |
| Size | nvarchar | Product size |
| ASIN | nvarchar | Amazon Standard ID |
| Qty | int | Quantity ordered |
| Amount | float | Order amount |
| ship-city | nvarchar | Destination city |
| ship-state | nvarchar | Destination state |
| ship-country | nvarchar | Destination country |
| currency | nvarchar | Currency code |
| fulfilled-by | nvarchar | Fulfillment service |

### 2. CloudWarehouse  

**Primary Key:** Index  

| Column | Data Type | Description |
|---------|------------|-------------|
| Operation | nvarchar | Type of operation |
| Price_INR | float | Local currency price |
| Price_Numeric | float | Numeric price format |

### 3. ExpenseIIGF  

**Primary Key:** Composite (Date, Expense_Type)  

| Column | Data Type | Description |
|---------|------------|-------------|
| Date | nvarchar | Expense date |
| Expense_Type | nvarchar | Category of expense |
| Amount | int | Expense amount |

### 4. InternationalSales  

**Primary Key:** Composite (DATE, CUSTOMER, Style)  

| Column | Data Type | Description |
|---------|------------|-------------|
| DATE | nvarchar | Order date |
| CUSTOMER | nvarchar | Buyer name |
| Style | nvarchar | Product style |
| SKU | nvarchar | SKU identifier |
| PCS | int | Quantity |
| RATE | float | Price per unit |
| GROSS_AMT | float | Total amount |

### 5. May2022  

**Primary Key:** Sku  

| Column | Data Type | Description |
|---------|------------|-------------|
| Sku | nvarchar | Unique SKU identifier |
| Style_Id | nvarchar | Product style ID |
| Catalog | nvarchar | Product collection |
| Category | nvarchar | Product type |
| Weight | float | Product weight |
| TP | float | Transfer price |
| MRP_Old | float | Previous MRP |
| Final_MRP_Old | float | Adjusted old MRP |
| Amazon_MRP | float | Amazon listed MRP |
| Flipkart_MRP | float | Flipkart listed MRP |
| Myntra_MRP | float | Myntra listed MRP |
| Snapdeal_MRP | float | Snapdeal listed MRP |

### 6. PL_March2021  

**Primary Key:** Sku  

| Column | Data Type | Description |
|---------|------------|-------------|
| Sku | nvarchar | SKU identifier |
| TP_1 | float | Primary transfer price |
| TP_2 | float | Secondary transfer price |
| MRP_Old | float | Old retail price |
| Final_MRP_Old | float | Final adjusted price |

### 7. SaleReport  

**Primary Key:** SKU_Code  

| Column | Data Type | Description |
|---------|------------|-------------|
| SKU_Code | nvarchar | SKU identifier |
| Design_No. | nvarchar | Design number |
| Stock | int | Stock available |
| Category | nvarchar | Product category |
| Size | nvarchar | Product size |
| Color | nvarchar | Product color |

## Relationships and Integration  

| Relationship | Description |
|---------------|-------------|
| AmazonSales.SKU ↔ May2022.Sku | Connects transaction records to catalog metadata |
| PL_March2021.Sku ↔ May2022.Sku | Enables price comparison between historical and current data |
| SaleReport.SKU_Code ↔ May2022.Sku | Maps inventory data to product catalog |
| CloudWarehouse.Operation ↔ AmazonSales.Fulfilment | Links warehouse operations to sales fulfillment types |

## Data Integrity and Validation  

- Duplicate records resolved using primary key constraints  
- Missing numerical values replaced with 0; categorical with "Unknown"  
- Data type enforcement and validation applied at ingestion  
- Referential integrity maintained through consistent keys  

## Purpose in the ETL Pipeline  

| Stage | Description |
|--------|-------------|
| Bronze | Raw CSV data ingestion |
| Silver | Cleansing, standardization, and normalization |
| Gold | Business logic modeling and analytical aggregation where BI tools will be used|

## Benefits  

- Unified and consistent data model across all business domains  
- High-quality, validated, and structured data for analytics  
- Scalable design for integration with new data sources  
- Supports traceability from source to consumption  

## Future Improvements  

- Implement foreign key constraints in the database engine  
- Convert text-based date fields to standard date formats  
- Add data profiling and validation reports  
- Automate schema drift detection and alerting

