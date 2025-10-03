# streamlit_app_comparative.py
import streamlit as st
import pandas as pd
import sqlite3
import time
import psutil
import plotly.express as px
import numpy as np

# -------- FUNCIONES --------
def get_memory_usage():
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)  # MB

def generate_data(n_rows):
    """Genera datos de ejemplo para benchmark con fechas simuladas"""
    dates = pd.date_range("2023-01-01", periods=90)  # 3 meses de ventas
    data = {
        "order_id": range(1, n_rows + 1),
        "product": ["Item" + str(i % 100) for i in range(1, n_rows + 1)],
        "price": [i % 50 + 10 for i in range(1, n_rows + 1)],
        "quantity": [i % 5 + 1 for i in range(1, n_rows + 1)],
        "date": np.random.choice(dates, size=n_rows)  # fechas aleatorias
    }
    df = pd.DataFrame(data)
    # Ensure date column is datetime
    df["date"] = pd.to_datetime(df["date"])
    return df

def benchmark_sql(df):
    conn = sqlite3.connect(":memory:")
    df.to_sql("orders", conn, if_exists="replace", index=False)
    cursor = conn.cursor()

    start = time.time()
    mem_before = get_memory_usage()

    cursor.execute("""
    SELECT product, SUM(price * quantity) as revenue
    FROM orders
    GROUP BY product
    ORDER BY revenue DESC
    LIMIT 5
    """)
    result = cursor.fetchall()

    mem_after = get_memory_usage()
    end = time.time()
    conn.close()
    return result, end-start, mem_after-mem_before

def benchmark_nosql(df):
    """Simula JSON/NoSQL con pandas"""
    start = time.time()
    mem_before = get_memory_usage()

    top_products = (df.groupby("product")
                      .apply(lambda x: (x["price"]*x["quantity"]).sum())
                      .sort_values(ascending=False)
                      .head(5))

    mem_after = get_memory_usage()
    end = time.time()
    return top_products, end-start, mem_after-mem_before

# -------- BENCHMARK SQL: Sales Trend --------
def benchmark_sql_trend(df):
    conn = sqlite3.connect(":memory:")
    df.to_sql("orders", conn, if_exists="replace", index=False)
    cursor = conn.cursor()

    start = time.time()
    mem_before = get_memory_usage()

    cursor.execute("""
    SELECT date, SUM(price * quantity) as revenue
    FROM orders
    GROUP BY date
    ORDER BY date
    """)
    result = cursor.fetchall()

    mem_after = get_memory_usage()
    end = time.time()
    conn.close()

    # result: list of (date_str or date, revenue)
    trend_df = pd.DataFrame(result, columns=["date", "revenue"])
    # Ensure date is datetime
    trend_df["date"] = pd.to_datetime(trend_df["date"])
    return trend_df, end-start, mem_after-mem_before

# -------- BENCHMARK NoSQL: Sales Trend --------
def benchmark_nosql_trend(df):
    start = time.time()
    mem_before = get_memory_usage()

    sales_trend = (df.groupby("date")
                     .apply(lambda x: (x["price"]*x["quantity"]).sum())
                     .reset_index())
    sales_trend.columns = ["date","revenue"]
    sales_trend["date"] = pd.to_datetime(sales_trend["date"])

    mem_after = get_memory_usage()
    end = time.time()

    return sales_trend.sort_values("date").reset_index(drop=True), end-start, mem_after-mem_before

# -------- STREAMLIT UI --------
st.set_page_config(layout="wide")
st.title("CSV vs JSON: Relational vs Non-Relational Benchmark")
st.markdown("""
This app demonstrates **when relational databases are better** and when **non-relational is better**.
- Relational (CSV → SQLite): better for **structured data, joins, complex queries**
- Non-relational (JSON → NoSQL/pandas): better for **flexible or nested data, rapid ingestion**
""")

n_rows = st.slider("Number of rows in dataset [5]", 1000, 200000, 10000, step=1000)
df = generate_data(n_rows)
st.write("Sample Data [5]", df.head())

st.subheader("Code: How Data is Generated")
st.code("""
categories = ["Electronics", "Clothing", "Home", "Books"]
base_date = datetime.date(2025, 1, 1)
data = {
    "order_id": range(1, n_rows + 1),
    "product": ["Item" + str(i % 100) for i in range(1, n_rows + 1)],
    "category": random.choice(categories),
    "price": [i % 50 + 10 for i in range(1, n_rows + 1)],
    "quantity": [i % 5 + 1 for i in range(1, n_rows + 1)],
    "date": [base_date + timedelta(days=i % 90) for i in range(n_rows)]
}
df = pd.DataFrame(data)
""", language="python")

