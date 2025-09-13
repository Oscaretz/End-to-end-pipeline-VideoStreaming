# Data warehouse bronze layer creation DAG.
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from scripts.dataIngestor import ingest_json_to_mongo, ingest_csv_to_mssql
from config import get_mongo_config, get_mssql_config

dag = DAG(
    'dag_2_data_ingesters',
    default_args={
        'owner': 'airflow',
        'start_date': '2025-05-01',
        'retries': 1,
    },
    schedule_interval=None,
    catchup=False
)

ingest_to_mongo_task = PythonOperator(
    task_id='ingest_to_mongo_task',
    python_callable=ingest_json_to_mongo,
    op_kwargs=get_mongo_config(),
    dag=dag
)

ingest_to_mssql_task = PythonOperator(
    task_id='ingest_to_mssql_task',
    python_callable=ingest_csv_to_mssql,
    op_kwargs=get_mssql_config(),
    dag=dag
)

# Set the dependencies between the tasks.
create_data_warehouse_task