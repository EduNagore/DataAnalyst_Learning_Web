import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
items = load_table("order_items")
customers = load_table("customers")

por_pedido = (
    items.assign(importe=items["quantity"] * items["unit_price"])
    .groupby("order_id")
    .agg(lineas=("order_id", "size"), importe=("importe", "sum"))
)
pedidos = (
    orders[orders["status"] != "cancelado"]
    .join(por_pedido, on="order_id")
    .merge(customers[["customer_id", "segment"]], on="customer_id")
    [["order_id", "customer_id", "segment", "discount_pct", "lineas", "importe"]]
)
print(pedidos.shape)


def correlaciones(df: pd.DataFrame, a: str, b: str) -> dict:
    """{'pearson': ..., 'spearman': ...} con 3 decimales."""
    return {
        "pearson": round(float(df[a].corr(df[b])), 3),
        "spearman": round(float(df[a].corr(df[b], method="spearman")), 3),
    }


def resumen_por_grupo(df: pd.DataFrame, grupo: str, medida: str) -> pd.DataFrame:
    """Columnas: <grupo>, n, media, mediana (1 decimal), ordenado por el grupo."""
    out = df.groupby(grupo)[medida].agg(n="size", media="mean", mediana="median").round(1)
    return out.reset_index().sort_values(grupo).reset_index(drop=True)


def importe_bruto_por_descuento(df: pd.DataFrame) -> pd.DataFrame:
    """Columnas: discount_pct, pedidos, importe_medio, importe_bruto_medio (1 decimal)."""
    out = df.groupby("discount_pct").agg(pedidos=("order_id", "size"), importe_medio=("importe", "mean"))
    out = out.reset_index()
    out["importe_bruto_medio"] = out["importe_medio"] / (1 - out["discount_pct"])
    out[["importe_medio", "importe_bruto_medio"]] = out[["importe_medio", "importe_bruto_medio"]].round(1)
    return out.sort_values("discount_pct").reset_index(drop=True)


print(correlaciones(pedidos, "lineas", "importe"))
print(resumen_por_grupo(pedidos, "segment", "importe"))
print(importe_bruto_por_descuento(pedidos))
