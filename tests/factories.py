"""Constructores de datos Silver sintéticos para los tests."""

from pathlib import Path

import pandas as pd

SILVER_COLUMNS = [
    "op_unique_carrier",
    "origin",
    "dest",
    "distance",
    "is_cancelled",
    "is_diverted",
    "is_delayed",
    "arr_delay",
]


def write_silver_partition(silver_dir: Path, event_date: str, rows: list[dict]) -> Path:
    """Escribe una partición diaria con el mismo layout que silver.py."""

    partition = silver_dir / f"event_date={event_date}"
    partition.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(rows, columns=SILVER_COLUMNS)
    output_file = partition / "part-0000.parquet"
    df.to_parquet(output_file, engine="pyarrow", index=False)

    return output_file


def flight(
    carrier="AA",
    origin="JFK",
    dest="LAX",
    distance=2475.0,
    cancelled=False,
    diverted=False,
    arr_delay=0.0,
):
    """Construye un vuelo Silver con valores por defecto razonables."""

    return {
        "op_unique_carrier": carrier,
        "origin": origin,
        "dest": dest,
        "distance": distance,
        "is_cancelled": cancelled,
        "is_diverted": diverted,
        # Misma regla que transforms.transform_flights
        "is_delayed": (arr_delay if arr_delay is not None else 0) > 15,
        "arr_delay": arr_delay,
    }
