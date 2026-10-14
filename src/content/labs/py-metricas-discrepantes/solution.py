import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
order_items = load_table("order_items")
returns = load_table("returns")
products = load_table("products")

DEFINICIONES = ["lista", "todos", "no_cancelados", "completados", "netos"]


def lineas(orders, order_items, returns, products, anio: int) -> pd.DataFrame:
    """YA IMPLEMENTADA. Una fila por línea de pedido del año con: status, cantidad, precio_lista, precio_final, devuelta."""
    o = orders.loc[pd.to_datetime(orders["order_date"]).dt.year == anio, ["order_id", "status"]]
    x = order_items.merge(o, on="order_id").merge(products[["product_id", "price"]], on="product_id")
    x["devuelta"] = x["order_item_id"].isin(returns["order_item_id"])
    return x.rename(columns={"quantity": "cantidad", "price": "precio_lista", "unit_price": "precio_final"})


def ingresos(lin: pd.DataFrame, definicion: str) -> float:
    """«Ingresos» según cinco definiciones habituales, sobre las líneas de `lineas()`:
    lista = Σ cantidad·precio_lista de las líneas no canceladas; todos = Σ cantidad·precio_final incluidos los
    cancelados; no_cancelados = Σ cantidad·precio_final sin cancelados; completados = lo anterior solo de pedidos
    con status «completado»; netos = no_cancelados menos las líneas devueltas. Lanza ValueError si la definición no existe."""
    if definicion not in DEFINICIONES:
        raise ValueError(f"Definición desconocida: {definicion}")
    vivas = lin[lin["status"] != "cancelado"]
    if definicion == "lista":
        return float((vivas["cantidad"] * vivas["precio_lista"]).sum())
    if definicion == "todos":
        return float((lin["cantidad"] * lin["precio_final"]).sum())
    if definicion == "completados":
        c = lin[lin["status"] == "completado"]
        return float((c["cantidad"] * c["precio_final"]).sum())
    if definicion == "netos":
        vivas = vivas[~vivas["devuelta"]]
    return float((vivas["cantidad"] * vivas["precio_final"]).sum())


def tabla_de_discrepancias(lin: pd.DataFrame) -> pd.Series:
    """Los ingresos con cada definición, de mayor a menor, en millones de euros."""
    return pd.Series({d: ingresos(lin, d) / 1e6 for d in DEFINICIONES}).sort_values(ascending=False)


def dispersion(tabla: pd.Series) -> float:
    """Diferencia entre la definición más alta y la más baja, como % de la más baja."""
    return float(100 * (tabla.max() - tabla.min()) / tabla.min())


def pedidos(orders: pd.DataFrame, anio: int, definicion: str) -> int:
    """Número de pedidos del año: todos, no_cancelados o completados (por `status`)."""
    o = orders[pd.to_datetime(orders["order_date"]).dt.year == anio]
    if definicion == "no_cancelados":
        o = o[o["status"] != "cancelado"]
    elif definicion == "completados":
        o = o[o["status"] == "completado"]
    return int(len(o))


l25 = lineas(orders, order_items, returns, products, 2025)
t = tabla_de_discrepancias(l25)
print(t.round(2).to_dict())
print("dispersión:", round(dispersion(t), 1), "% | pedidos:", {d: pedidos(orders, 2025, d) for d in ("todos", "no_cancelados", "completados")})
