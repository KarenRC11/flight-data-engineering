from pathlib import Path
import pandas as pd


def read_flight_data(
    file_path: str,
    chunksize: int = 100_000,
):
    """
    Lee el dataset de vuelos en chunks para evitar
    cargar todo el archivo en memoria.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")

    return pd.read_csv(
    path,
    chunksize=chunksize,
    dtype={"cancellation_code": "string"},
)
