from pathlib import Path

from google.api_core.retry import Retry
from google.cloud import storage


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ID = "time-series-data-pipeline"
BUCKET_NAME = "time-series-data-pipeline-raw"

RAW_DATA_DIR = Path("data/raw")

UPLOAD_TIMEOUT = 600

UPLOAD_RETRY = Retry(
    initial=2.0,
    maximum=30.0,
    multiplier=2.0,
    deadline=900.0,
)

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
    Envoie un fichier vers Google Cloud Storage.

    Si un objet de même taille existe déjà dans GCS,
    l'upload est ignoré afin de rendre l'ingestion idempotente.
    """

    local_size = local_file.stat().st_size
    file_size_mb = local_size / (1024 * 1024)

    blob = bucket.blob(destination_blob_name)

    # --------------------------------------------------------
    # Vérifier si le fichier existe déjà dans GCS
    # --------------------------------------------------------

    if blob.exists():
        blob.reload()

        remote_size = blob.size

        if remote_size == local_size:
            print(
                f"[SKIP] {local_file.name} existe déjà dans GCS "
                f"avec la même taille ({file_size_mb:.2f} MB).",
                flush=True,
            )
            return

        print(
            f"[INFO] {local_file.name} existe dans GCS "
            "mais sa taille est différente. Nouvel upload.",
            flush=True,
        )

    # --------------------------------------------------------
    # Upload
    # --------------------------------------------------------

    print(
        f"\nUpload de {local_file.name} "
        f"({file_size_mb:.2f} MB)...",
        flush=True,
    )

    blob.upload_from_filename(
        filename=str(local_file),
        timeout=UPLOAD_TIMEOUT,
        retry=UPLOAD_RETRY,
    )

    # --------------------------------------------------------
    # Vérification après upload
    # --------------------------------------------------------

    blob.reload()

    if blob.size != local_size:
        raise RuntimeError(
            f"Taille incorrecte après upload de {local_file.name}. "
            f"Local={local_size}, GCS={blob.size}"
        )

    print(
        f"[OK] {local_file.name} envoyé vers "
        f"gs://{BUCKET_NAME}/{destination_blob_name}",
        flush=True,
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

    client = storage.Client(project=PROJECT_ID)

    bucket = client.bucket(BUCKET_NAME)

    if not bucket.exists():
        raise RuntimeError(
            f"Bucket GCS inaccessible ou inexistant : {BUCKET_NAME}"
        )

    for file_name, config in SOURCE_FILES.items():

        if not config["enabled"]:
            print(f"[SKIP] {file_name}")
            continue

        local_file = config["local_path"]
        gcs_path = config["gcs_path"]

        if not local_file.exists():
            raise FileNotFoundError(
                f"Source introuvable : {local_file}"
            )

        if local_file.stat().st_size == 0:
            raise ValueError(
                f"Source vide : {local_file}"
            )

        upload_file_to_gcs(
            bucket=bucket,
            local_file=local_file,
            destination_blob_name=gcs_path,
        )

    print("\n[SUCCES] Ingestion terminée.", flush=True)


# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":
    ingest_sources()