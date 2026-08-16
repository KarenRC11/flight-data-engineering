from pathlib import Path

import pandas as pd


def save_bronze(
    chunks,
    output_dir: str,
) -> int:
    """
    Guarda los chunks del dataset en Bronze.

    Los datos se particionan por event_date utilizando fl_date.
    """

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    total_rows = 0

    for chunk_number, chunk in enumerate(chunks):

        chunk["fl_date"] = pd.to_datetime(
            chunk["fl_date"],
            errors="coerce",
        )

        chunk = chunk.dropna(subset=["fl_date"])

        dates = chunk["fl_date"].dt.strftime("%Y-%m-%d").unique()

        for event_date in dates:

            date_chunk = chunk[
                chunk["fl_date"].dt.strftime("%Y-%m-%d") == event_date
            ]

            partition_path = (
                output_path
                / f"event_date={event_date}"
            )

            partition_path.mkdir(
                parents=True,
                exist_ok=True,
            )

            file_path = (
                partition_path
                / f"part-{chunk_number:05d}.parquet"
            )

            date_chunk.to_parquet(
                file_path,
                engine="pyarrow",
                index=False,
            )

            total_rows += len(date_chunk)

            print(
                f"Bronze: {file_path} "
                f"({len(date_chunk):,} registros)"
            )

    print(
        f"\nTotal Bronze: "
        f"{total_rows:,} registros"
    )

    return total_rows
