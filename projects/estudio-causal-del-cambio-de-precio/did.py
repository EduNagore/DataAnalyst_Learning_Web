"""Panel región-mes, diferencias en diferencias y control sintético. Implementa los TODO."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize


def build_panel(orders: pd.DataFrame, items: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    """Panel con una fila por región y mes: columnas `region`, `mes` (primer día del mes), `ingresos`, `unidades`.

    Solo pedidos no cancelados; la región es la del cliente.
    """
    # TODO
    raise NotImplementedError


def did_estimate(panel: pd.DataFrame, treated_region: str, start: str, outcome: str = "ingresos") -> dict:
    """Estimador de diferencias en diferencias 2x2 sobre el logaritmo del resultado.

    effect = (media_post_tratada - media_pre_tratada) - (media_post_control - media_pre_control), en logs.
    Devuelve {"effect_log": ..., "effect_pct": ...} donde effect_pct = exp(effect_log) - 1.
    `start` es el primer mes del periodo posterior ('AAAA-MM-DD').
    """
    # TODO
    raise NotImplementedError


def synthetic_control_weights(y_treated_pre: np.ndarray, y_controls_pre: np.ndarray) -> np.ndarray:
    """Pesos w >= 0 con suma 1 que minimizan ||y_tratada_pre - y_controles_pre @ w||^2.

    y_controls_pre tiene forma (periodos, controles). Devuelve un vector de longitud n_controles.
    """
    # TODO: scipy.optimize.minimize con restricciones (SLSQP) y límites (0, 1).
    raise NotImplementedError


def placebo_effects(panel: pd.DataFrame, regions: list[str], start: str, outcome: str = "ingresos") -> pd.Series:
    """Efecto 'placebo' (DiD con cada región no tratada como si lo fuera). Sirve para ver cuán raro es el efecto real."""
    # TODO
    raise NotImplementedError


__all__ = ["build_panel", "did_estimate", "minimize", "placebo_effects", "synthetic_control_weights"]
