import pandas as pd

from pipeline.transform.quality import validate_flights


def test_valid_flights():

    df = pd.DataFrame({
        "month": [1],
        "day_of_week": [1],
        "distance": [509.0],
        "cancelled": [0],
        "diverted": [0],
        "cancellation_code": [pd.NA],
    })

    results = validate_flights(df)

    assert results["valid_month"]
    assert results["valid_day_of_week"]
    assert results["valid_distance"]
    assert results["valid_cancelled"]
    assert results["valid_diverted"]
    assert results["non_cancelled_without_code"]
