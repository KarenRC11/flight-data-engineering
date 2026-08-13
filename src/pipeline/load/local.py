from pathlib import Path

import pandas as pd


def save_bronze(
    chunks,
    output_dir: str,
) -> int:
    """
    Guarda los chunks del dataset en formato Parquet.

    Cada chunk se almacena como un archivo independiente.
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    total_rows = 0

    for chunk_number, chunk in enumerate(chunks):

        file_path = output_path / f"part-{chunk_number:05d}.parquet"

        chunk.to_parquet(
            file_path,
            engine="pyarrow",
            index=False,
        )

        total_rows += len(chunk)

        print(
            f"Bronze: {file_path.name} "
            f"({len(chunk):,} registros)"
        )

    print(f"\nTotal Bronze: {total_rows:,} registros")

    return total_rows
