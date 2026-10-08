import re

import pandas as pd
from datakit.data import load_raw, load_table

raw = load_raw("orders")
customers = load_table("customers")
print(raw.shape, raw["order_id"].nunique())
print(raw.head(3))

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7,
    "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
}


def parsear_fecha(texto: str) -> pd.Timestamp:
    """Convierte AAAA-MM-DD, DD/MM/AAAA o «D de mes de AAAA» en una fecha."""
    t = str(texto).strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", t):
        return pd.Timestamp(t)
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", t)
    if m:
        return pd.Timestamp(int(m[3]), int(m[2]), int(m[1]))
    m = re.fullmatch(r"(\d{1,2}) de (\w+) de (\d{4})", t)
    if m:
        return pd.Timestamp(int(m[3]), MESES[m[2].lower()], int(m[1]))
    raise ValueError(f"Formato de fecha no reconocido: {texto!r}")


def limpiar_pedidos(raw: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    """Una fila por pedido, ordenado por order_id, con las banderas cliente_valido y tienda_sin_id."""
    df = raw.assign(
        order_date=raw["order_date"].map(parsear_fecha),
        shipping_cost=raw["shipping_cost"].astype("string").str.replace(",", ".").astype("float64"),
        device=raw["device"].where(raw["channel"] != "store", "n/a"),
    )
    df = df.drop_duplicates().drop_duplicates("order_id")
    df = df.assign(
        cliente_valido=df["customer_id"].isin(customers["customer_id"]),
        tienda_sin_id=(df["channel"] == "store") & df["store_id"].isna(),
    )
    return df.sort_values("order_id").reset_index(drop=True)


limpio = limpiar_pedidos(raw, customers)
print(len(limpio), round(limpio["shipping_cost"].sum(), 2))
