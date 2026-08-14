from pathlib import Path

import pandas as pd


SILVER_PATH = Path("data/silver/flights")
GOLD_PATH = Path("data/gold")


def create_route_performance():

    print("Creando Gold: route_performance...")

    files = sorted(SILVER_PATH.glob("*.parquet"))

    results = []

    for file in files:

        df = pd.read_parquet(
            file,
            columns=[
                "origin",
                "dest",
                "distance",
                "is_cancelled",
                "is_diverted",
                "is_delayed",
                "arr_delay",
            ],
        )

        # ---------------------------------
        # MÉTRICAS POR RUTA
        # ---------------------------------

        route = (
            df.groupby(["origin", "dest"])
            .agg(
                total_flights=("origin", "size"),
                cancelled_flights=("is_cancelled", "sum"),
                diverted_flights=("is_diverted", "sum"),
                delayed_flights=("is_delayed", "sum"),
                avg_arrival_delay=("arr_delay", "mean"),
                avg_distance=("distance", "mean"),
            )
            .reset_index()
        )

        results.append(route)

    # ---------------------------------
    # CONSOLIDAR TODOS LOS PARQUET
    # ---------------------------------

    result = (
        pd.concat(results, ignore_index=True)
        .groupby(["origin", "dest"], as_index=False)
        .agg(
            total_flights=("total_flights", "sum"),
            cancelled_flights=("cancelled_flights", "sum"),
            diverted_flights=("diverted_flights", "sum"),
            delayed_flights=("delayed_flights", "sum"),
            avg_arrival_delay=("avg_arrival_delay", "mean"),
            avg_distance=("avg_distance", "mean"),
        )
    )

    # ---------------------------------
    # MÉTRICAS DE NEGOCIO
    # ---------------------------------

    result["delay_rate"] = (
        result["delayed_flights"]
        / result["total_flights"]
    )

    result["cancellation_rate"] = (
        result["cancelled_flights"]
        / result["total_flights"]
    )

    # ---------------------------------
    # EVITAR DIVISIONES POR CERO
    # ---------------------------------

    result["delay_rate"] = (
        result["delay_rate"]
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
        .fillna(0)
    )

    # ---------------------------------
    # DISTANCIA REDONDEADA
    # ---------------------------------

    result["avg_distance"] = (
        result["avg_distance"]
        .round(2)
    )

    result["avg_arrival_delay"] = (
        result["avg_arrival_delay"]
        .round(2)
    )

    # ---------------------------------
    # ORDENAR POR VOLUMEN
    # ---------------------------------

    result = result.sort_values(
        "total_flights",
        ascending=False,
    )

    # ---------------------------------
    # GUARDAR GOLD
    # ---------------------------------

    output_path = (
        GOLD_PATH / "route_performance"
    )

    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        output_path
        / "route_performance.parquet"
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
        f"\nTotal rutas: {len(result)}"
    )

    print(
        f"Archivo: {output_file}"
    )


if __name__ == "__main__":
    create_route_performance()
