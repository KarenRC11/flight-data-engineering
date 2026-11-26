"""Casos negativos de las reglas de calidad.

test_quality.py prueba que un vuelo correcto pasa. Aquí se prueba que
cada regla detecta el error que le corresponde, que es lo que protege
a la capa Silver.
"""

import pandas as pd
import pytest

from pipeline.transform.quality import validate_flights
from pipeline.transform.transforms import transform_flights


def base_flight(**overrides):
    row = {
        "month": 1,
        "day_of_week": 1,
        "distance": 509.0,
        "cancelled": 0,
        "diverted": 0,
        "cancellation_code": pd.NA,
    }
    row.update(overrides)
    return pd.DataFrame([row])


@pytest.mark.parametrize(
    "overrides, failing_rule",
    [
        ({"month": 13}, "valid_month"),
        ({"month": 0}, "valid_month"),
        ({"day_of_week": 8}, "valid_day_of_week"),
        ({"distance": -1.0}, "valid_distance"),
        ({"cancelled": 2}, "valid_cancelled"),
        ({"diverted": -1}, "valid_diverted"),
        ({"cancelled": 1, "cancellation_code": pd.NA}, "cancelled_have_code"),
        ({"cancelled": 0, "cancellation_code": "A"}, "non_cancelled_without_code"),
    ],
)
def test_each_rule_detects_its_error(overrides, failing_rule):
    results = validate_flights(base_flight(**overrides))

    assert not results[failing_rule]

    # Solo debe fallar la regla que corresponde: así un error no se
    # confunde con otro al revisar los logs de Silver.
    others = {rule: ok for rule, ok in results.items() if rule != failing_rule}
    assert all(others.values()), others


def test_cancelled_flight_with_code_passes():
    results = validate_flights(base_flight(cancelled=1, cancellation_code="B"))

    assert all(results.values())


def test_rules_evaluate_every_row_not_just_the_first():
    df = pd.concat(
        [base_flight(), base_flight(), base_flight(month=13)],
        ignore_index=True,
    )

    assert not validate_flights(df)["valid_month"]


# ---------------------------------------------------------------------
# transform_flights
# ---------------------------------------------------------------------


def transform_input(**overrides):
    row = {
        "fl_date": "2024-03-15",
        "op_carrier_fl_num": 100.0,
        "cancellation_code": None,
        "cancelled": 0,
        "diverted": 0,
        "arr_delay": 0.0,
        "distance": 300.0,
    }
    row.update(overrides)
    return pd.DataFrame([row])


@pytest.mark.parametrize(
    "arr_delay, expected",
    [(16.0, True), (15.0, True), (14.0, False), (-5.0, False), (None, False)],
)
def test_is_delayed_threshold(arr_delay, expected):
    result = transform_flights(transform_input(arr_delay=arr_delay))

    assert bool(result["is_delayed"].iloc[0]) is expected


def test_negative_distance_becomes_null():
    result = transform_flights(transform_input(distance=-10.0))

    assert pd.isna(result["distance"].iloc[0])


def test_invalid_date_becomes_null_instead_of_crashing():
    result = transform_flights(transform_input(fl_date="not-a-date"))

    assert pd.isna(result["fl_date"].iloc[0])


def test_cancellation_code_is_trimmed():
    result = transform_flights(transform_input(cancelled=1, cancellation_code="  A "))

    assert result["cancellation_code"].iloc[0] == "A"
