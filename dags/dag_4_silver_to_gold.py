from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pyodbc
from config import get_mssql_config

def run_silver_to_gold():
    cfg = get_mssql_config()
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={cfg['server']},{cfg.get('port',1433)};"
        f"DATABASE={cfg['database']};"
        f"UID={cfg['username']};PWD={cfg['password']};"
        "TrustServerCertificate=Yes"
    )
    cursor = conn.cursor()

    # Read SQL script
    with open("/opt/airflow/sql/silver_to_gold.sql", "r") as f:
        sql_script = f.read()

    # Split by custom delimiter
    for stmt in sql_script.split("/* SPLIT */"):
        stmt = stmt.strip()
        if stmt:
            try:
                cursor.execute(stmt)
            except Exception as e:
                print(f"Failed SQL:\n{stmt[:200]}...\nError: {e}")
                raise

    conn.commit()
    cursor.close()
    conn.close()


default_args = {
    "owner": "airflow",
    "start_date": datetime(2025, 1, 1),
    "retries": 1
}

with DAG(
    "silver_to_gold",
    schedule_interval="0 2 * * *",
    default_args=default_args,
    catchup=False,
    tags=["gold"]
) as dag:

    run_task = PythonOperator(
        task_id="run_silver_to_gold",
        python_callable=run_silver_to_gold
    )
