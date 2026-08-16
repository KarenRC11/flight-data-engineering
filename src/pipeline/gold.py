from pathlib import Path

import pandas as pd


SILVER_PATH = Path("data/silver/flights")
GOLD_PATH = Path("data/gold")


def create_airline_performance():

    print("Creando Gold: airline_performance...")

    files = sorted(
    SILVER_PATH.glob("event_date=*/*.parquet")
    )

    results = []

    for file in files:

        df = pd.read_parquet(
            file,
            columns=[
                "op_unique_carrier",
                "is_cancelled",
                "is_diverted",
                "is_delayed",
                "arr_delay",
            ],
        )

        grouped = (
            df.groupby("op_unique_carrier")
            .agg(
                total_flights=("op_unique_carrier", "size"),
                cancelled_flights=("is_cancelled", "sum"),
                diverted_flights=("is_diverted", "sum"),
                delayed_flights=("is_delayed", "sum"),
                arr_delay_sum=("arr_delay", "sum"),
                arr_delay_count=("arr_delay", "count"),
            )
            .reset_index()
        )

        results.append(grouped)

    # ---------------------------------
    # Consolidar resultados de todos
    # los archivos Silver
    # ---------------------------------

    result = (
        pd.concat(results, ignore_index=True)
        .groupby("op_unique_carrier")
        .agg(
            total_flights=("total_flights", "sum"),
            cancelled_flights=("cancelled_flights", "sum"),
            diverted_flights=("diverted_flights", "sum"),
            delayed_flights=("delayed_flights", "sum"),
            arr_delay_sum=("arr_delay_sum", "sum"),
            arr_delay_count=("arr_delay_count", "sum"),
        )
        .reset_index()
    )

    # ---------------------------------
    # Promedio real de retraso
    # ---------------------------------

    result["avg_arr_delay"] = (
        result["arr_delay_sum"]
        / result["arr_delay_count"]
    )

    # ---------------------------------
    # Tasas
    # ---------------------------------

    result["cancellation_rate"] = (
        result["cancelled_flights"]
        / result["total_flights"]
    )

    result["delay_rate"] = (
        result["delayed_flights"]
        / result["total_flights"]
    )

    # ---------------------------------
    # Eliminar columnas técnicas
    # ---------------------------------

    result = result.drop(
        columns=[
            "arr_delay_sum",
            "arr_delay_count",
        ]
    )

    # ---------------------------------
    # Ordenar por volumen de vuelos
    # ---------------------------------

    result = result.sort_values(
        "total_flights",
        ascending=False,
    )

    # ---------------------------------
    # Guardar Gold
    # ---------------------------------

    output_path = GOLD_PATH / "airline_performance"

    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        output_path / "airline_performance.parquet"
    )

    result.to_parquet(
        output_file,
        engine="pyarrow",
        index=False,
    )

    # ---------------------------------
    # Resultado
    # ---------------------------------

    print("\nGold generado:")
    print(result.to_string(index=False))

    print(f"\nArchivo: {output_file}")


if __name__ == "__main__":
    create_airline_performance()