# -------- BENCHMARK RELACIONAL (Top products) --------
st.subheader("Relational DB (CSV → SQLite) — Top products")
sql_result, sql_time, sql_mem = benchmark_sql(df)
st.write("Top products (SQL):", sql_result)
st.write(f"Time: {sql_time:.4f} s | Memory: {sql_mem:.2f} MB")

# -------- BENCHMARK NO RELACIONAL (Top products) --------
st.subheader("Non-Relational DB (JSON → pandas simulation) — Top products")
nosql_result, nosql_time, nosql_mem = benchmark_nosql(df)
st.write("Top products (NoSQL simulated):")
st.write(nosql_result)
st.write(f"Time: {nosql_time:.4f} s | Memory: {nosql_mem:.2f} MB")

# -------- COMPARATIVA GRÁFICA (Top Products) --------
st.subheader("Performance Comparison: Top Products")
performance = pd.DataFrame({
    "Database": ["Relational (SQLite)", "Non-Relational (pandas JSON)"],
    "Time (s)": [sql_time, nosql_time],
    "Memory (MB)": [sql_mem, nosql_mem]
})
col1, col2 = st.columns(2)
with col1:
    fig_time = px.bar(performance, x="Database", y="Time (s)", color="Database",
                      title="Query Execution Time (Top Products)")
    st.plotly_chart(fig_time, use_container_width=True)
with col2:
    fig_mem = px.bar(performance, x="Database", y="Memory (MB)", color="Database",
                     title="Memory Usage (Top Products)")
    st.plotly_chart(fig_mem, use_container_width=True)

# -------- EVOLUCIÓN TEMPORAL DE VENTAS --------
st.subheader("Sales Trend Analysis (SQL vs NoSQL)")

sql_trend, sql_trend_time, sql_trend_mem = benchmark_sql_trend(df)
nosql_trend, nosql_trend_time, nosql_trend_mem = benchmark_nosql_trend(df)

# Plots de tendencia (lado a lado)
col3, col4 = st.columns(2)
with col3:
    fig_sql_trend = px.line(sql_trend, x="date", y="revenue",
                            title="Sales Trend Over Time (SQL)", markers=True)
    st.plotly_chart(fig_sql_trend, use_container_width=True)
with col4:
    fig_nosql_trend = px.line(nosql_trend, x="date", y="revenue",
                              title="Sales Trend Over Time (NoSQL/pandas)", markers=True)
    st.plotly_chart(fig_nosql_trend, use_container_width=True)

    # SQL Query para evolución temporal
sql_trend_query = """
SELECT 
    date,
    SUM(price * quantity) AS revenue
FROM sales
GROUP BY date
ORDER BY date;
"""

st.markdown("**SQL Query:**")
st.code(sql_trend_query, language="sql")

# NoSQL "query" equivalente (MongoDB estilo)
nosql_trend_query = """
sales_trend = (df.groupby("date")
    .apply(lambda x: (x["price"]*x["quantity"]).sum())
    .reset_index())
sales_trend.columns = ["date","revenue"]
sales_trend["date"] = pd.to_datetime(sales_trend["date"])
"""
st.markdown("**NoSQL Aggregation:**")
st.code(nosql_trend_query, language="javascript")

# -------- GRAFICAS DE CONSUMO DE CÓMPUTO (Trend) --------
st.subheader("Compute Consumption: Sales Trend Query")
trend_perf = pd.DataFrame({
    "Database": ["Relational (SQLite)", "Non-Relational (pandas JSON)"],
    "Time (s)": [sql_trend_time, nosql_trend_time],
    "Memory (MB)": [sql_trend_mem, nosql_trend_mem]
})
tcol1, tcol2 = st.columns(2)
with tcol1:
    fig_trend_time = px.bar(trend_perf, x="Database", y="Time (s)",
                            color="Database", title="Trend Query Execution Time")
    st.plotly_chart(fig_trend_time, use_container_width=True)
with tcol2:
    fig_trend_mem = px.bar(trend_perf, x="Database", y="Memory (MB)",
                           color="Database", title="Trend Query Memory Usage")
    st.plotly_chart(fig_trend_mem, use_container_width=True)

# -------- CUANDO USAR CADA MODELO (INSIGHTS) --------
st.subheader("Insights & Notes")
st.markdown("""
- **Relational DB (CSV → SQLite)**: best for structured, tabular data with complex aggregations or joins.  
- **Non-Relational (JSON/pandas)**: best for flexible, semi-structured data or when schema changes often.  

**Important note about the benchmark:**  
- SQLite is running *in-memory* here (demo), so timings and memory may be optimistic vs a production RDBMS (Postgres/MySQL). The relative behavior on **query types** (aggregations by key, time-series grouping, top-N per group) is still illustrative.
""")
