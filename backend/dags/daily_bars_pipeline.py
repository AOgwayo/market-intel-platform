from datetime import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator

default_args = {"owner": "airflow"}
with DAG(
    dag_id="daily_bars_pipeline",
    start_date=datetime(2024,1,1),
    schedule_interval="@daily",
    catchup=False,
    default_args=default_args,
    tags=["market"],
):
    start = EmptyOperator(task_id="start")
