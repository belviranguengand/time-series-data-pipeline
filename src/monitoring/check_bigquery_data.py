from google.cloud import bigquery


PROJECT_ID = "time-series-data-pipeline"
DATASET_ID = "raw_ashrae"

# Volumes attendus pour le snapshot ASHRAE actuellement utilisé
EXPECTED_ROW_COUNTS = {
    "building_metadata": 1_449,
    "weather_train": 139_773,
    "train": 20_216_100,
}


def check_table(client, table_name, expected_rows):
    """Vérifie qu'une table BigQuery existe et possède le volume attendu."""

    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    print(f"[INFO] Vérification de {table_id}...")

    table = client.get_table(table_id)
    actual_rows = table.num_rows

    # Contrôle 1 : la table ne doit pas être vide
    if actual_rows == 0:
        raise ValueError(
            f"[ERREUR] La table {table_id} existe mais elle est vide."
        )

    # Contrôle 2 : le nombre de lignes doit correspondre au snapshot source
    if actual_rows != expected_rows:
        raise ValueError(
            f"[ERREUR] Volumétrie incorrecte pour {table_id}. "
            f"Attendu : {expected_rows:,} lignes | "
            f"Obtenu : {actual_rows:,} lignes."
        )

    print(
        f"[SUCCES] {table_id} : "
        f"{actual_rows:,} lignes / {expected_rows:,} attendues."
    )


def main():
    print("[INFO] Début des contrôles BigQuery.")

    client = bigquery.Client(project=PROJECT_ID)

    for table_name, expected_rows in EXPECTED_ROW_COUNTS.items():
        check_table(
            client=client,
            table_name=table_name,
            expected_rows=expected_rows,
        )

    print("[SUCCES] Tous les contrôles BigQuery sont validés.")


if __name__ == "__main__":
    main()