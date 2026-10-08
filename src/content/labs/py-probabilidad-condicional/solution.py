import pandas as pd
from datakit.data import load_table
from scipy.stats import chi2_contingency

orders = load_table("orders")
items = load_table("order_items")
returns = load_table("returns")
products = load_table("products")
categories = load_table("categories").set_index("category_id")
shipments = load_table("shipments")
subscriptions = load_table("subscriptions")

# Líneas de pedidos no cancelados, con si se devolvió y si son de Electrónica.
padre = categories["parent_category_id"].fillna(categories.index.to_series())
nombre_cat = padre.map(categories["name"])
lineas = (
    items.merge(orders[orders["status"] != "cancelado"][["order_id"]], on="order_id")
    .merge(products[["product_id", "category_id"]], on="product_id")
    .assign(
        devuelta=lambda d: d["order_item_id"].isin(returns["order_item_id"]),
        es_electronica=lambda d: d["category_id"].map(nombre_cat) == "Electrónica",
    )[["devuelta", "es_electronica"]]
)

# Suscripciones: ¿ha sufrido el cliente algún envío con >= 5 días de retraso? ¿ha cancelado?
retraso = (shipments["actual_date"] - shipments["promised_date"]).dt.days
con_retraso = shipments[retraso >= 5].merge(orders[["order_id", "customer_id"]], on="order_id")["customer_id"].unique()
subs = subscriptions.assign(
    retraso_grave=lambda d: d["customer_id"].isin(con_retraso), cancela=lambda d: d["cancelled_at"].notna()
)[["retraso_grave", "cancela"]]
print(len(lineas), len(subs))


def p_condicional(df: pd.DataFrame, a: str, b: str) -> float:
    """P(A|B) en % (2 decimales): porcentaje de a entre las filas con b verdadero."""
    return round(float(df.loc[df[b], a].mean() * 100), 2)


def bayes(p_b_dado_a: float, p_a: float, p_b: float) -> float:
    """P(A|B) = P(B|A) * P(A) / P(B), con 3 decimales."""
    return round(p_b_dado_a * p_a / p_b, 3)


def independientes(df: pd.DataFrame, a: str, b: str, alpha: float = 0.01) -> bool:
    """True si la prueba chi-cuadrado no rechaza la independencia entre a y b."""
    p = chi2_contingency(pd.crosstab(df[a], df[b]))[1]
    return bool(p > alpha)


print(p_condicional(subs, "cancela", "retraso_grave"), p_condicional(subs, "retraso_grave", "cancela"))
print(bayes(0.595, 0.565, 0.534))
print(independientes(lineas, "devuelta", "es_electronica"), independientes(subs, "cancela", "retraso_grave"))
