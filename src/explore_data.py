from pathlib import Path

import pandas as pd


# ============================================================
# CONFIGURATION DES CHEMINS
# ============================================================

# Dossier contenant les données brutes téléchargées depuis Kaggle
RAW_DATA_DIR = Path("data/raw")

# Fichiers principaux du projet
BUILDING_FILE = RAW_DATA_DIR / "building_metadata.csv"
WEATHER_FILE = RAW_DATA_DIR / "weather_train.csv"
TRAIN_FILE = RAW_DATA_DIR / "train.csv"


# ============================================================
# 1. INSPECTION RAPIDE DES DATASETS
# ============================================================

def inspect_dataset(file_path: Path, sample_size: int = 5) -> None:
    """Affiche les premières informations sur un fichier CSV."""

    print("\n" + "=" * 70)
    print(f"FICHIER : {file_path.name}")
    print("=" * 70)

    # Lecture d'un petit échantillon uniquement
    df = pd.read_csv(file_path, nrows=sample_size)

    print("\nColonnes :")
    print(df.columns.tolist())

    print("\nAperçu :")
    print(df.head())

    print("\nTypes détectés :")
    print(df.dtypes)


# ============================================================
# 2. VOLUMETRIE
# ============================================================

def count_csv_rows(file_path: Path) -> int:
    """Compte le nombre de lignes de données d'un fichier CSV."""

    with file_path.open("r", encoding="utf-8") as file:
        total_lines = sum(1 for _ in file)

    # On retire la ligne d'en-tête
    return total_lines - 1


# ============================================================
# 3. CARDINALITE
# ============================================================

def analyze_cardinality() -> None:
    """Compte les valeurs distinctes des dimensions principales."""

    buildings = pd.read_csv(BUILDING_FILE)

    print("\n" + "=" * 70)
    print("CARDINALITE")
    print("=" * 70)

    print(
        f"Nombre de sites : "
        f"{buildings['site_id'].nunique()}"
    )

    print(
        f"Nombre de bâtiments : "
        f"{buildings['building_id'].nunique()}"
    )

    print(
        f"Nombre d'usages de bâtiments : "
        f"{buildings['primary_use'].nunique()}"
    )


# ============================================================
# 4. TYPES DE COMPTEURS
# ============================================================

def analyze_meters() -> None:
    """Analyse les types de compteurs par lecture en chunks."""

    chunk_size = 500_000
    meter_values = set()

    # train.csv contient plus de 20 millions de lignes.
    # On ne lit que la colonne nécessaire et par blocs.
    for chunk in pd.read_csv(
        TRAIN_FILE,
        usecols=["meter"],
        chunksize=chunk_size
    ):
        meter_values.update(
            chunk["meter"].dropna().unique()
        )

    print("\n" + "=" * 70)
    print("COMPTEURS")
    print("=" * 70)

    print(
        f"Nombre de types de compteurs : "
        f"{len(meter_values)}"
    )

    print(
        f"Codes des compteurs : "
        f"{sorted(meter_values)}"
    )


# ============================================================
# 5. PERIODE TEMPORELLE
# ============================================================

def analyze_time_range() -> None:
    """Détermine la période couverte par les relevés énergétiques."""

    chunk_size = 500_000

    min_timestamp = None
    max_timestamp = None

    for chunk in pd.read_csv(
        TRAIN_FILE,
        usecols=["timestamp"],
        chunksize=chunk_size,
        parse_dates=["timestamp"]
    ):
        chunk_min = chunk["timestamp"].min()
        chunk_max = chunk["timestamp"].max()

        if min_timestamp is None or chunk_min < min_timestamp:
            min_timestamp = chunk_min

        if max_timestamp is None or chunk_max > max_timestamp:
            max_timestamp = chunk_max

    print("\n" + "=" * 70)
    print("PERIODE TEMPORELLE")
    print("=" * 70)

    print(f"Premier timestamp : {min_timestamp}")
    print(f"Dernier timestamp : {max_timestamp}")
    print(f"Durée couverte : {max_timestamp - min_timestamp}")


# ============================================================
# 6. DATA QUALITY - COMPLETUDE / VALEURS MANQUANTES
# ============================================================

