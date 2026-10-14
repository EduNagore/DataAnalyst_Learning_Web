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
    # TODO
    ...


def pyg(lineas: pd.DataFrame, orders: pd.DataFrame, marketing_spend: pd.DataFrame, anio: int) -> pd.Series:
    """Cuenta de resultados hasta la contribución de un año natural (en euros).
    ventas_lista = Σ cantidad·precio_lista; descuentos = ventas_lista − ventas_brutas;
    ventas_brutas = Σ cantidad·precio_final; devoluciones = ventas brutas de las líneas devueltas;
    ventas_netas = ventas_brutas − devoluciones; coste_producto = coste de las líneas NO devueltas
    (la mercancía devuelta vuelve al almacén); margen_bruto = ventas_netas − coste_producto;
    envios = Σ shipping_cost de los pedidos no cancelados; marketing = Σ spend_eur;
    contribucion = margen_bruto − envios − marketing. Incluye margen_bruto_pct y contribucion_pct sobre ventas netas."""
    # TODO
    ...


def comparar(a: pd.Series, b: pd.Series) -> pd.DataFrame:
    """Tabla con las columnas `anterior`, `actual` y `variacion_pct` (actual/anterior − 1, en %)
    para las partidas en euros; en las partidas en % (`_pct`), `variacion_pct` es la diferencia en puntos."""
    # TODO
    ...


lin = lineas_pedido(orders, order_items, products, returns)
p24, p25 = (pyg(lin, orders, marketing_spend, a) for a in (2024, 2025))
print((comparar(p24, p25) / 1).round(2))
