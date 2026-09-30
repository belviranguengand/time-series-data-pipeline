from pathlib import Path

from pyspark.sql import SparkSession


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PARQUET_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "spark"
    / "daily_site_meter_consumption"
)


def main():
    print("[INFO] Démarrage de la vérification du Parquet.")

    spark = (
        SparkSession.builder
        .appName("verify-energy-parquet")
        .master("local[*]")
        .getOrCreate()
    )

    try:
        print(f"[INFO] Lecture de : {PARQUET_DIR}")

        df = spark.read.parquet(str(PARQUET_DIR))

        print("\n=== SCHEMA ===")
        df.printSchema()

        print("\n=== NOMBRE DE LIGNES ===")
        row_count = df.count()
        print(f"Nombre de lignes : {row_count}")

        print("\n=== APERCU DES DONNEES ===")
        (
            df.orderBy(
                "date",
                "site_id",
                "meter",
            )
            .show(10, truncate=False)
        )

        print(
            "\n[SUCCES] Le dataset Parquet est "
            "lisible et valide avec Spark."
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()