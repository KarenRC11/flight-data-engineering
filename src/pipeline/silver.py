from pathlib import Path

import pandas as pd

from pipeline.transform.quality import validate_flights
from pipeline.transform.transforms import transform_flights


BRONZE_PATH = Path("data/bronze/flights")
SILVER_PATH = Path("data/silver/flights")


def process_bronze_to_silver():

    SILVER_PATH.mkdir(parents=True, exist_ok=True)

    parquet_files = sorted(BRONZE_PATH.glob("*.parquet"))

    total_rows = 0
    failed_files = 0

    print(f"Archivos Bronze encontrados: {len(parquet_files)}")

    for file in parquet_files:

        print(f"\nProcesando: {file.name}")

        df = pd.read_parquet(file)

        # -----------------------------
        # Transformaciones
        # -----------------------------

        df = transform_flights(df)

        # -----------------------------
        # Data Quality
        # -----------------------------

        quality_results = validate_flights(df)

        quality_passed = all(quality_results.values())

        if not quality_passed:
            failed_files += 1

            print("❌ Data Quality FAILED")

            for rule, result in quality_results.items():
                print(f"   {rule}: {result}")

            continue

        print("✅ Data Quality PASSED")

        # -----------------------------
        # Guardar Silver
        # -----------------------------

        output_file = SILVER_PATH / file.name

        df.to_parquet(
            output_file,
            engine="pyarrow",
            index=False,
        )

        total_rows += len(df)

    print("\n================================")
    print("SILVER COMPLETADO")
    print("================================")
    print(f"Registros procesados: {total_rows:,}")
    print(f"Archivos con errores: {failed_files}")


if __name__ == "__main__":
    process_bronze_to_silver()
