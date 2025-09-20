from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy import DummyOperator
import sys
sys.path.append('/opt/airflow')

from scripts.sql_runner import run_sql_file
from config import get_mssql_config
from datetime import datetime

dag = DAG(
    'dag_4_silver_to_gold',
    default_args={
        'owner': 'data_engineer',
        'start_date': datetime(2025, 5, 1),
        'retries': 1,
    },
    schedule_interval=None,
    catchup=False,
    description='Silver to Gold transformation - Business Analytics'
)

# Start task
start_task = DummyOperator(
    task_id='start_gold_transformation',
    dag=dag
)

# Run SQL script for Silver → Gold analytics
silver_to_gold_task = PythonOperator(
    task_id='silver_to_gold_sql',
    python_callable=run_sql_file,
    op_kwargs={
        **get_mssql_config(),
        "filename": "/opt/airflow/sql/silver_to_gold.sql"
    },
    dag=dag
)

# End task
end_task = DummyOperator(
    task_id='gold_transformation_complete',
    dag=dag
)

# Set dependencies
start_task >> silver_to_gold_task >> end_task