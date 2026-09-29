from google.cloud import bigquery


PROJECT_ID = "time-series-data-pipeline"
DATASET_ID = "raw_ashrae"

EXPECTED_TABLES = [
    "building_metadata",
    "weather_train",
    "train",
]


def check_table(client, table_name):
    """Vérifie qu'une table BigQuery existe et contient des données."""

    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    print(f"[INFO] Vérification de {table_id}...")

    table = client.get_table(table_id)

    if table.num_rows == 0:
        raise ValueError(
            f"[ERREUR] La table {table_id} existe mais elle est vide."
        )

    print(
        f"[SUCCES] {table_id} contient "
        f"{table.num_rows:,} lignes."
    )


def main():
    print("[INFO] Début des contrôles BigQuery.")

    client = bigquery.Client(project=PROJECT_ID)

    for table_name in EXPECTED_TABLES:
        check_table(client, table_name)

    print("[SUCCES] Tous les contrôles BigQuery sont validés.")


if __name__ == "__main__":
    main()