from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.bash import BashOperator


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
        retries=2,
        retry_delay=timedelta(minutes=2),
    )

    load_to_bigquery = BashOperator(
        task_id="load_to_bigquery",
        bash_command=(
            "cd /opt/airflow && "
            "python src/ingestion/load_to_bigquery.py"
        ),
        retries=2,
        retry_delay=timedelta(minutes=2),
    )

    check_bigquery_data = BashOperator(
        task_id="check_bigquery_data",
        bash_command=(
            "cd /opt/airflow && "
            "python src/monitoring/check_bigquery_data.py"
        ),
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            "cd /opt/airflow/dbt/energy_pipeline && "
            "dbt build"
        ),
        retries=1,
        retry_delay=timedelta(minutes=2),
    )

    end = EmptyOperator(
        task_id="end"
    )

    start >> validate_sources >> ingest_to_gcs >> load_to_bigquery >> check_bigquery_data >> dbt_build >> end