def analyze_missing_values() -> None:
    """Compte les valeurs manquantes dans les trois datasets."""

    print("\n" + "=" * 70)
    print("DATA QUALITY - VALEURS MANQUANTES")
    print("=" * 70)

    # --------------------------------------------------------
    # Métadonnées bâtiments
    # --------------------------------------------------------

    buildings = pd.read_csv(BUILDING_FILE)

    print("\nbuilding_metadata.csv")
    print("-" * 40)
    print(buildings.isna().sum())

    # --------------------------------------------------------
    # Données météorologiques
    # --------------------------------------------------------

    weather = pd.read_csv(WEATHER_FILE)

    print("\nweather_train.csv")
    print("-" * 40)
    print(weather.isna().sum())

    # --------------------------------------------------------
    # Relevés énergétiques
    # --------------------------------------------------------

    missing_train = None
    chunk_size = 500_000

    for chunk in pd.read_csv(
        TRAIN_FILE,
        chunksize=chunk_size
    ):
        chunk_missing = chunk.isna().sum()

        if missing_train is None:
            missing_train = chunk_missing
        else:
            missing_train = missing_train.add(
                chunk_missing,
                fill_value=0
            )

    print("\ntrain.csv")
    print("-" * 40)
    print(missing_train)


# ============================================================
# 7. DATA QUALITY - UNICITE / DOUBLONS
# ============================================================

def analyze_duplicates() -> None:
    """Analyse les doublons dans les petits datasets."""

    print("\n" + "=" * 70)
    print("DATA QUALITY - DOUBLONS")
    print("=" * 70)

    # --------------------------------------------------------
    # Métadonnées bâtiments
    # --------------------------------------------------------

    buildings = pd.read_csv(BUILDING_FILE)

    building_full_duplicates = buildings.duplicated().sum()

    building_key_duplicates = buildings.duplicated(
        subset=["building_id"]
    ).sum()

    print("\nbuilding_metadata.csv")
    print("-" * 40)

    print(
        f"Doublons lignes complètes : "
        f"{building_full_duplicates}"
    )

    print(
        f"Doublons sur building_id : "
        f"{building_key_duplicates}"
    )

    # --------------------------------------------------------
    # Données météorologiques
    # --------------------------------------------------------

    weather = pd.read_csv(WEATHER_FILE)

    weather_full_duplicates = weather.duplicated().sum()

    weather_key_duplicates = weather.duplicated(
        subset=["site_id", "timestamp"]
    ).sum()

    print("\nweather_train.csv")
    print("-" * 40)

    print(
        f"Doublons lignes complètes : "
        f"{weather_full_duplicates}"
    )

    print(
        f"Doublons sur site_id + timestamp : "
        f"{weather_key_duplicates}"
    )


# ============================================================
# 8. DATA QUALITY - UNICITE DE TRAIN.CSV
# ============================================================

def analyze_train_duplicates() -> None:
    """
    Recherche les doublons de la clé métier dans train.csv.

    ATTENTION :
    Cette fonction est conservée pour l'instant mais n'est pas exécutée.
    Le contrôle global sera effectué plus tard dans BigQuery afin
    d'éviter de conserver des millions de clés Python en mémoire.
    """

    print("\n" + "=" * 70)
    print("DATA QUALITY - UNICITE DES RELEVES ENERGETIQUES")
    print("=" * 70)

    chunk_size = 500_000
    seen_keys = set()
    duplicate_count = 0

    for chunk in pd.read_csv(
        TRAIN_FILE,
        usecols=["building_id", "meter", "timestamp"],
        chunksize=chunk_size
    ):
        for row in chunk.itertuples(index=False):

            key = (
                row.building_id,
                row.meter,
                row.timestamp
            )

            if key in seen_keys:
                duplicate_count += 1
            else:
                seen_keys.add(key)

    print(
        "Clé métier testée : "
        "building_id + meter + timestamp"
    )

    print(
        f"Nombre de clés dupliquées : "
        f"{duplicate_count:,}"
    )


# ============================================================
# 9. DATA QUALITY - VALIDITE
# ============================================================

