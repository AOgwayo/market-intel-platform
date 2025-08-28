from datetime import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator

default_args = {"owner": "airflow"}
with DAG(
    dag_id="ingest_intraday",
    start_date=datetime(2024,1,1),
    schedule_interval="*/5 * * * *",
    catchup=False,
    default_args=default_args,
    tags=["ingest"],
):
    start = EmptyOperator(task_id="start")
