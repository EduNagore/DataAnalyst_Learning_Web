import pandas as pd
from datakit.data import load_table

shipments = load_table("shipments")
inventory = load_table("inventory_snapshots")
products = load_table("products")
orders = load_table("orders")
order_items = load_table("order_items")


def retraso_dias(shipments: pd.DataFrame) -> pd.Series:
    """Días de retraso de cada envío: fecha real − fecha prometida (negativo si llega antes)."""
    # TODO
    ...


def puntualidad(shipments: pd.DataFrame, por: str | None = None):
    """Porcentaje de envíos que llegan a tiempo (real ≤ prometida). Con `por` (p. ej. «carrier»),
    una serie con el porcentaje de cada grupo."""
    # TODO
    ...


def retraso_grave(shipments: pd.DataFrame, umbral: int = 5) -> float:
    """Porcentaje de envíos con `umbral` días de retraso o más."""
    # TODO
    ...


def rotura_mensual(inventory: pd.DataFrame, products: pd.DataFrame, categoria: str) -> pd.DataFrame:
    """Por mes (Period) y para una categoría principal (p. ej. «cat-00»): `stock_medio` por producto y almacén
    y `pct_sin_stock` (porcentaje de registros semanales con stock 0)."""
    # TODO
    ...


def rotacion_inventario(inventory, products, orders, order_items, anio: int) -> dict:
    """Rotación del inventario de un año: coste de ventas (Σ cantidad·coste de los pedidos no cancelados) entre el
    valor medio del inventario a coste (media de los registros semanales del año). Devuelve valor_medio, coste_ventas,
    rotacion y dias_cobertura = 365 / rotación."""
    # TODO
    ...


print("a tiempo:", round(puntualidad(shipments), 2), "% | retraso ≥ 5 días:", round(retraso_grave(shipments), 2), "%")
print(puntualidad(shipments, "carrier").round(2).to_dict())
print(rotura_mensual(inventory, products, "cat-00").loc["2026-02":"2026-04"].round(1))
print({k: round(v, 2) for k, v in rotacion_inventario(inventory, products, orders, order_items, 2025).items()})
