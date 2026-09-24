from google.cloud import bigquery


# Configuration GCP
PROJECT_ID = "time-series-data-pipeline"
DATASET_ID = "raw_ashrae"
BUCKET_NAME = "time-series-data-pipeline-raw"
LOCATION = "europe-west9"


# Client BigQuery
client = bigquery.Client(project=PROJECT_ID)


# Schéma : building_metadata.csv
BUILDING_METADATA_SCHEMA = [
    bigquery.SchemaField("site_id", "INTEGER"),
    bigquery.SchemaField("building_id", "INTEGER"),
    bigquery.SchemaField("primary_use", "STRING"),
    bigquery.SchemaField("square_feet", "INTEGER"),
    bigquery.SchemaField("year_built", "INTEGER"),
    bigquery.SchemaField("floor_count", "INTEGER"),
]


# Schéma : weather_train.csv
WEATHER_SCHEMA = [
    bigquery.SchemaField("site_id", "INTEGER"),
    bigquery.SchemaField("timestamp", "TIMESTAMP"),
    bigquery.SchemaField("air_temperature", "FLOAT"),
    bigquery.SchemaField("cloud_coverage", "FLOAT"),
    bigquery.SchemaField("dew_temperature", "FLOAT"),
    bigquery.SchemaField("precip_depth_1_hr", "FLOAT"),
    bigquery.SchemaField("sea_level_pressure", "FLOAT"),
    bigquery.SchemaField("wind_direction", "FLOAT"),
    bigquery.SchemaField("wind_speed", "FLOAT"),
]


# Schéma : train.csv
TRAIN_SCHEMA = [
    bigquery.SchemaField("building_id", "INTEGER"),
    bigquery.SchemaField("meter", "INTEGER"),
    bigquery.SchemaField("timestamp", "TIMESTAMP"),
    bigquery.SchemaField("meter_reading", "FLOAT"),
]


def load_csv_from_gcs(
    source_blob,
    table_name,
    schema,
    partition_field=None,
):
    """Charge un fichier CSV depuis GCS vers une table BigQuery."""

    gcs_uri = f"gs://{BUCKET_NAME}/{source_blob}"
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        schema=schema,
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    if partition_field:
        job_config.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field=partition_field,
        )

    print(f"[INFO] Chargement de {gcs_uri} vers {table_id}...")

    load_job = client.load_table_from_uri(
        gcs_uri,
        table_id,
        job_config=job_config,
        location=LOCATION,
    )

    # Attendre la fin du job BigQuery
    load_job.result()

    # Vérifier la table après chargement
    table = client.get_table(table_id)

    print(
        f"[SUCCES] {table_id} chargé : "
        f"{table.num_rows:,} lignes."
    )


def main():
    print("[INFO] Début du chargement GCS vers BigQuery.")

    load_csv_from_gcs(
        source_blob="ashrae/raw/building_metadata.csv",
        table_name="building_metadata",
        schema=BUILDING_METADATA_SCHEMA,
    )

    load_csv_from_gcs(
        source_blob="ashrae/raw/weather_train.csv",
        table_name="weather_train",
        schema=WEATHER_SCHEMA,
        partition_field="timestamp",
    )

    load_csv_from_gcs(
        source_blob="ashrae/raw/train.csv",
        table_name="train",
        schema=TRAIN_SCHEMA,
        partition_field="timestamp",
    )

    print("[SUCCES] Chargement GCS vers BigQuery terminé.")


if __name__ == "__main__":
    main()