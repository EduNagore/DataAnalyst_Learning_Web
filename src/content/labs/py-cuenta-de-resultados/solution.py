import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
order_items = load_table("order_items")
products = load_table("products")
returns = load_table("returns")
marketing_spend = load_table("marketing_spend")


def lineas_pedido(orders, order_items, products, returns) -> pd.DataFrame:
    """Una fila por línea de pedidos no cancelados con: order_id, fecha, cantidad, precio_lista,
    precio_final, coste_unitario y devuelta (True si la línea aparece en `returns`)."""
    o = orders.loc[orders["status"] != "cancelado", ["order_id", "order_date"]].rename(columns={"order_date": "fecha"})
    x = order_items.merge(o, on="order_id").merge(
        products[["product_id", "price", "cost"]].rename(columns={"price": "precio_lista", "cost": "coste_unitario"}),
        on="product_id",
    )
    x["devuelta"] = x["order_item_id"].isin(returns["order_item_id"])
    x = x.rename(columns={"quantity": "cantidad", "unit_price": "precio_final"})
    return x[["order_id", "fecha", "cantidad", "precio_lista", "precio_final", "coste_unitario", "devuelta"]]


def pyg(lineas: pd.DataFrame, orders: pd.DataFrame, marketing_spend: pd.DataFrame, anio: int) -> pd.Series:
    """Cuenta de resultados hasta la contribución de un año natural (en euros).
    ventas_lista = Σ cantidad·precio_lista; descuentos = ventas_lista − ventas_brutas;
    ventas_brutas = Σ cantidad·precio_final; devoluciones = ventas brutas de las líneas devueltas;
    ventas_netas = ventas_brutas − devoluciones; coste_producto = coste de las líneas NO devueltas
    (la mercancía devuelta vuelve al almacén); margen_bruto = ventas_netas − coste_producto;
    envios = Σ shipping_cost de los pedidos no cancelados; marketing = Σ spend_eur;
    contribucion = margen_bruto − envios − marketing. Incluye margen_bruto_pct y contribucion_pct sobre ventas netas."""
    ln = lineas[pd.to_datetime(lineas["fecha"]).dt.year == anio]
    ventas_lista = float((ln["cantidad"] * ln["precio_lista"]).sum())
    ventas_brutas = float((ln["cantidad"] * ln["precio_final"]).sum())
    devoluciones = float((ln["cantidad"] * ln["precio_final"])[ln["devuelta"]].sum())
    ventas_netas = ventas_brutas - devoluciones
    coste = float((ln["cantidad"] * ln["coste_unitario"])[~ln["devuelta"]].sum())
    o = orders[(orders["status"] != "cancelado") & (pd.to_datetime(orders["order_date"]).dt.year == anio)]
    envios = float(o["shipping_cost"].sum())
    marketing = float(marketing_spend.loc[pd.to_datetime(marketing_spend["date"]).dt.year == anio, "spend_eur"].sum())
    margen = ventas_netas - coste
    contribucion = margen - envios - marketing
    return pd.Series(
        {
            "ventas_lista": ventas_lista,
            "descuentos": ventas_lista - ventas_brutas,
            "ventas_brutas": ventas_brutas,
            "devoluciones": devoluciones,
            "ventas_netas": ventas_netas,
            "coste_producto": coste,
            "margen_bruto": margen,
            "margen_bruto_pct": 100 * margen / ventas_netas,
            "envios": envios,
            "marketing": marketing,
            "contribucion": contribucion,
            "contribucion_pct": 100 * contribucion / ventas_netas,
        }
    )


def comparar(a: pd.Series, b: pd.Series) -> pd.DataFrame:
    """Tabla con las columnas `anterior`, `actual` y `variacion_pct` (actual/anterior − 1, en %)
    para las partidas en euros; en las partidas en % (`_pct`), `variacion_pct` es la diferencia en puntos."""
    t = pd.DataFrame({"anterior": a, "actual": b})
    es_pct = t.index.str.endswith("_pct")
    t["variacion_pct"] = 100 * (t["actual"] / t["anterior"] - 1)
    t.loc[es_pct, "variacion_pct"] = (t["actual"] - t["anterior"])[es_pct]
    return t


lin = lineas_pedido(orders, order_items, products, returns)
p24, p25 = (pyg(lin, orders, marketing_spend, a) for a in (2024, 2025))
print((comparar(p24, p25) / 1).round(2))
