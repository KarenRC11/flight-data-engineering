import pandas as pd

from pipeline.transform.transforms import transform_flights


def test_transform_flights():

    df = pd.DataFrame({
        "fl_date": ["2024-01-01"],
        "op_carrier_fl_num": [4814.0],
        "cancellation_code": [None],
        "cancelled": [0],
        "diverted": [0],
        "arr_delay": [-19.0],
        "distance": [509.0],
    })

    result = transform_flights(df)

    assert pd.api.types.is_datetime64_any_dtype(
        result["fl_date"]
    )

    assert result["op_carrier_fl_num"].iloc[0] == 4814

    assert not result["is_cancelled"].iloc[0]
    assert not result["is_diverted"].iloc[0]
    assert not result["is_delayed"].iloc[0]

    assert result["flight_year"].iloc[0] == 2024

    assert result["flight_month"].iloc[0] == 1

    assert result["flight_day"].iloc[0] == 1
