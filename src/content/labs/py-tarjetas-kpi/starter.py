import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
items = load_table("order_items")
products = load_table("products")
shipments = load_table("shipments")

lineas = items.merge(products[["product_id", "cost"]], on="product_id").assign(
    ing=lambda d: d["quantity"] * d["unit_price"], mg=lambda d: d["quantity"] * (d["unit_price"] - d["cost"])
)
por_pedido = lineas.groupby("order_id")[["ing", "mg"]].sum()
todos = orders.join(por_pedido, on="order_id").assign(anio=lambda d: d["order_date"].dt.year)
retraso = (shipments["actual_date"] - shipments["promised_date"]).dt.days
envios = shipments.merge(orders[["order_id", "order_date"]], on="order_id").assign(
    anio=lambda d: d["order_date"].dt.year, grave=(retraso >= 5).to_numpy()
)


def valores(anio: int) -> dict:
    t = todos[todos["anio"] == anio]
    ok = t[t["status"] != "cancelado"]
    return {
        "Ingresos netos (€)": float(ok["ing"].sum()),
        "Pedidos": float(len(ok)),
        "Clientes activos": float(ok["customer_id"].nunique()),
        "Ticket medio (€)": float(ok["ing"].sum() / len(ok)),
        "Margen sobre ingresos (%)": float(ok["mg"].sum() / ok["ing"].sum() * 100),
        "Devoluciones (%)": float((ok["status"] == "devuelto_parcial").mean() * 100),
        "Cancelaciones (%)": float((t["status"] == "cancelado").mean() * 100),
        "Envíos con retraso grave (%)": float(envios.loc[envios["anio"] == anio, "grave"].mean() * 100),
    }


def tarjeta_kpi(nombre: str, actual: float, anterior: float, tipo: str, mejor: str = "mas", umbral: float = 2.0) -> dict:
    """Tarjeta de KPI: variación (relativa % o en pp), unidad y estado verde/ambar/rojo."""
    # TODO
    ...


v24, v25 = valores(2024), valores(2025)
# KPI: (tipo, mejor, umbral)
reglas = {
    "Ingresos netos (€)": ("cantidad", "mas", 2.0),
    "Pedidos": ("cantidad", "mas", 2.0),
    "Clientes activos": ("cantidad", "mas", 2.0),
    "Ticket medio (€)": ("cantidad", "mas", 2.0),
    "Margen sobre ingresos (%)": ("tasa", "mas", 0.5),
    "Devoluciones (%)": ("tasa", "menos", 0.5),
    "Cancelaciones (%)": ("tasa", "menos", 0.5),
    "Envíos con retraso grave (%)": ("tasa", "menos", 0.5),
}
tarjetas = [tarjeta_kpi(k, v25[k], v24[k], *reglas[k]) for k in reglas]
cuadro = pd.DataFrame([t for t in tarjetas if isinstance(t, dict)])
print(cuadro.round(2).to_string(index=False) if len(cuadro) else "Aún no hay tarjetas: implementa tarjeta_kpi.")
