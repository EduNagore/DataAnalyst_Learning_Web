import numpy as np
import pandas as pd
from datakit.data import load_table
from scipy import stats

orders = load_table("orders")
order_items = load_table("order_items")
customers = load_table("customers")
products = load_table("products")


def serie_mensual(orders, order_items, customers, products) -> pd.DataFrame:
    """Mes → rev_and, rev_resto, q_and, q_resto (Electrónica, sin cancelados)."""
    # TODO
    ...


def did_log(serie, y, previo=("2024-03", "2025-02"), posterior=("2025-03", "2026-02")) -> dict:
    """DiD en logaritmos: did, efecto_pct, se, ic_inf, ic_sup (en %)."""
    # TODO
    ...


def pendiente_previa(serie, y, previo=("2024-03", "2025-02")) -> tuple[float, float, float]:
    """(pendiente, error estándar, p-valor) de la tendencia previa del log-cociente."""
    # TODO
    ...


def estudio_eventos(serie, y, base="2025-02") -> pd.Series:
    """Log-cociente Andalucía / resto menos su valor en el mes base."""
    # TODO
    ...


serie = serie_mensual(orders, order_items, customers, products)
for y in ("rev", "q"):
    print(y, {k: round(v, 4) for k, v in did_log(serie, y).items()})
    print("  tendencia previa:", [round(v, 4) for v in pendiente_previa(serie, y)])
