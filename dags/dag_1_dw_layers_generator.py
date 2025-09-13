# Data warehouse bronze layer creation DAG.
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

from scripts.layerSchemasGenerator import generate_layer_schemas
from config import get_mssql_config

dag = DAG(
    'dag_1_dw_layers_generator',
    default_args={
        'owner': 'airflow',
        'start_date': '2025-05-01',
        'retries': 1,
    },
    schedule_interval=None,
    catchup=False
)

create_data_warehouse_task = PythonOperator(
    task_id='create_data_warehouse_task',
    python_callable=generate_layer_schemas,
    op_kwargs=get_mssql_config(),
    dag=dag
)

# Set the dependencies between the tasks.
create_data_warehouse_task