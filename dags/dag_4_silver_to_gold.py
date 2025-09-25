from airflow import DAG
from airflow.providers.microsoft.mssql.operators.mssql import MsSqlOperator
from datetime import datetime
import os

# Define SQL file path (adjust as needed)
SQL_FILE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "sql", "silver_to_gold.sql"
)

# Load SQL from file
with open(SQL_FILE_PATH, "r") as f:
    SILVER_TO_GOLD_SQL = f.read()

with DAG(
    dag_id="silver_to_gold_dag",
    start_date=datetime(2023, 1, 1),
    schedule_interval="@daily",  # run daily
    catchup=False,
    default_args={"retries": 1},
    tags=["etl", "silver-to-gold", "mssql"]
) as dag:

    silver_to_gold = MsSqlOperator(
        task_id="transform_silver_to_gold",
        mssql_conn_id="'mssql+pyodbc://sa:Password_airflow10@mssql_db:1433/dbo?driver=ODBC+Driver+17+for+SQL+Server'",  # Airflow Connection ID
        sql=SILVER_TO_GOLD_SQL,
    )

    silver_to_gold
