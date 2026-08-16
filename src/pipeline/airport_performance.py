from pathlib import Path

import pandas as pd


SILVER_PATH = Path("data/silver/flights")
GOLD_PATH = Path("data/gold")


def create_airport_performance():

    print("Creando Gold: airport_performance...")

    files = sorted(
    SILVER_PATH.glob("event_date=*/*.parquet")
    )

    departure_results = []
    arrival_results = []

    for file in files:

        df = pd.read_parquet(
            file,
            columns=[
                "origin",
                "dest",
                "is_cancelled",
                "is_diverted",
                "is_delayed",
                "arr_delay",
            ],
        )

        # ---------------------------------
        # DEPARTURES
        # ---------------------------------

        departures = (
            df.groupby("origin")
            .agg(
                total_departures=("origin", "size"),
                cancelled_departures=("is_cancelled", "sum"),
                diverted_departures=("is_diverted", "sum"),
                delayed_arrivals=("is_delayed", "sum"),
            )
            .reset_index()
            .rename(columns={"origin": "airport"})
        )

        departure_results.append(departures)

        # ---------------------------------
        # ARRIVALS
        # ---------------------------------

        arrivals = (
            df.groupby("dest")
            .agg(
                total_arrivals=("dest", "size"),
                arr_delay_sum=("arr_delay", "sum"),
                arr_delay_count=("arr_delay", "count"),
            )
            .reset_index()
            .rename(columns={"dest": "airport"})
        )

        arrival_results.append(arrivals)

    # ---------------------------------
    # CONSOLIDAR DEPARTURES
    # ---------------------------------

    departures = (
        pd.concat(departure_results, ignore_index=True)
        .groupby("airport")
        .sum()
        .reset_index()
    )

    # ---------------------------------
    # CONSOLIDAR ARRIVALS
    # ---------------------------------

    arrivals = (
        pd.concat(arrival_results, ignore_index=True)
        .groupby("airport")
        .sum()
        .reset_index()
    )

    # ---------------------------------
    # UNIR DEPARTURES + ARRIVALS
    # ---------------------------------

    result = departures.merge(
        arrivals,
        on="airport",
        how="outer",
    )

    # ---------------------------------
    # RELLENAR VALORES FALTANTES
    # ---------------------------------

    numeric_columns = [
        "total_departures",
        "cancelled_departures",
        "diverted_departures",
        "delayed_arrivals",
        "total_arrivals",
        "arr_delay_sum",
        "arr_delay_count",
    ]

    result[numeric_columns] = (
        result[numeric_columns]
        .fillna(0)
    )

    # ---------------------------------
    # MÉTRICAS DE NEGOCIO
    # ---------------------------------

    result["arrival_delay_rate"] = (
        result["delayed_arrivals"]
        / result["total_departures"]
    )

    result["cancellation_rate"] = (
        result["cancelled_departures"]
        / result["total_departures"]
    )

    result["avg_arrival_delay"] = (
        result["arr_delay_sum"]
        / result["arr_delay_count"]
    )

    # ---------------------------------
    # EVITAR DIVISIONES POR CERO
    # ---------------------------------

    result["arrival_delay_rate"] = (
        result["arrival_delay_rate"]
        .replace([float("inf"), -float("inf")], 0)
        .fillna(0)
    )

    result["cancellation_rate"] = (
        result["cancellation_rate"]
        .replace([float("inf"), -float("inf")], 0)
        .fillna(0)
    )

    result["avg_arrival_delay"] = (
        result["avg_arrival_delay"]
        .replace([float("inf"), -float("inf")], 0)
        .fillna(0)
    )

    # ---------------------------------
    # ELIMINAR COLUMNAS TÉCNICAS
    # ---------------------------------

    result = result.drop(
        columns=[
            "arr_delay_sum",
            "arr_delay_count",
        ]
    )

    # ---------------------------------
    # ORDENAR POR VOLUMEN DE OPERACIÓN
    # ---------------------------------

    result = result.sort_values(
        "total_departures",
        ascending=False,
    )

    # ---------------------------------
    # GUARDAR GOLD
    # ---------------------------------

    output_path = (
        GOLD_PATH / "airport_performance"
    )

    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        output_path
        / "airport_performance.parquet"
    )

    result.to_parquet(
        output_file,
        engine="pyarrow",
        index=False,
    )

    # ---------------------------------
    # RESULTADO
    # ---------------------------------

    print("\nGold generado:")

    print(
        result.head(20)
        .to_string(index=False)
    )

    print(
        f"\nTotal aeropuertos: {len(result)}"
    )

    print(
        f"Archivo: {output_file}"
    )


if __name__ == "__main__":
    create_airport_performance()
