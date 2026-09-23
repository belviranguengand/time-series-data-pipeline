from pathlib import Path

from google.cloud import storage


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ID = "time-series-data-pipeline"
BUCKET_NAME = "time-series-data-pipeline-raw"

RAW_DATA_DIR = Path("data/raw")

SOURCE_FILES = {
    "building_metadata.csv": {
        "local_path": RAW_DATA_DIR / "building_metadata.csv",
        "gcs_path": "ashrae/raw/building_metadata.csv",
        "enabled": True,
    },
    "weather_train.csv": {
        "local_path": RAW_DATA_DIR / "weather_train.csv",
        "gcs_path": "ashrae/raw/weather_train.csv",
        "enabled": True,
    },
    "train.csv": {
        "local_path": RAW_DATA_DIR / "train.csv",
        "gcs_path": "ashrae/raw/train.csv",
        "enabled": True,
    },
}


# ============================================================
# CLOUD STORAGE
# ============================================================

def upload_file_to_gcs(
    bucket,
    local_file: Path,
    destination_blob_name: str,
) -> None:
    """
    Envoie un fichier local vers Google Cloud Storage.
    """

    print(f"\nUpload de {local_file.name}...")

    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(str(local_file))

    print(
        f"[OK] {local_file.name} envoyé vers "
        f"gs://{BUCKET_NAME}/{destination_blob_name}"
    )


# ============================================================
# PIPELINE D'INGESTION
# ============================================================

def ingest_sources() -> None:
    """
    Envoie les sources activées vers la zone RAW
    de Google Cloud Storage.
    """

    print("=" * 70)
    print("INGESTION ASHRAE VERS GOOGLE CLOUD STORAGE")
    print("=" * 70)

    # Création du client Google Cloud Storage
    client = storage.Client(project=PROJECT_ID)

    # Connexion au bucket
    bucket = client.bucket(BUCKET_NAME)

    # Parcours des fichiers sources
    for file_name, config in SOURCE_FILES.items():

        # Ignorer les fichiers désactivés
        if not config["enabled"]:
            print(f"[SKIP] {file_name}")
            continue

        local_file = config["local_path"]
        gcs_path = config["gcs_path"]

        # Vérifier que le fichier existe localement
        if not local_file.exists():
            raise FileNotFoundError(
                f"Source introuvable : {local_file}"
            )

        # Upload vers Google Cloud Storage
        upload_file_to_gcs(
            bucket=bucket,
            local_file=local_file,
            destination_blob_name=gcs_path,
        )

    print("\n[SUCCES] Ingestion terminée.")


# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":
    ingest_sources()