def analyze_validity() -> None:
    """Vérifie plusieurs règles de validité des données."""

    print("\n" + "=" * 70)
    print("DATA QUALITY - VALIDITE")
    print("=" * 70)

    # --------------------------------------------------------
    # Métadonnées bâtiments
    # --------------------------------------------------------

    buildings = pd.read_csv(BUILDING_FILE)

    print("\nbuilding_metadata.csv")
    print("-" * 40)

    print(
        "site_id négatifs :",
        (buildings["site_id"] < 0).sum()
    )

    print(
        "building_id négatifs :",
        (buildings["building_id"] < 0).sum()
    )

    print(
        "square_feet <= 0 :",
        (buildings["square_feet"] <= 0).sum()
    )

    print(
        "floor_count <= 0 :",
        (buildings["floor_count"] <= 0).sum()
    )

    # Pour year_built, on observe d'abord les données.
    # On définira une règle de validité ensuite.
    print(
        "year_built minimum :",
        buildings["year_built"].min()
    )

    print(
        "year_built maximum :",
        buildings["year_built"].max()
    )

    # --------------------------------------------------------
    # Relevés énergétiques
    # --------------------------------------------------------

    valid_meters = {0, 1, 2, 3}

    invalid_meter_count = 0
    negative_reading_count = 0
    negative_building_id_count = 0
    invalid_timestamp_count = 0

    chunk_size = 500_000

    for chunk in pd.read_csv(
        TRAIN_FILE,
        chunksize=chunk_size
    ):

        # Vérification des codes de compteur
        invalid_meter_count += (
            ~chunk["meter"].isin(valid_meters)
        ).sum()

        # Vérification des consommations négatives
        negative_reading_count += (
            chunk["meter_reading"] < 0
        ).sum()

        # Vérification des identifiants négatifs
        negative_building_id_count += (
            chunk["building_id"] < 0
        ).sum()

        # Vérification du format des timestamps
        parsed_timestamp = pd.to_datetime(
            chunk["timestamp"],
            errors="coerce"
        )

        invalid_timestamp_count += (
            parsed_timestamp.isna().sum()
        )

    print("\ntrain.csv")
    print("-" * 40)

    print(
        f"Codes meter invalides : "
        f"{invalid_meter_count:,}"
    )

    print(
        f"meter_reading négatifs : "
        f"{negative_reading_count:,}"
    )

    print(
        f"building_id négatifs : "
        f"{negative_building_id_count:,}"
    )

    print(
        f"timestamps invalides : "
        f"{invalid_timestamp_count:,}"
    )



# ============================================================
# 10. DATA QUALITY - INTEGRITE REFERENTIELLE
# ============================================================

def analyze_referential_integrity() -> None:
    """
    Vérifie que les identifiants utilisés dans les datasets
    existent bien dans leurs tables de référence.
    """

    print("\n" + "=" * 70)
    print("DATA QUALITY - INTEGRITE REFERENTIELLE")
    print("=" * 70)

    # --------------------------------------------------------
    # Chargement des tables de référence
    # --------------------------------------------------------

    buildings = pd.read_csv(
        BUILDING_FILE,
        usecols=["building_id", "site_id"]
    )

    weather = pd.read_csv(
        WEATHER_FILE,
        usecols=["site_id"]
    )

    # Ensemble des identifiants autorisés
    valid_building_ids = set(
        buildings["building_id"].unique()
    )

    valid_site_ids = set(
        weather["site_id"].unique()
    )

    # --------------------------------------------------------
    # 1. Vérification des building_id de train.csv
    # --------------------------------------------------------

    orphan_building_ids = set()
    chunk_size = 500_000

    for chunk in pd.read_csv(
        TRAIN_FILE,
        usecols=["building_id"],
        chunksize=chunk_size
    ):
        current_building_ids = set(
            chunk["building_id"].unique()
        )

        orphan_building_ids.update(
            current_building_ids - valid_building_ids
        )

    # --------------------------------------------------------
    # 2. Vérification des site_id
    # --------------------------------------------------------

    building_site_ids = set(
        buildings["site_id"].unique()
    )

    orphan_site_ids = (
        building_site_ids - valid_site_ids
    )

    # --------------------------------------------------------
    # Résultats
    # --------------------------------------------------------

    print("\ntrain.csv -> building_metadata.csv")
    print("-" * 40)

    print(
        f"building_id orphelins : "
        f"{len(orphan_building_ids)}"
    )

    if orphan_building_ids:
        print(
            f"Identifiants concernés : "
            f"{sorted(orphan_building_ids)}"
        )

    print("\nbuilding_metadata.csv -> weather_train.csv")
    print("-" * 40)

    print(
        f"site_id orphelins : "
        f"{len(orphan_site_ids)}"
    )

    if orphan_site_ids:
        print(
            f"Identifiants concernés : "
            f"{sorted(orphan_site_ids)}"
        )


