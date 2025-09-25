-- Create Gold schema
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'gold')
BEGIN
    EXEC('CREATE SCHEMA gold');
END
/* SPLIT */

------------------------------
-- Amazon Sales
------------------------------
IF OBJECT_ID('gold.AmazonSalesSummary','U') IS NULL
BEGIN
    CREATE TABLE gold.AmazonSalesSummary (
        Date DATE,
        TotalQty INT,
        TotalAmount DECIMAL(18,2)
    );
END
/* SPLIT */

TRUNCATE TABLE gold.AmazonSalesSummary;
/* SPLIT */

INSERT INTO gold.AmazonSalesSummary (Date, TotalQty, TotalAmount)
SELECT 
    Date,
    SUM(Qty) AS TotalQty,
    SUM(Amount) AS TotalAmount
FROM silver.AmazonSales
GROUP BY Date;
/* SPLIT */

------------------------------
-- Cloud Warehouse
------------------------------
IF OBJECT_ID('gold.CloudWarehouseSummary','U') IS NULL
BEGIN
    CREATE TABLE gold.CloudWarehouseSummary (
        Operation NVARCHAR(MAX),
        TotalPriceINR DECIMAL(18,2),
        TotalPriceNumeric DECIMAL(18,2)
    );
END
/* SPLIT */

TRUNCATE TABLE gold.CloudWarehouseSummary;
/* SPLIT */

INSERT INTO gold.CloudWarehouseSummary (Operation, TotalPriceINR, TotalPriceNumeric)
SELECT
    Operation,
    SUM(Price_INR),
    SUM(Price_Numeric)
FROM silver.CloudWarehouse
GROUP BY Operation;
/* SPLIT */

------------------------------
-- Expenses IIGF
------------------------------
IF OBJECT_ID('gold.ExpenseSummary','U') IS NULL
BEGIN
    CREATE TABLE gold.ExpenseSummary (
        Date DATE,
        Expense_Type NVARCHAR(255),
        TotalAmount DECIMAL(18,2)
    );
END
/* SPLIT */

TRUNCATE TABLE gold.ExpenseSummary;
/* SPLIT */

INSERT INTO gold.ExpenseSummary (Date, Expense_Type, TotalAmount)
SELECT
    Date,
    Expense_Type,
    SUM(Amount)
FROM silver.ExpenseIIGF
GROUP BY Date, Expense_Type;
/* SPLIT */

------------------------------
-- International Sales
------------------------------
IF OBJECT_ID('gold.InternationalSalesSummary','U') IS NULL
BEGIN
    CREATE TABLE gold.InternationalSalesSummary (
        Date DATE,
        TotalPCS INT,
        TotalRate DECIMAL(18,2),
        TotalGrossAmt DECIMAL(18,2)
    );
END
/* SPLIT */

TRUNCATE TABLE gold.InternationalSalesSummary;
/* SPLIT */

INSERT INTO gold.InternationalSalesSummary (Date, TotalPCS, TotalRate, TotalGrossAmt)
SELECT
    DATE,
    SUM(PCS),
    SUM(RATE),
    SUM(GROSS_AMT)
FROM silver.InternationalSales
GROUP BY DATE;
/* SPLIT */

------------------------------
-- PL March 2021
------------------------------
IF OBJECT_ID('gold.PLMarch2021Summary','U') IS NULL
BEGIN
    SELECT * INTO gold.PLMarch2021Summary
    FROM silver.PL_March2021;
END
/* SPLIT */

TRUNCATE TABLE gold.PLMarch2021Summary;
/* SPLIT */

INSERT INTO gold.PLMarch2021Summary
SELECT * FROM silver.PL_March2021;
/* SPLIT */

------------------------------
-- May 2022
------------------------------
IF OBJECT_ID('gold.May2022Summary','U') IS NULL
BEGIN
    SELECT * INTO gold.May2022Summary
    FROM silver.May2022;
END
/* SPLIT */

TRUNCATE TABLE gold.May2022Summary;
/* SPLIT */

INSERT INTO gold.May2022Summary
SELECT * FROM silver.May2022;
/* SPLIT */

------------------------------
-- Sale Report
------------------------------
IF OBJECT_ID('gold.SaleReportSummary','U') IS NULL
BEGIN
    CREATE TABLE gold.SaleReportSummary (
        Stock INT
    );
END
/* SPLIT */

TRUNCATE TABLE gold.SaleReportSummary;
/* SPLIT */

INSERT INTO gold.SaleReportSummary (Stock)
SELECT SUM(Stock)
FROM silver.SaleReport;
/* SPLIT */
