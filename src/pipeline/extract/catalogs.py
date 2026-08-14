from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]

RAW_DIR = PROJECT_ROOT / "data" / "raw" / "catalogs"
BRONZE_DIR = PROJECT_ROOT / "data" / "bronze"


CATALOGS = {
    "airlines": "airlines.csv",
    "airplanes": "airplanes.csv",
    "airports": "airports.csv",
    "routes": "routes.csv",
}


def extract_catalog(name: str) -> pd.DataFrame:
    """
    Lee un catálogo CSV desde la zona Raw.
    """
    if name not in CATALOGS:
        raise ValueError(f"Catálogo no soportado: {name}")

    file_path = RAW_DIR / CATALOGS[name]

    if not file_path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo: {file_path}"
        )

    return pd.read_csv(
        file_path,
        low_memory=False
    )


def save_bronze(df: pd.DataFrame, name: str) -> Path:
    """
    Guarda un catálogo en Bronze como Parquet.
    """
    output_dir = BRONZE_DIR / name
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{name}.parquet"

    df.to_parquet(
        output_path,
        index=False
    )

    return output_path


def extract_all_catalogs() -> None:
    """
    Extrae todos los catálogos y los guarda en Bronze.
    """
    for name in CATALOGS:
        print(f"Extrayendo catálogo: {name}...")

        df = extract_catalog(name)

        output_path = save_bronze(df, name)

        print(
            f"  Filas: {len(df):,} | "
            f"Columnas: {len(df.columns)} | "
            f"Bronze: {output_path}"
        )


if __name__ == "__main__":
    extract_all_catalogs()
