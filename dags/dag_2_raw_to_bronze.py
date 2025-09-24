from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import sys
sys.path.append('/opt/airflow')  # Para que encuentre scripts/

from scripts.ingest_csvs_to_mssql import ingest_all_csvs

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 5, 1),
    'retries': 1,
}

dag = DAG(
    'dag_bronze_ingest_all_csvs',
    default_args=default_args,
    schedule_interval=None,
    catchup=False
)

ingest_task = PythonOperator(
    task_id='ingest_all_csvs_task',
    python_callable=ingest_all_csvs,
    dag=dag
)
