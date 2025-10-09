# Visualization Guide
E-Commerce Analytics Project

## Overview

This guide provides step-by-step instructions for connecting Power BI to the E-Commerce Analytics database and creating insightful visualizations. The database follows a medallion architecture (Bronze → Silver → Gold), with the Gold layer optimized for business intelligence and reporting.

## Prerequisites

- Power BI Desktop installed on your machine
- Access to the MSSQL database server
- Completed ETL pipeline execution (all DAGs have run successfully)
- Database: `mssql_db` on `localhost:1433`

## Database Connection

### Step 1: Open Power BI Desktop

Launch Power BI Desktop and select **Get Data** from the Home ribbon.

### Step 2: Select SQL Server

1. In the Get Data dialog, search for "SQL Server"
2. Select **SQL Server** as the data source
3. Click **Connect**

### Step 3: Configure Connection Settings

Enter the following connection details:

- **Server**: `localhost:1433`
- **Database**: `mssql_db`
- **Data Connectivity mode**: 
  - Choose **Import** for better performance with historical data
  - Choose **DirectQuery** for real-time analytics (may impact performance)

### Step 4: Authentication

Select the appropriate authentication method:
- **Windows Authentication** (recommended for local development)
- **Database credentials** (if configured)

### Step 5: Load Tables

After successful connection, you'll see the Navigator window displaying available tables. Load the following Gold layer tables for visualization:

**Core Tables:**
- `AmazonSales` - E-commerce transaction data
- `InternationalSales` - Global sales records
- `May2022` - Current product catalog
- `PL_March2021` - Historical product catalog
- `SaleReport` - Inventory status
- `CloudWarehouse` - Warehouse operations
- `ExpenseIIGF` - Business expenses

Select the tables you need and click **Load** or **Transform Data** to apply additional data modeling.

## Data Model Configuration

### Establishing Relationships

After loading tables, configure relationships in the **Model View**:

1. **AmazonSales ↔ May2022**
   - Relationship: `AmazonSales[SKU]` to `May2022[Sku]`
   - Cardinality: Many-to-One
   - Cross-filter direction: Single

2. **SaleReport ↔ May2022**
   - Relationship: `SaleReport[SKU_Code]` to `May2022[Sku]`
   - Cardinality: Many-to-One
   - Cross-filter direction: Single

3. **InternationalSales ↔ May2022**
   - Relationship: `InternationalSales[SKU]` to `May2022[Sku]`
   - Cardinality: Many-to-One
   - Cross-filter direction: Single

4. **PL_March2021 ↔ May2022**
   - Relationship: `PL_March2021[Sku]` to `May2022[Sku]`
   - Cardinality: One-to-One
   - Purpose: Historical price comparison

### Data Transformations

Consider these Power Query transformations:

1. **Date Formatting**
   - Convert text-based date columns to proper Date type
   - Create a separate Date dimension table for time intelligence

2. **Data Cleansing**
   - Remove any leading/trailing whitespace from key columns
   - Standardize text casing where appropriate
   - Handle null values according to business rules

## Visualization Examples

Based on the provided dashboard, here are key visualizations to create:

### 1. Sales Channel Distribution (Pie Chart)

**Purpose:** Compare revenue across Amazon vs Non-Amazon channels

- **Visual Type:** Pie Chart or Donut Chart
- **Legend:** `Sales_Channel_` from AmazonSales
- **Values:** Sum of `GROSS_AMT` or `Amount`
- **Format:** Show percentage labels

### 2. Top Designs by Stock (Bar Chart)

**Purpose:** Identify inventory concentration by design

- **Visual Type:** Horizontal Bar Chart
- **Axis:** `Design_No.` from SaleReport
- **Values:** Sum of `Stock`
- **Sort:** Descending by stock value
- **Top N Filter:** Show top 10 designs

### 3. Order Status Breakdown (Donut Chart)

**Purpose:** Monitor order fulfillment status

- **Visual Type:** Donut Chart
- **Legend:** `Status` from AmazonSales
- **Values:** Count of `Order_ID`
- **Format:** Show both count and percentage

### 4. Monthly Sales Trend (Area Chart)

**Purpose:** Track revenue patterns over time

- **Visual Type:** Area Chart
- **X-Axis:** `Month` (derived from Date)
- **Y-Axis:** Sum of `GROSS_AMT` or `Amount`
- **Format:** Continuous axis, smooth lines

### 5. Customer Analysis (Bar Chart)

**Purpose:** Identify top customers by revenue and volume

- **Visual Type:** Clustered Bar Chart
- **Axis:** `CUSTOMER` from InternationalSales
- **Values:** 
  - Sum of `GROSS_AMT`
  - Sum of `Qty` or `PCS`
- **Sort:** Descending by GROSS_AMT

### 6. Product Performance by Weight (Column Chart)

**Purpose:** Analyze pricing strategy across weight categories

- **Visual Type:** Column Chart
- **X-Axis:** `Weight` from May2022
- **Y-Axis:** Sum of `Amazon_MRP` or relevant MRP field
- **Format:** Show data labels

### Connection Issues

**Problem:** Unable to connect to localhost:1433

**Solutions:**
- Verify SQL Server is running
- Check TCP/IP is enabled in SQL Server Configuration Manager
- Confirm port 1433 is not blocked by firewall
- Test connection using SQL Server Management Studio first


