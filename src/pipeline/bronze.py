from pipeline.extract.file import read_flight_data
from pipeline.load.local import save_bronze


FILE_PATH = "data/raw/flight_data_2024.csv"
BRONZE_PATH = "data/bronze/flights"


def main():

    print("Iniciando proceso Bronze...")

    chunks = read_flight_data(
        FILE_PATH,
        chunksize=100_000,
    )

    total_rows = save_bronze(
        chunks,
        BRONZE_PATH,
    )

    print(
        f"\nProceso Bronze terminado: "
        f"{total_rows:,} registros"
    )


if __name__ == "__main__":
    main()
