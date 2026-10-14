import pandas as pd
from datakit.data import load_table

shipments = load_table("shipments")
inventory = load_table("inventory_snapshots")
products = load_table("products")
orders = load_table("orders")
order_items = load_table("order_items")


def retraso_dias(shipments: pd.DataFrame) -> pd.Series:
    """Días de retraso de cada envío: fecha real − fecha prometida (negativo si llega antes)."""
    return (pd.to_datetime(shipments["actual_date"]) - pd.to_datetime(shipments["promised_date"])).dt.days


def puntualidad(shipments: pd.DataFrame, por: str | None = None):
    """Porcentaje de envíos que llegan a tiempo (real ≤ prometida). Con `por` (p. ej. «carrier»),
    una serie con el porcentaje de cada grupo."""
    a_tiempo = (retraso_dias(shipments) <= 0).astype(float)
    if por is None:
        return float(100 * a_tiempo.mean())
    return 100 * a_tiempo.groupby(shipments[por]).mean()


def retraso_grave(shipments: pd.DataFrame, umbral: int = 5) -> float:
    """Porcentaje de envíos con `umbral` días de retraso o más."""
    return float(100 * (retraso_dias(shipments) >= umbral).mean())


def rotura_mensual(inventory: pd.DataFrame, products: pd.DataFrame, categoria: str) -> pd.DataFrame:
    """Por mes (Period) y para una categoría principal (p. ej. «cat-00»): `stock_medio` por producto y almacén
    y `pct_sin_stock` (porcentaje de registros semanales con stock 0)."""
    x = inventory.merge(products[["product_id", "category_id"]], on="product_id")
    x = x[x["category_id"].str.startswith(categoria)].copy()
    x["mes"] = pd.to_datetime(x["snapshot_date"]).dt.to_period("M")
    x["sin_stock"] = x["stock_qty"] == 0
    g = x.groupby("mes").agg(stock_medio=("stock_qty", "mean"), pct_sin_stock=("sin_stock", "mean"))
    g["pct_sin_stock"] = 100 * g["pct_sin_stock"]
    return g


def rotacion_inventario(inventory, products, orders, order_items, anio: int) -> dict:
    """Rotación del inventario de un año: coste de ventas (Σ cantidad·coste de los pedidos no cancelados) entre el
    valor medio del inventario a coste (media de los registros semanales del año). Devuelve valor_medio, coste_ventas,
    rotacion y dias_cobertura = 365 / rotación."""
    inv = inventory[pd.to_datetime(inventory["snapshot_date"]).dt.year == anio].merge(
        products[["product_id", "cost"]], on="product_id"
    )
    valor_medio = float((inv["stock_qty"] * inv["cost"]).groupby(inv["snapshot_date"]).sum().mean())
    ped = orders.loc[
        (orders["status"] != "cancelado") & (pd.to_datetime(orders["order_date"]).dt.year == anio), ["order_id"]
    ]
    v = order_items.merge(ped, on="order_id").merge(products[["product_id", "cost"]], on="product_id")
    coste_ventas = float((v["quantity"] * v["cost"]).sum())
    rotacion = coste_ventas / valor_medio
    return {
        "valor_medio": valor_medio,
        "coste_ventas": coste_ventas,
        "rotacion": rotacion,
        "dias_cobertura": 365 / rotacion,
    }


print("a tiempo:", round(puntualidad(shipments), 2), "% | retraso ≥ 5 días:", round(retraso_grave(shipments), 2), "%")
print(puntualidad(shipments, "carrier").round(2).to_dict())
print(rotura_mensual(inventory, products, "cat-00").loc["2026-02":"2026-04"].round(1))
print({k: round(v, 2) for k, v in rotacion_inventario(inventory, products, orders, order_items, 2025).items()})
