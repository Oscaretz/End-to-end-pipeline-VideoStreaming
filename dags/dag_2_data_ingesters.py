# Data warehouse bronze layer creation DAG.
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import sys
sys.path.append('/opt/airflow')
from scripts.dataIngestor import ingest_json_to_mongo, ingest_csv_to_mssql
from scripts.layerSchemasGenerator import generate_layer_schemas
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

# Tarea para crear esquemas PRIMERO
create_schemas_task = PythonOperator(
    task_id='create_schemas_task',
    python_callable=generate_layer_schemas,
    op_kwargs=get_mssql_config(),
    dag=dag
)

ingest_to_mongo_task = PythonOperator(
    task_id='ingest_to_mongo_task',
    python_callable=ingest_json_to_mongo,
    op_kwargs={
        **get_mongo_config(),
        "filename": "content.json"  
    },
    dag=dag
)

ingest_to_mssql_task_1 = PythonOperator(
    task_id='ingest_to_mssql_task_1',
    python_callable=ingest_csv_to_mssql,
    op_kwargs={
        **get_mssql_config(),
        "filename": "users.csv"       
    },
    dag=dag
)

ingest_to_mssql_task_2 = PythonOperator(
    task_id='ingest_to_mssql_task_2',
    python_callable=ingest_csv_to_mssql,
    op_kwargs={
        **get_mssql_config(),
        "filename": "viewing_sessions.csv"       
    },
    dag=dag
)

create_schemas_task >> [ingest_to_mongo_task, ingest_to_mssql_task_1, ingest_to_mssql_task_2]
ingest_to_mongo_task >> ingest_to_mssql_task_1 >> ingest_to_mssql_task_2