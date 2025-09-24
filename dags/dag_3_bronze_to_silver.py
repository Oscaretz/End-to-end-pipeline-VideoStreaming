from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from scripts.bronze_cleaning import (
    process_table,
    clean_amazon_sales,
    clean_cloud_warehouse,
    clean_expense_iigf,
    clean_international_sales,
    clean_may2022_pl,
    clean_sale_report
)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 9, 23),
    'retries': 1,
}

with DAG(
    'bronze_to_silver_dag',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:

    amazon_task = PythonOperator(
        task_id='amazon_sales_to_silver',
        python_callable=process_table,
        op_args=['Amazon_Sale_Report', clean_amazon_sales, 'AmazonSales']
    )

    cloud_task = PythonOperator(
        task_id='cloud_warehouse_to_silver',
        python_callable=process_table,
        op_args=['Cloud_Warehouse_Compersion_Chart', clean_cloud_warehouse, 'CloudWarehouse']
    )

    expense_task = PythonOperator(
        task_id='expense_iigf_to_silver',
        python_callable=process_table,
        op_args=['Expense_IIGF', clean_expense_iigf, 'ExpenseIIGF']
    )

    international_task = PythonOperator(
        task_id='international_sales_to_silver',
        python_callable=process_table,
        op_args=['International_Sale_Report', clean_international_sales, 'InternationalSales']
    )

    may2022_task = PythonOperator(
        task_id='may2022_pl_to_silver',
        python_callable=process_table,
        op_args=['P__L_March_2021', clean_may2022_pl, 'PL_March2021']
    )

    sale_report_task = PythonOperator(
        task_id='sale_report_to_silver',
        python_callable=process_table,
        op_args=['Sale_Report', clean_sale_report, 'SaleReport']
    )

    # Orden de ejecución
    amazon_task >> cloud_task >> expense_task >> international_task >> may2022_task >> sale_report_task
