from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]

SILVER_DIR = PROJECT_ROOT / "data" / "silver"
OUTPUT_DIR = SILVER_DIR / "flights_enriched"

FLIGHTS_DIR = SILVER_DIR / "flights"
AIRPORTS_PATH = SILVER_DIR / "airports" / "airports.parquet"
AIRLINES_PATH = SILVER_DIR / "airlines" / "airlines.parquet"


CHUNK_SIZE = 100_000


def load_catalogs():
    """Carga los catálogos necesarios para enriquecer los vuelos."""

    airports = pd.read_parquet(
        AIRPORTS_PATH,
        columns=[
            "iata",
            "name",
            "city",
            "country",
        ],
    )

    airports = airports.drop_duplicates("iata")
    airports = airports[airports["iata"].notna()]

    airlines = pd.read_parquet(
        AIRLINES_PATH,
        columns=[
            "iata",
            "name",
            "country",
        ],
    )

    airlines = airlines.drop_duplicates("iata")
    airlines = airlines[airlines["iata"].notna()]

    return airports, airlines


def enrich_chunk(
    flights: pd.DataFrame,
    airports: pd.DataFrame,
    airlines: pd.DataFrame,
) -> pd.DataFrame:
    """Enriquece un chunk de vuelos con aeropuertos y aerolíneas."""

    flights = flights.copy()

    # --------------------------------------------------
    # Airport Origin
    # --------------------------------------------------

    origin_airports = airports.rename(
        columns={
            "iata": "origin",
            "name": "origin_airport_name",
            "city": "origin_city",
            "country": "origin_country",
        }
    )

    flights = flights.merge(
        origin_airports,
        on="origin",
        how="left",
    )

    # --------------------------------------------------
    # Airport Destination
    # --------------------------------------------------

    destination_airports = airports.rename(
        columns={
            "iata": "dest",
            "name": "dest_airport_name",
            "city": "dest_city",
            "country": "dest_country",
        }
    )

    flights = flights.merge(
        destination_airports,
        on="dest",
        how="left",
    )

    # --------------------------------------------------
    # Airline
    # --------------------------------------------------

    airline_catalog = airlines.rename(
        columns={
            "iata": "op_unique_carrier",
            "name": "carrier_name",
            "country": "carrier_country",
        }
    )

    flights = flights.merge(
        airline_catalog,
        on="op_unique_carrier",
        how="left",
    )

    return flights


def enrich_flights():
    """Procesa todos los archivos Silver de vuelos."""

    print("Cargando catálogos...")

    airports, airlines = load_catalogs()

    print(f"Aeropuertos disponibles: {len(airports):,}")
    print(f"Aerolíneas disponibles: {len(airlines):,}")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    files = sorted(
        FLIGHTS_DIR.glob("*.parquet")
    )

    total_rows = 0
    total_chunks = 0

    for file in files:

        print(f"\nProcesando: {file.name}")

        df = pd.read_parquet(file)

        for start in range(
            0,
            len(df),
            CHUNK_SIZE,
        ):

            chunk = df.iloc[
                start : start + CHUNK_SIZE
            ]

            enriched = enrich_chunk(
                chunk,
                airports,
                airlines,
            )

            output_file = (
                OUTPUT_DIR
                / f"{file.stem}_{start // CHUNK_SIZE:05d}.parquet"
            )

            enriched.to_parquet(
                output_file,
                index=False,
            )

            total_rows += len(enriched)
            total_chunks += 1

        print(
            f"  Filas procesadas: {len(df):,}"
        )

    print("\nEnrichment terminado")
    print(f"Chunks generados: {total_chunks:,}")
    print(f"Filas procesadas: {total_rows:,}")
    print(f"Salida: {OUTPUT_DIR}")


if __name__ == "__main__":
    enrich_flights()
