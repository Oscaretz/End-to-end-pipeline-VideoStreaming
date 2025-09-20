from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy import DummyOperator
import sys
sys.path.append('/opt/airflow')

from scripts.sql_runner import run_sql_file
from config import get_mssql_config
from datetime import datetime

dag = DAG(
    'dag_3_data_transformer_bronze',
    default_args={
        'owner': 'data_engineer',
        'start_date': datetime(2025, 5, 1),
        'retries': 1,
    },
    schedule_interval=None,
    catchup=False,
    description='Bronze to Silver transformation with SQL'
)

# Start task
start_task = DummyOperator(
    task_id='start_bronze_transformation',
    dag=dag
)

# Run SQL script for Bronze → Silver cleaning
bronze_to_silver_task = PythonOperator(
    task_id='bronze_to_silver_sql',
    python_callable=run_sql_file,
    op_kwargs={
        **get_mssql_config(),
        "filename": "/opt/airflow/sql/bronze_to_silver.sql"
    },
    dag=dag
)

# End task
end_task = DummyOperator(
    task_id='bronze_transformation_complete',
    dag=dag
)

# Set dependencies
start_task >> bronze_to_silver_task >> end_task