# ============================================================
# 11. DATA QUALITY - QUALITE TEMPORELLE DE WEATHER_TRAIN
# ============================================================

def analyze_weather_time_gaps() -> None:
    """
    Vérifie si chaque site possède bien toutes les heures attendues
    dans weather_train.csv entre le premier et le dernier timestamp.
    """

    print("\n" + "=" * 70)
    print("DATA QUALITY - QUALITE TEMPORELLE")
    print("=" * 70)

    # --------------------------------------------------------
    # Chargement des données météo
    # --------------------------------------------------------

    weather = pd.read_csv(
        WEATHER_FILE,
        usecols=["site_id", "timestamp"],
        parse_dates=["timestamp"]
    )

    # --------------------------------------------------------
    # Détermination de la période temporelle globale
    # --------------------------------------------------------

    global_start = weather["timestamp"].min()
    global_end = weather["timestamp"].max()

    # Création de toutes les heures théoriquement attendues
    expected_timestamps = pd.date_range(
        start=global_start,
        end=global_end,
        freq="h"
    )

    expected_hour_count = len(expected_timestamps)

    print(f"\nPremier timestamp météo : {global_start}")
    print(f"Dernier timestamp météo : {global_end}")
    print(
        f"Nombre d'heures attendues par site : "
        f"{expected_hour_count:,}"
    )

    # --------------------------------------------------------
    # Recherche des gaps site par site
    # --------------------------------------------------------

    total_missing_hours = 0
    sites_with_gaps = 0

    print("\nGaps temporels par site")
    print("-" * 40)

    for site_id in sorted(weather["site_id"].unique()):

        site_timestamps = set(
            weather.loc[
                weather["site_id"] == site_id,
                "timestamp"
            ]
        )

        missing_timestamps = (
            set(expected_timestamps) - site_timestamps
        )

        missing_count = len(missing_timestamps)

        total_missing_hours += missing_count

        if missing_count > 0:
            sites_with_gaps += 1

        print(
            f"Site {site_id} : "
            f"{missing_count:,} heure(s) manquante(s)"
        )

    # --------------------------------------------------------
    # Résumé
    # --------------------------------------------------------

    print("\nRésumé")
    print("-" * 40)

    print(
        f"Nombre de sites avec au moins un gap : "
        f"{sites_with_gaps}"
    )

    print(
        f"Nombre total d'heures manquantes : "
        f"{total_missing_hours:,}"
    )


# ============================================================
# 12. DATA QUALITY - QUALITE TEMPORELLE DE TRAIN.CSV
# ============================================================

