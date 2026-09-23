from pathlib import Path
import pandas as pd

RAW_DATA_DIR = Path("data/raw")

SOURCE_FILES = {
    "building_metadata.csv": {
        "path": RAW_DATA_DIR / "building_metadata.csv",
        "required_columns": [
            "site_id", "building_id", "primary_use",
            "square_feet", "year_built", "floor_count",
        ],
    },
    "weather_train.csv": {
        "path": RAW_DATA_DIR / "weather_train.csv",
        "required_columns": [
            "site_id", "timestamp", "air_temperature",
            "cloud_coverage", "dew_temperature",
            "precip_depth_1_hr", "sea_level_pressure",
            "wind_direction", "wind_speed",
        ],
    },
    "train.csv": {
        "path": RAW_DATA_DIR / "train.csv",
        "required_columns": [
            "building_id", "meter", "timestamp", "meter_reading",
        ],
    },
}


def validate_file_exists(file_name: str, file_path: Path) -> bool:
    if not file_path.exists():
        print(f"[ERREUR] {file_name} : fichier introuvable -> {file_path}")
        return False

    print(f"[OK] {file_name} : fichier trouvé")
    return True


def validate_file_not_empty(file_name: str, file_path: Path) -> bool:
    file_size = file_path.stat().st_size

    if file_size == 0:
        print(f"[ERREUR] {file_name} : fichier vide")
        return False

    size_mb = file_size / (1024 * 1024)
    print(f"[OK] {file_name} : taille = {size_mb:.2f} MB")
    return True


def validate_schema(
    file_name: str,
    file_path: Path,
    required_columns: list[str],
) -> bool:
    try:
        dataframe = pd.read_csv(file_path, nrows=0)
    except Exception as error:
        print(f"[ERREUR] {file_name} : impossible de lire le fichier")
        print(f"         Détail : {error}")
        return False

    actual_columns = dataframe.columns.tolist()

    missing_columns = [
        column
        for column in required_columns
        if column not in actual_columns
    ]

    if missing_columns:
        print(
            f"[ERREUR] {file_name} : colonnes manquantes -> "
            f"{missing_columns}"
        )
        return False

    print(
        f"[OK] {file_name} : schéma valide "
        f"({len(actual_columns)} colonnes)"
    )
    return True


def validate_source(file_name: str, file_config: dict) -> bool:
    file_path = file_config["path"]
    required_columns = file_config["required_columns"]

    print("\n" + "-" * 70)
    print(f"Validation de : {file_name}")
    print("-" * 70)

    if not validate_file_exists(file_name, file_path):
        return False

    if not validate_file_not_empty(file_name, file_path):
        return False

    if not validate_schema(file_name, file_path, required_columns):
        return False

    return True


def validate_all_sources() -> None:
    print("=" * 70)
    print("VALIDATION DES SOURCES ASHRAE")
    print("=" * 70)

    invalid_sources = []

    for file_name, file_config in SOURCE_FILES.items():
        is_valid = validate_source(file_name, file_config)

        if not is_valid:
            invalid_sources.append(file_name)

    print("\n" + "=" * 70)
    print("RESUME")
    print("=" * 70)

    if invalid_sources:
        print(
            f"[ECHEC] {len(invalid_sources)} source(s) invalide(s) : "
            f"{invalid_sources}"
        )
        raise RuntimeError(
            "Validation des sources échouée. "
            "Le pipeline ne peut pas continuer."
        )

    print(f"[SUCCES] Les {len(SOURCE_FILES)} sources sont valides.")
    print("Le pipeline peut passer à l'étape suivante.")


if __name__ == "__main__":
    validate_all_sources()
