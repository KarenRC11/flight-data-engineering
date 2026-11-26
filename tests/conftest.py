"""Fixtures compartidos para probar las capas Gold sin el dataset completo.

Las funciones Gold leen archivos Parquet particionados desde
``SILVER_PATH`` y escriben en ``GOLD_PATH``. Estos fixtures crean una
capa Silver sintética y pequeña en un directorio temporal y redirigen
ambas rutas hacia ahí, para que los tests corran en CI en segundos.
"""

import pandas as pd
import pytest

from factories import write_silver_partition


@pytest.fixture
def lake(tmp_path, monkeypatch):
    """Redirige SILVER_PATH y GOLD_PATH de los módulos Gold a tmp_path."""

    import pipeline.airport_performance as airport_module
    import pipeline.gold as airline_module
    import pipeline.route_performance as route_module

    silver_dir = tmp_path / "silver" / "flights"
    gold_dir = tmp_path / "gold"
    silver_dir.mkdir(parents=True)

    for module in (airline_module, airport_module, route_module):
        monkeypatch.setattr(module, "SILVER_PATH", silver_dir)
        monkeypatch.setattr(module, "GOLD_PATH", gold_dir)

    class Lake:
        silver = silver_dir
        gold = gold_dir

        def add_day(self, event_date, rows):
            return write_silver_partition(silver_dir, event_date, rows)

        def read_gold(self, name):
            return pd.read_parquet(gold_dir / name / f"{name}.parquet")

    return Lake()
