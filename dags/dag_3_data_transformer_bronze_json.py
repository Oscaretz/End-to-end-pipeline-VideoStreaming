from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy import DummyOperator
import sys
sys.path.append('/opt/airflow')

from scripts.json_loader import load_content_json
from config import get_mssql_config
from datetime import datetime

dag = DAG(
    'dag_3_json_content_loader',
    default_args={
        'owner': 'data_engineer',
        'start_date': datetime(2025, 5, 1),
        'retries': 1,
    },
    schedule_interval=None,
    catchup=False,
    description='Load content.json to bronze.content table'
)

# Start task
start_task = DummyOperator(
    task_id='start_json_loading',
    dag=dag
)

# Load JSON content
load_json_task = PythonOperator(
    task_id='load_content_json',
    python_callable=load_content_json,
    op_kwargs={
        **get_mssql_config(),
        "json_file_path": "/opt/airflow/data/portfolio/content.json"
    },
    dag=dag
)

# End task
end_task = DummyOperator(
    task_id='json_loading_complete',
    dag=dag
)

# Set dependencies
start_task >> load_json_task >> end_task