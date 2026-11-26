"""Validación automática de data contracts.

Los contratos en ``data_contract/schema/*.json`` describen las columnas,
tipos y obligatoriedad de cada dataset. Este módulo los convierte de
documentación a una regla que se ejecuta: si una tabla Gold no cumple su
contrato, el pipeline se detiene antes de escribirla y publicarla en S3.

Uso:

    from pipeline.contracts import enforce_contract

    enforce_contract(df, "gold_route_performance")
"""

import json
from functools import lru_cache
from pathlib import Path

import pandas as pd
from pandas.api import types as ptypes

CONTRACTS_DIR = Path(__file__).resolve().parents[2] / "data_contract" / "schema"


class ContractViolationError(ValueError):
    """El DataFrame no cumple su data contract."""

    def __init__(self, contract_name: str, violations: list[str]):
        self.contract_name = contract_name
        self.violations = violations
        detail = "\n".join(f"  - {v}" for v in violations)
        super().__init__(
            f"El dataset no cumple el contrato '{contract_name}':\n{detail}"
        )


# Tipo declarado en el contrato -> verificación sobre el dtype de pandas.
_TYPE_CHECKS = {
    "string": lambda s: ptypes.is_string_dtype(s) or ptypes.is_object_dtype(s),
    "integer": lambda s: ptypes.is_integer_dtype(s),
    "numeric": lambda s: ptypes.is_numeric_dtype(s) and not ptypes.is_bool_dtype(s),
    "boolean": lambda s: ptypes.is_bool_dtype(s),
    "date": lambda s: ptypes.is_datetime64_any_dtype(s),
}


@lru_cache(maxsize=None)
def load_contract(name: str) -> dict:
    """Carga un contrato por nombre de archivo, sin la extensión .json."""

    path = CONTRACTS_DIR / f"{name}.json"

    if not path.exists():
        raise FileNotFoundError(f"No existe el contrato: {path}")

    with path.open(encoding="utf-8") as f:
        return json.load(f)


def validate_contract(df: pd.DataFrame, contract: dict, strict: bool = True) -> list[str]:
    """Devuelve la lista de violaciones; una lista vacía significa que cumple.

    Reglas:
      1. Toda columna del contrato debe existir.
      2. Con ``strict=True``, no se permiten columnas fuera del contrato
         (evita que columnas técnicas o sensibles se publiquen sin revisión).
      3. El dtype debe corresponder al tipo declarado.
      4. Las columnas con ``required: true`` no pueden tener nulos.
    """

    violations = []
    columns = contract.get("columns", {})

    missing = [c for c in columns if c not in df.columns]
    if missing:
        violations.append(f"Columnas faltantes: {missing}")

    if strict:
        extra = [c for c in df.columns if c not in columns]
        if extra:
            violations.append(f"Columnas no declaradas en el contrato: {extra}")

    for name, spec in columns.items():
        if name not in df.columns:
            continue

        series = df[name]
        expected_type = spec.get("type")
        check = _TYPE_CHECKS.get(expected_type)

        if check is None:
            violations.append(f"'{name}': tipo desconocido en el contrato '{expected_type}'")
        elif not check(series):
            violations.append(
                f"'{name}': se esperaba {expected_type}, se encontró {series.dtype}"
            )

        if spec.get("required", False):
            nulls = int(series.isna().sum())
            if nulls:
                violations.append(f"'{name}': {nulls} valores nulos en columna obligatoria")

    return violations


def enforce_contract(df: pd.DataFrame, contract_name: str, strict: bool = True) -> None:
    """Lanza ContractViolationError si el DataFrame no cumple el contrato."""

    violations = validate_contract(df, load_contract(contract_name), strict=strict)

    if violations:
        raise ContractViolationError(contract_name, violations)

    print(f"✅ Contrato '{contract_name}' validado ({len(df):,} filas)")
