from datetime import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator


with DAG(
    dag_id="energy_pipeline",
    description="Pipeline de monitoring de consommation énergétique ASHRAE",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["data-engineering", "energy", "gcp", "dbt"],
) as dag:

    start = EmptyOperator(
        task_id="start"
    )

    validate_sources = BashOperator(
        task_id="validate_sources",
        bash_command=(
            "cd /opt/airflow && "
            "python src/ingestion/validate_sources.py"
        ),
    )

    ingest_to_gcs = BashOperator(
        task_id="ingest_to_gcs",
        bash_command=(
            "cd /opt/airflow && "
            "python src/ingestion/ingest_data.py"
        ),
    )

    end = EmptyOperator(
        task_id="end"
    )

    start >> validate_sources >> ingest_to_gcs >> end