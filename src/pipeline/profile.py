from pipeline.extract.file import read_flight_data


FILE_PATH = "data/raw/flight_data_2024.csv"


def main():
    chunks = read_flight_data(FILE_PATH, chunksize=100_000)

    total_rows = 0
    cancelled = 0
    diverted = 0

    for chunk in chunks:
        total_rows += len(chunk)
        cancelled += chunk["cancelled"].sum()
        diverted += chunk["diverted"].sum()

    print(f"Total vuelos: {total_rows:,}")
    print(f"Cancelados: {cancelled:,}")
    print(f"Desviados: {diverted:,}")


if __name__ == "__main__":
    main()
