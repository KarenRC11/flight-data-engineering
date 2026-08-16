from pathlib import Path

import pandas as pd

from pipeline.transform.quality import validate_flights
from pipeline.transform.transforms import transform_flights


BRONZE_PATH = Path("data/bronze/flights")
SILVER_PATH = Path("data/silver/flights")


def process_bronze_to_silver():

    SILVER_PATH.mkdir(parents=True, exist_ok=True)

    parquet_files = sorted(
        BRONZE_PATH.glob("event_date=*/**/*.parquet")
    )

    total_rows = 0
    failed_files = 0

    print(
        f"Archivos Bronze encontrados: "
        f"{len(parquet_files)}"
    )

    for file in parquet_files:

        print(f"\nProcesando: {file}")

        df = pd.read_parquet(file)

        # -----------------------------
        # Transformaciones
        # -----------------------------

        df = transform_flights(df)

        # -----------------------------
        # Data Quality
        # -----------------------------

        quality_results = validate_flights(df)

        quality_passed = all(
            quality_results.values()
        )

        if not quality_passed:

            failed_files += 1

            print("❌ Data Quality FAILED")

            for rule, result in quality_results.items():
                print(f"   {rule}: {result}")

            continue

        print("✅ Data Quality PASSED")

        # -----------------------------
        # Mantener partición event_date
        # -----------------------------

        event_date_partition = file.parent.name

        output_dir = (
            SILVER_PATH
            / event_date_partition
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = (
            output_dir
            / file.name
        )

        df.to_parquet(
            output_file,
            engine="pyarrow",
            index=False,
        )

        total_rows += len(df)

    print("\n================================")
    print("SILVER COMPLETADO")
    print("================================")
    print(
        f"Registros procesados: "
        f"{total_rows:,}"
    )
    print(
        f"Archivos con errores: "
        f"{failed_files}"
    )


if __name__ == "__main__":
    process_bronze_to_silver()
