-- ===============================
-- Amazon Sales → Gold
-- ===============================
IF OBJECT_ID('gold.AmazonSales', 'U') IS NOT NULL
    DROP TABLE gold.AmazonSales;

SELECT
    Date,
    SUM(Qty) AS Total_Units,
    SUM(Amount) AS Total_Sales
INTO gold.AmazonSales
FROM silver.AmazonSaleReportRow
GROUP BY Date;

-- ===============================
-- Cloud Warehouse → Gold
-- ===============================
IF OBJECT_ID('gold.CloudWarehouse', 'U') IS NOT NULL
    DROP TABLE gold.CloudWarehouse;

SELECT
    [Index],
    AVG(Price_INR) AS Avg_Price_INR,
    AVG(Price_Numeric) AS Avg_Price_Numeric
INTO gold.CloudWarehouse
FROM silver.CloudWarehouseRow
GROUP BY [Index];

-- ===============================
-- Expenses → Gold
-- ===============================
IF OBJECT_ID('gold.Expenses', 'U') IS NOT NULL
    DROP TABLE gold.Expenses;

SELECT
    Date,
    Expense_Type,
    SUM(Amount) AS Total_Expense
INTO gold.Expenses
FROM silver.ExpenseIIGFRow
GROUP BY Date, Expense_Type;

-- ===============================
-- International Sales → Gold
-- ===============================
IF OBJECT_ID('gold.InternationalSales', 'U') IS NOT NULL
    DROP TABLE gold.InternationalSales;

SELECT
    DATE,
    SUM(PCS) AS Total_Pieces,
    AVG(RATE) AS Avg_Rate,
    SUM(GROSS_AMT) AS Total_Gross
INTO gold.InternationalSales
FROM silver.InternationalSalesRow
GROUP BY DATE;

-- ===============================
-- Sale Report → Gold
-- ===============================
IF OBJECT_ID('gold.SaleReport', 'U') IS NOT NULL
    DROP TABLE gold.SaleReport;

SELECT
    SUM(Stock) AS Total_Stock
INTO gold.SaleReport
FROM silver.SaleReportRow;
