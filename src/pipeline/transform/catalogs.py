from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]

BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"
SILVER_DIR = PROJECT_ROOT / "data" / "silver"


def clean_airlines(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df.columns = [
        "index",
        "airline_id",
        "name",
        "alias",
        "iata",
        "icao",
        "callsign",
        "country",
        "active",
    ]

    df = df.drop_duplicates()

    df["iata"] = df["iata"].astype("string").str.strip()
    df["icao"] = df["icao"].astype("string").str.strip()
    df["name"] = df["name"].astype("string").str.strip()
    df["country"] = df["country"].astype("string").str.strip()

    return df


def clean_airplanes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df.columns = [
        "index",
        "name",
        "iata_code",
        "icao_code",
    ]

    df = df.drop_duplicates()

    df["name"] = df["name"].astype("string").str.strip()
    df["iata_code"] = df["iata_code"].astype("string").str.strip()
    df["icao_code"] = df["icao_code"].astype("string").str.strip()

    return df


def clean_airports(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df.columns = [
        "index",
        "airport_id",
        "name",
        "city",
        "country",
        "iata",
        "icao",
        "latitude",
        "longitude",
        "altitude",
        "timezone",
        "dst",
        "tz_database_timezone",
        "type",
        "source",
    ]

    df = df.drop_duplicates()

    df["iata"] = df["iata"].astype("string").str.strip()
    df["icao"] = df["icao"].astype("string").str.strip()
    df["name"] = df["name"].astype("string").str.strip()
    df["city"] = df["city"].astype("string").str.strip()
    df["country"] = df["country"].astype("string").str.strip()

    df["latitude"] = pd.to_numeric(
        df["latitude"],
        errors="coerce",
    )

    df["longitude"] = pd.to_numeric(
        df["longitude"],
        errors="coerce",
    )

    df["altitude"] = pd.to_numeric(
        df["altitude"],
        errors="coerce",
    )

    return df


def clean_routes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df.columns = [
        "index",
        "airline",
        "airline_id",
        "source_airport",
        "source_airport_id",
        "destination_airport",
        "destination_airport_id",
        "codeshare",
        "stops",
        "equipment",
    ]

    df = df.drop_duplicates()

    df["airline"] = df["airline"].astype("string").str.strip()
    df["source_airport"] = (
        df["source_airport"].astype("string").str.strip()
    )
    df["destination_airport"] = (
        df["destination_airport"].astype("string").str.strip()
    )
    df["equipment"] = df["equipment"].astype("string").str.strip()

    df["stops"] = pd.to_numeric(
        df["stops"],
        errors="coerce",
    )

    return df


def save_silver(df: pd.DataFrame, name: str) -> Path:
    output_dir = SILVER_DIR / name
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{name}.parquet"

    df.to_parquet(
        output_path,
        index=False,
    )

    return output_path


def transform_catalogs() -> None:

    transformations = {
        "airlines": clean_airlines,
        "airplanes": clean_airplanes,
        "airports": clean_airports,
        "routes": clean_routes,
    }

    for name, transform_function in transformations.items():

        print(f"Transformando catálogo: {name}...")

        input_path = (
            BRONZE_DIR
            / name
            / f"{name}.parquet"
        )

        df = pd.read_parquet(input_path)

        df_clean = transform_function(df)

        output_path = save_silver(
            df_clean,
            name,
        )

        print(
            f"  Antes: {len(df):,} filas"
        )

        print(
            f"  Después: {len(df_clean):,} filas"
        )

        print(
            f"  Silver: {output_path}"
        )


if __name__ == "__main__":
    transform_catalogs()
