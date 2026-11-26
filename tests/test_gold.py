"""Tests de las tres tablas Gold con una capa Silver sintética.

El escenario clave: la misma ruta aparece en dos días con distinto
volumen de vuelos. Las métricas Gold deben ponderar por vuelo, no por
archivo. Un promedio de promedios diarios da el mismo peso a un día con
1 vuelo que a un día con 3, y sesga el resultado.
"""

import pytest

from pipeline.airport_performance import create_airport_performance
from pipeline.gold import create_airline_performance
from pipeline.route_performance import create_route_performance
from factories import flight


@pytest.fixture
def uneven_days(lake):
    """JFK→LAX: 1 vuelo con 100 min de retraso el día 1; 3 vuelos puntuales el día 2."""

    lake.add_day(
        "2024-01-01",
        [flight(arr_delay=100.0, distance=2475.0)],
    )
    lake.add_day(
        "2024-01-02",
        [
            flight(arr_delay=0.0, distance=2475.0),
            flight(arr_delay=0.0, distance=2475.0),
            flight(arr_delay=0.0, distance=2475.0),
        ],
    )
    return lake


# ---------------------------------------------------------------------
# route_performance
# ---------------------------------------------------------------------


def test_route_avg_delay_is_weighted_by_flight(uneven_days):
    create_route_performance()
    route = uneven_days.read_gold("route_performance").iloc[0]

    # 100 min de retraso total / 4 vuelos = 25.
    # El cálculo anterior (promedio de promedios diarios) daba (100 + 0) / 2 = 50.
    assert route["avg_arrival_delay"] == pytest.approx(25.0)
    assert route["total_flights"] == 4
    assert route["delayed_flights"] == 1
    assert route["delay_rate"] == pytest.approx(0.25)


def test_route_avg_distance_is_weighted_by_flight(lake):
    # La distancia de una ruta puede variar ligeramente entre registros.
    lake.add_day("2024-01-01", [flight(distance=1000.0)])
    lake.add_day(
        "2024-01-02",
        [flight(distance=2000.0), flight(distance=2000.0), flight(distance=2000.0)],
    )

    create_route_performance()
    route = lake.read_gold("route_performance").iloc[0]

    # (1000 + 3 * 2000) / 4 = 1750, no (1000 + 2000) / 2 = 1500.
    assert route["avg_distance"] == pytest.approx(1750.0)


def test_route_ignores_missing_arrival_delay_in_average(lake):
    # Un vuelo cancelado no tiene arr_delay; no debe contar como 0 minutos.
    lake.add_day(
        "2024-01-01",
        [
            flight(arr_delay=30.0),
            flight(arr_delay=None, cancelled=True),
        ],
    )

    create_route_performance()
    route = lake.read_gold("route_performance").iloc[0]

    assert route["avg_arrival_delay"] == pytest.approx(30.0)
    assert route["total_flights"] == 2
    assert route["cancelled_flights"] == 1
    assert route["cancellation_rate"] == pytest.approx(0.5)


def test_route_output_has_no_technical_columns(uneven_days):
    create_route_performance()
    columns = set(uneven_days.read_gold("route_performance").columns)

    assert not {c for c in columns if c.endswith("_sum") or c.endswith("_count")}


# ---------------------------------------------------------------------
# airline_performance
# ---------------------------------------------------------------------


def test_airline_metrics_are_weighted_by_flight(uneven_days):
    create_airline_performance()
    airline = uneven_days.read_gold("airline_performance").iloc[0]

    assert airline["op_unique_carrier"] == "AA"
    assert airline["total_flights"] == 4
    assert airline["avg_arr_delay"] == pytest.approx(25.0)
    assert airline["delay_rate"] == pytest.approx(0.25)
    assert airline["cancellation_rate"] == pytest.approx(0.0)


def test_airline_rows_are_one_per_carrier(lake):
    lake.add_day("2024-01-01", [flight(carrier="AA"), flight(carrier="DL")])
    lake.add_day("2024-01-02", [flight(carrier="AA")])

    create_airline_performance()
    airlines = lake.read_gold("airline_performance")

    assert airlines["op_unique_carrier"].is_unique
    assert dict(zip(airlines["op_unique_carrier"], airlines["total_flights"])) == {
        "AA": 2,
        "DL": 1,
    }


# ---------------------------------------------------------------------
# airport_performance
# ---------------------------------------------------------------------


def test_airport_counts_departures_and_arrivals(lake):
    lake.add_day(
        "2024-01-01",
        [
            flight(origin="JFK", dest="LAX", arr_delay=20.0),
            flight(origin="LAX", dest="JFK", arr_delay=0.0, cancelled=True),
        ],
    )

    create_airport_performance()
    airports = lake.read_gold("airport_performance").set_index("airport")

    assert airports.loc["JFK", "total_departures"] == 1
    assert airports.loc["JFK", "total_arrivals"] == 1
    assert airports.loc["LAX", "cancelled_departures"] == 1
    assert airports.loc["LAX", "cancellation_rate"] == pytest.approx(1.0)
    # LAX recibe el vuelo con 20 min de retraso.
    assert airports.loc["LAX", "avg_arrival_delay"] == pytest.approx(20.0)


def test_airport_with_only_arrivals_has_zero_rates_not_nan(lake):
    lake.add_day("2024-01-01", [flight(origin="JFK", dest="SMALL")])

    create_airport_performance()
    small = lake.read_gold("airport_performance").set_index("airport").loc["SMALL"]

    assert small["total_departures"] == 0
    assert small["cancellation_rate"] == 0
    assert small["arrival_delay_rate"] == 0
