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
    g = df.groupby(por)[col]
    out = pd.DataFrame({"filas": g.size(), "ausentes": g.apply(lambda s: int(s.isna().sum()))})
    out["pct_ausentes"] = (out["ausentes"] / out["filas"] * 100).round(1)
    return out.reset_index().sort_values(por).reset_index(drop=True)


def atipicos_iqr(x: pd.Series, k: float = 1.5) -> pd.Series:
    """Serie booleana: True si x queda fuera de [Q1 - k*IQR, Q3 + k*IQR]."""
    q1, q3 = x.quantile(0.25), x.quantile(0.75)
    iqr = q3 - q1
    return (x < q1 - k * iqr) | (x > q3 + k * iqr)


def atipicos_mad(x: pd.Series, umbral: float = 3.5) -> pd.Series:
    """Serie booleana: True si |0.6745 * (x - mediana) / MAD| > umbral."""
    mediana = x.median()
    mad = (x - mediana).abs().median()
    z = 0.6745 * (x - mediana) / mad
    return z.abs() > umbral


print(tasa_ausentes_por_grupo(clientes, "province", "segment"))
print("IQR:", int(atipicos_iqr(importes).sum()), " MAD:", int(atipicos_mad(importes).sum()))