def analyze_train_time_gaps() -> None:
    """
    Analyse les gaps temporels dans train.csv pour chaque série
    définie par le couple (building_id, meter).

    La lecture se fait par chunks afin de ne pas charger les
    20+ millions de lignes en mémoire.

    Cette analyse suppose que les observations d'une même série
    apparaissent dans l'ordre chronologique dans le fichier.
    Le code contrôle également les éventuels retours en arrière.
    """

    print("\n" + "=" * 70)
    print("DATA QUALITY - QUALITE TEMPORELLE DE TRAIN.CSV")
    print("=" * 70)

    chunk_size = 500_000

    last_timestamp_by_series = {}
    missing_hours_by_series = {}

    duplicate_timestamp_count = 0
    out_of_order_count = 0
    total_rows_processed = 0

    for chunk in pd.read_csv(
        TRAIN_FILE,
        usecols=["building_id", "meter", "timestamp"],
        chunksize=chunk_size,
        parse_dates=["timestamp"]
    ):
        total_rows_processed += len(chunk)

        for (building_id, meter), group in chunk.groupby(
            ["building_id", "meter"],
            sort=False
        ):
            timestamps = group["timestamp"]

            series_key = (
                int(building_id),
                int(meter)
            )

            previous_timestamp = last_timestamp_by_series.get(
                series_key
            )

            first_timestamp = timestamps.iloc[0]

            if previous_timestamp is not None:
                delta = (
                    first_timestamp - previous_timestamp
                ).total_seconds() / 3600

                if delta == 0:
                    duplicate_timestamp_count += 1

                elif delta < 0:
                    out_of_order_count += 1

                elif delta > 1:
                    missing_hours = int(delta - 1)
                    missing_hours_by_series[series_key] = (
                        missing_hours_by_series.get(series_key, 0)
                        + missing_hours
                    )

            deltas = (
                timestamps
                .diff()
                .dt.total_seconds()
                .div(3600)
            )

            duplicate_timestamp_count += int(
                (deltas == 0).sum()
            )

            out_of_order_count += int(
                (deltas < 0).sum()
            )

            positive_gaps = deltas[
                deltas > 1
            ]

            if not positive_gaps.empty:
                missing_hours = int(
                    (positive_gaps - 1).sum()
                )

                missing_hours_by_series[series_key] = (
                    missing_hours_by_series.get(series_key, 0)
                    + missing_hours
                )

            last_timestamp_by_series[series_key] = (
                timestamps.iloc[-1]
            )

    total_series = len(last_timestamp_by_series)
    series_with_gaps = len(missing_hours_by_series)
    total_missing_hours = sum(
        missing_hours_by_series.values()
    )

    print(
        f"\nLignes analysées : "
        f"{total_rows_processed:,}"
    )

    print(
        f"Nombre de séries building_id + meter : "
        f"{total_series:,}"
    )

    print(
        f"Séries avec au moins un gap : "
        f"{series_with_gaps:,}"
    )

    print(
        f"Nombre total d'heures manquantes détectées : "
        f"{total_missing_hours:,}"
    )

    print(
        f"Timestamps dupliqués détectés pendant le parcours : "
        f"{duplicate_timestamp_count:,}"
    )

    print(
        f"Retours temporels détectés : "
        f"{out_of_order_count:,}"
    )

    if missing_hours_by_series:
        top_series = sorted(
            missing_hours_by_series.items(),
            key=lambda item: item[1],
            reverse=True
        )[:10]

        print(
            "\nTop 10 des séries avec le plus "
            "d'heures manquantes"
        )
        print("-" * 40)

        for (building_id, meter), missing_hours in top_series:
            print(
                f"building_id={building_id}, "
                f"meter={meter} : "
                f"{missing_hours:,} heure(s) manquante(s)"
            )

    print("\nInterprétation")
    print("-" * 40)

    if out_of_order_count == 0:
        print(
            "Aucun retour temporel détecté : "
            "l'ordre chronologique utilisé pour l'analyse est cohérent."
        )
    else:
        print(
            "ATTENTION : des retours temporels ont été détectés. "
            "Les résultats de gaps devront être confirmés dans BigQuery."
        )

# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # 1. Inspection
    # --------------------------------------------------------

    inspect_dataset(BUILDING_FILE)
    inspect_dataset(WEATHER_FILE)
    inspect_dataset(TRAIN_FILE)

    # --------------------------------------------------------
    # 2. Volumétrie
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("VOLUMETRIE")
    print("=" * 70)

    print(
        f"building_metadata.csv : "
        f"{count_csv_rows(BUILDING_FILE):,} lignes"
    )

    print(
        f"weather_train.csv : "
        f"{count_csv_rows(WEATHER_FILE):,} lignes"
    )

    print(
        f"train.csv : "
        f"{count_csv_rows(TRAIN_FILE):,} lignes"
    )

    # --------------------------------------------------------
    # 3. Cardinalité
    # --------------------------------------------------------

    analyze_cardinality()

    # --------------------------------------------------------
    # 4. Compteurs
    # --------------------------------------------------------

    analyze_meters()

    # --------------------------------------------------------
    # 5. Période temporelle
    # --------------------------------------------------------

    analyze_time_range()

    # --------------------------------------------------------
    # 6. Complétude
    # --------------------------------------------------------

    analyze_missing_values()

    # --------------------------------------------------------
    # 7. Unicité des petits datasets
    # --------------------------------------------------------

    analyze_duplicates()

    # --------------------------------------------------------
    # 8. Unicité de train.csv
    # --------------------------------------------------------

    # NE PAS EXECUTER POUR LE MOMENT.
    # Ce contrôle sera réalisé dans BigQuery.
    #
    # analyze_train_duplicates()

    # --------------------------------------------------------
    # 9. Validité
    # --------------------------------------------------------

    analyze_validity()

    # --------------------------------------------------------
    # 10. Intégrité référentielle
    # --------------------------------------------------------

    analyze_referential_integrity()

    # --------------------------------------------------------
    # 11. Qualité temporelle de weather_train.csv
    # --------------------------------------------------------

    analyze_weather_time_gaps()

    # --------------------------------------------------------
    # 12. Qualité temporelle de train.csv
    # --------------------------------------------------------

    analyze_train_time_gaps()

    