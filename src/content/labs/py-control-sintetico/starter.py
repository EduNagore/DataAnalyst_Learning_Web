import numpy as np
import pandas as pd
from datakit.data import load_table
from scipy.optimize import nnls

orders = load_table("orders")
order_items = load_table("order_items")
customers = load_table("customers")
products = load_table("products")


def panel_regional(orders, order_items, customers, products, desde="2023-01", hasta="2026-02") -> pd.DataFrame:
    """Ingresos mensuales de Electrónica por región (filas = mes, columnas = región); 0 si no hay ventas."""
    # TODO
    ...


def a_indice(panel: pd.DataFrame, fin_previo: str) -> pd.DataFrame:
    """Cada región dividida por su media del periodo previo (hasta `fin_previo`) y multiplicada por 100."""
    # TODO
    ...


def pesos_sinteticos(previo: pd.DataFrame, tratada: str, lam: float = 1000.0) -> pd.Series:
    """Pesos no negativos que suman 1 de las donantes para reproducir la serie previa de `tratada`."""
    # TODO
    ...


def efecto_sintetico(panel: pd.DataFrame, tratada: str, inicio: str = "2025-03") -> dict:
    """pesos, rmse_previo, gap_pct (brecha media posterior en % del sintético) y ratio (RMSPE post/pre)."""
    # TODO
    ...


def placebos(panel: pd.DataFrame, tratada: str, inicio: str = "2025-03") -> pd.DataFrame:
    """Aplica el método a cada región: region, ratio, gap_pct (ordenado por ratio descendente)."""
    # TODO
    ...


panel = panel_regional(orders, order_items, customers, products)
andalucia = next(c for c in panel.columns if c.startswith("Andaluc"))
r = efecto_sintetico(panel, andalucia)
print(r["pesos"][r["pesos"] > 0.005].round(3).to_string())
print({k: round(v, 3) for k, v in r.items() if k != "pesos"})
pl = placebos(panel, andalucia)
print(pl.head(4).round(2).to_string(index=False))
print("p de permutación:", (pl["ratio"] >= r["ratio"]).mean())
