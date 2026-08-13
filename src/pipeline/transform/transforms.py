import pandas as pd


def transform_flights(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica transformaciones de limpieza y estandarización
    al dataset de vuelos.
    """

    df = df.copy()

    # -----------------------------
    # Tipos de datos
    # -----------------------------

    df["fl_date"] = pd.to_datetime(
        df["fl_date"],
        errors="coerce"
    )

    df["op_carrier_fl_num"] = pd.to_numeric(
        df["op_carrier_fl_num"],
        errors="coerce"
    ).astype("Int64")

    df["cancellation_code"] = (
        df["cancellation_code"]
        .astype("string")
        .str.strip()
    )

    # -----------------------------
    # Indicadores de negocio
    # -----------------------------

    df["is_cancelled"] = df["cancelled"].eq(1)

    df["is_diverted"] = df["diverted"].eq(1)

    df["is_delayed"] = (
        df["arr_delay"].fillna(0) > 15
    )

    # -----------------------------
    # Validación básica de valores
    # -----------------------------

    df["distance"] = df["distance"].where(
        df["distance"] >= 0
    )

    # -----------------------------
    # Columnas derivadas de fecha
    # -----------------------------

    df["flight_year"] = df["fl_date"].dt.year
    df["flight_month"] = df["fl_date"].dt.month
    df["flight_day"] = df["fl_date"].dt.day

    return df
