from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import broadcast, col, sum as spark_sum, to_date


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed" / "spark"

TRAIN_FILE = RAW_DATA_DIR / "train.csv"
BUILDING_METADATA_FILE = RAW_DATA_DIR / "building_metadata.csv"

OUTPUT_DIR = (
    PROCESSED_DATA_DIR
    / "daily_site_meter_consumption"
)


def create_spark_session() -> SparkSession:
    """Crée la session Spark utilisée par le job."""

    return (
        SparkSession.builder
        .appName("energy-consumption-aggregation")
        .master("local[*]")
        .getOrCreate()
    )


def main():
    print("[INFO] Démarrage du job PySpark.")

    spark = create_spark_session()

    try:
        # ---------------------------------------------------------
        # 1. Lecture des données
        # ---------------------------------------------------------
        print(f"[INFO] Lecture de : {TRAIN_FILE}")

        train_df = (
            spark.read
            .option("header", True)
            .option("inferSchema", True)
            .csv(str(TRAIN_FILE))
        )

        print(f"[INFO] Lecture de : {BUILDING_METADATA_FILE}")

        building_df = (
            spark.read
            .option("header", True)
            .option("inferSchema", True)
            .csv(str(BUILDING_METADATA_FILE))
        )

        # ---------------------------------------------------------
        # 2. Vérification des schémas
        # ---------------------------------------------------------
        print("\n[INFO] Schéma de train.csv :")
        train_df.printSchema()

        print("\n[INFO] Schéma de building_metadata.csv :")
        building_df.printSchema()

        # ---------------------------------------------------------
        # 3. Jointure avec les métadonnées bâtiments
        # ---------------------------------------------------------
        print(
            "\n[INFO] Jointure des consommations "
            "avec les métadonnées bâtiments."
        )

        energy_df = train_df.join(
            broadcast(
                building_df.select(
                    "building_id",
                    "site_id",
                    "primary_use",
                    "square_feet",
                )
            ),
            on="building_id",
            how="inner",
        )

        print("\n[INFO] Aperçu après jointure :")
        energy_df.show(5, truncate=False)

        # ---------------------------------------------------------
        # 4. Vérification du plan d'exécution Spark
        # ---------------------------------------------------------
        print("\n[INFO] Plan d'exécution de la jointure :")
        energy_df.explain()

        # ---------------------------------------------------------
        # 5. Création de la date
        # ---------------------------------------------------------
        print("\n[INFO] Création de la date à partir du timestamp.")

        energy_with_date_df = energy_df.withColumn(
            "date",
            to_date(col("timestamp")),
        )

        # ---------------------------------------------------------
        # 6. Agrégation quotidienne
        # ---------------------------------------------------------
        print(
            "[INFO] Calcul de la consommation quotidienne "
            "par site et par type de compteur."
        )

        daily_site_consumption_df = (
            energy_with_date_df
            .groupBy(
                "site_id",
                "meter",
                "date",
            )
            .agg(
                spark_sum("meter_reading").alias(
                    "total_meter_reading"
                )
            )
            .orderBy(
                "date",
                "site_id",
                "meter",
            )
        )

        # ---------------------------------------------------------
        # 7. Affichage du résultat
        # ---------------------------------------------------------
        print(
            "\n[INFO] Consommation quotidienne "
            "par site et type de compteur :"
        )

        daily_site_consumption_df.show(
            30,
            truncate=False,
        )

        # ---------------------------------------------------------
        # 8. Écriture du résultat au format Parquet
        # ---------------------------------------------------------
        print(
            f"\n[INFO] Écriture du résultat au format Parquet : "
            f"{OUTPUT_DIR}"
        )

        (
            daily_site_consumption_df
            .write
            .mode("overwrite")
            .parquet(str(OUTPUT_DIR))
        )

        print("[INFO] Dataset Parquet créé avec succès.")

        print(
            "[SUCCES] Traitement PySpark terminé : "
            "jointure, agrégation et écriture Parquet réalisées."
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()