import pandas as pd
from datakit.data import load_raw, load_table

clientes = load_raw("customers").drop_duplicates("customer_id")
orders = load_table("orders")
items = load_table("order_items")

pedidos_2025 = orders[(orders["status"] != "cancelado") & (orders["order_date"].dt.year == 2025)]
importes = (
    (items["quantity"] * items["unit_price"])
    .groupby(items["order_id"])
    .sum()
    .reindex(pedidos_2025["order_id"])
    .reset_index(drop=True)
)
print(len(clientes), clientes["province"].isna().sum(), len(importes), round(importes.mean(), 2))


def tasa_ausentes_por_grupo(df: pd.DataFrame, col: str, por: str) -> pd.DataFrame:
    """Columnas: <por>, filas, ausentes, pct_ausentes (1 decimal), ordenado por <por>."""
    # TODO
    ...


def atipicos_iqr(x: pd.Series, k: float = 1.5) -> pd.Series:
    """Serie booleana: True si x queda fuera de [Q1 - k*IQR, Q3 + k*IQR]."""
    # TODO
    ...


def atipicos_mad(x: pd.Series, umbral: float = 3.5) -> pd.Series:
    """Serie booleana: True si |0.6745 * (x - mediana) / MAD| > umbral."""
    # TODO
    ...


print(tasa_ausentes_por_grupo(clientes, "province", "segment"))
print("IQR:", int(atipicos_iqr(importes).sum()), " MAD:", int(atipicos_mad(importes).sum()))
