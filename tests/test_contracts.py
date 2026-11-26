"""Tests del validador de data contracts y de su uso en la capa Gold."""

import pandas as pd
import pytest

from factories import flight
from pipeline.airport_performance import create_airport_performance
from pipeline.contracts import (
    ContractViolationError,
    enforce_contract,
    load_contract,
    validate_contract,
)
from pipeline.gold import create_airline_performance
from pipeline.route_performance import create_route_performance

GOLD_CONTRACTS = {
    "airline_performance": create_airline_performance,
    "airport_performance": create_airport_performance,
    "route_performance": create_route_performance,
}

SIMPLE_CONTRACT = {
    "columns": {
        "airport": {"type": "string", "required": True},
        "total_departures": {"type": "integer", "required": True},
        "cancellation_rate": {"type": "numeric", "required": True},
    }
}


def valid_frame():
    return pd.DataFrame(
        {
            "airport": ["JFK", "LAX"],
            "total_departures": [10, 20],
            "cancellation_rate": [0.1, 0.0],
        }
    )


# ---------------------------------------------------------------------
# validate_contract: reglas individuales
# ---------------------------------------------------------------------


def test_valid_frame_has_no_violations():
    assert validate_contract(valid_frame(), SIMPLE_CONTRACT) == []


def test_missing_column_is_reported():
    df = valid_frame().drop(columns=["cancellation_rate"])
    violations = validate_contract(df, SIMPLE_CONTRACT)

    assert any("Columnas faltantes" in v and "cancellation_rate" in v for v in violations)


def test_undeclared_column_is_reported_in_strict_mode():
    df = valid_frame().assign(passenger_email="x@example.com")
    violations = validate_contract(df, SIMPLE_CONTRACT)

    assert any("no declaradas" in v and "passenger_email" in v for v in violations)


def test_undeclared_column_is_allowed_when_not_strict():
    df = valid_frame().assign(extra=1)

    assert validate_contract(df, SIMPLE_CONTRACT, strict=False) == []


def test_integer_column_stored_as_float_is_reported():
    df = valid_frame().astype({"total_departures": "float64"})
    violations = validate_contract(df, SIMPLE_CONTRACT)

    assert any("total_departures" in v and "integer" in v for v in violations)


def test_nulls_in_required_column_are_reported():
    df = valid_frame()
    df.loc[0, "cancellation_rate"] = None
    violations = validate_contract(df, SIMPLE_CONTRACT)

    assert any("cancellation_rate" in v and "nulos" in v for v in violations)


def test_boolean_is_not_accepted_as_numeric():
    df = valid_frame().assign(cancellation_rate=[True, False])
    violations = validate_contract(df, SIMPLE_CONTRACT)

    assert any("cancellation_rate" in v for v in violations)


def test_enforce_raises_with_all_violations():
    df = valid_frame().drop(columns=["airport"]).astype({"total_departures": "float64"})

    with pytest.raises(ContractViolationError) as excinfo:
        enforce_contract(df, "gold_airport_performance")

    assert excinfo.value.contract_name == "gold_airport_performance"
    assert len(excinfo.value.violations) >= 2


def test_unknown_contract_fails_loudly():
    with pytest.raises(FileNotFoundError):
        load_contract("gold_does_not_exist")


# ---------------------------------------------------------------------
# Las tablas Gold reales cumplen su contrato
# ---------------------------------------------------------------------


@pytest.mark.parametrize("name", GOLD_CONTRACTS)
def test_gold_output_matches_contract(lake, name):
    lake.add_day(
        "2024-01-01",
        [
            flight(carrier="AA", origin="JFK", dest="LAX", arr_delay=20.0),
            flight(carrier="DL", origin="LAX", dest="JFK", arr_delay=None, cancelled=True),
            # Aeropuerto que solo recibe vuelos: provoca NaN en el merge outer.
            flight(carrier="AA", origin="JFK", dest="SMALL", arr_delay=5.0),
        ],
    )

    GOLD_CONTRACTS[name]()
    df = lake.read_gold(name)

    assert validate_contract(df, load_contract(f"gold_{name}")) == []


@pytest.mark.parametrize("name", GOLD_CONTRACTS)
def test_gold_column_order_matches_contract(lake, name):
    """Snowflake carga por posición en COPY INTO; el orden importa."""

    lake.add_day("2024-01-01", [flight()])

    GOLD_CONTRACTS[name]()
    df = lake.read_gold(name)

    assert list(df.columns) == list(load_contract(f"gold_{name}")["columns"])
