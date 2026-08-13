import pandas as pd


def validate_flights(df: pd.DataFrame) -> dict:
    """
    Ejecuta reglas básicas de calidad sobre los vuelos.
    """

    results = {}

    # 1. Mes válido
    results["valid_month"] = df["month"].between(1, 12).all()

    # 2. Día de semana válido
    results["valid_day_of_week"] = df["day_of_week"].between(1, 7).all()

    # 3. Distancia válida
    results["valid_distance"] = (df["distance"] >= 0).all()

    # 4. Cancelled debe ser 0 o 1
    results["valid_cancelled"] = df["cancelled"].isin([0, 1]).all()

    # 5. Diverted debe ser 0 o 1
    results["valid_diverted"] = df["diverted"].isin([0, 1]).all()

    # 6. Si el vuelo está cancelado,
    # debería tener código de cancelación
    cancelled_missing_code = (
        (df["cancelled"] == 1)
        & (df["cancellation_code"].isna())
    ).sum()

    results["cancelled_have_code"] = (
        cancelled_missing_code == 0
    )

    # 7. Un vuelo no cancelado no debería
    # tener código de cancelación
    non_cancelled_with_code = (
        (df["cancelled"] == 0)
        & (df["cancellation_code"].notna())
    ).sum()

    results["non_cancelled_without_code"] = (
        non_cancelled_with_code == 0
    )

    return results
