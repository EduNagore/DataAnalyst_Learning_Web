"""Tablas transaccionales: orders, order_items, returns, shipments,
inventory_snapshots.

Aquí viven tres verdades plantadas (ver docs/DATASET.md §5): el cambio de
precio regional (#6), la rotura de stock de marzo de 2026 (#10, junto con
`inventory_snapshots`) y, de forma indirecta, los retrasos de envío que
alimentan el churn de suscripción (#8, implementado en `growth.py` a
partir de los `shipments` que devuelve este módulo).
"""

import numpy as np
import pandas as pd

from .reference_data import (
    CARRIERS,
    DEVICES,
    ORDER_CHANNELS,
    ORDER_STATUS_WEIGHTS,
    ORDER_STATUSES,
    RETURN_REASONS,
)

_SEGMENT_ORDER_WEIGHT = {"nuevo": 1.0, "ocasional": 1.8, "habitual": 4.0, "vip": 8.0}
_QUANTITY_CHOICES = np.array([1, 2, 3, 4])
_QUANTITY_WEIGHTS = np.array([0.70, 0.18, 0.08, 0.04])


def build_orders(
    rng: np.random.Generator,
    n_orders: int,
    customers: pd.DataFrame,
    stores: pd.DataFrame,
    calendar: pd.DataFrame,
    online_share: float,
) -> pd.DataFrame:
    # Clientes más "pegajosos" (vip/habitual) generan más pedidos.
    cust_weights = customers["segment"].map(_SEGMENT_ORDER_WEIGHT).to_numpy()
    cust_weights = cust_weights / cust_weights.sum()
    customer_idx = rng.choice(len(customers), size=n_orders, p=cust_weights)
    customer_ids = customers["customer_id"].to_numpy()[customer_idx]
    customer_regions = customers["region"].to_numpy()[customer_idx]
    signup_dates = customers["signup_date"].to_numpy()[customer_idx]

    day_weights = calendar["demand_multiplier"].to_numpy()
    day_weights = day_weights / day_weights.sum()
    day_idx = rng.choice(len(calendar), size=n_orders, p=day_weights)
    order_dates = calendar["date"].to_numpy()[day_idx]

    # Ningún pedido antes del alta del cliente: si tocara, se reubica justo
    # después del alta (con un pequeño margen aleatorio).
    too_early = order_dates < signup_dates
    max_date = calendar["date"].to_numpy()[-1]
    beyond_calendar = np.zeros(n_orders, dtype=bool)
    if too_early.any():
        offset_days = rng.integers(0, 30, size=too_early.sum())
        order_dates = order_dates.copy()
        order_dates[too_early] = signup_dates[too_early] + offset_days.astype("timedelta64[D]")
        # Los pedidos relocalizados más allá del fin del calendario no existen en la realidad: se
        # marcan (columna `_beyond_calendar`) para que `build_lumen` los elimine al final, sin
        # alterar el resto de la generación aleatoria. Recortarlos al último día apilaba miles.
        beyond_calendar = order_dates > max_date
        order_dates = np.minimum(order_dates, max_date)

    is_sale_event = pd.Series(order_dates).isin(
        calendar.loc[calendar["is_sale_event"], "date"]
    ).to_numpy()

    channels = rng.choice(ORDER_CHANNELS, size=n_orders, p=[online_share, 1 - online_share])
    devices = np.where(
        channels == "online",
        rng.choice(DEVICES, size=n_orders, p=[0.58, 0.35, 0.07]),
        "n/a",
    )

    base_discount = rng.choice([0, 0.05, 0.10, 0.15, 0.20], size=n_orders, p=[0.5, 0.2, 0.15, 0.1, 0.05])
    sale_discount = np.where(is_sale_event, rng.choice([0.10, 0.20, 0.30], size=n_orders), 0)
    discount_pct = np.round(np.maximum(base_discount, sale_discount), 2)

    shipping_cost = np.where(
        channels == "store",
        0.0,
        rng.choice([0.0, 2.95, 4.95], size=n_orders, p=[0.4, 0.3, 0.3]),
    )

    status = rng.choice(ORDER_STATUSES, size=n_orders, p=ORDER_STATUS_WEIGHTS)

    # store_id: solo para pedidos en tienda, preferentemente en la región del cliente.
    store_ids = np.full(n_orders, None, dtype=object)
    store_mask = channels == "store"
    stores_by_region = {r: g["store_id"].to_numpy() for r, g in stores.groupby("region")}
    all_store_ids = stores["store_id"].to_numpy()
    for i in np.nonzero(store_mask)[0]:
        candidates = stores_by_region.get(customer_regions[i])
        store_ids[i] = rng.choice(candidates) if candidates is not None and len(candidates) else rng.choice(
            all_store_ids
        )

    return pd.DataFrame(
        {
            "order_id": [f"order-{i:07d}" for i in range(n_orders)],
            "customer_id": customer_ids,
            "order_date": order_dates,
            "channel": channels,
            "device": devices,
            "discount_pct": discount_pct,
            "shipping_cost": shipping_cost,
            "status": status,
            "store_id": store_ids,
            "_beyond_calendar": beyond_calendar,
        }
    )


def build_order_items(
    rng: np.random.Generator,
    orders: pd.DataFrame,
    products: pd.DataFrame,
    customers: pd.DataFrame,
    avg_items_per_order: float,
    price_change: dict,
    stockout: dict,
) -> pd.DataFrame:
    n_orders = len(orders)
    n_items_per_order = np.clip(rng.poisson(avg_items_per_order, size=n_orders), 1, None)
    n_items_total = int(n_items_per_order.sum())

    order_id_rep = np.repeat(orders["order_id"].to_numpy(), n_items_per_order)
    order_date_rep = np.repeat(orders["order_date"].to_numpy(), n_items_per_order)
    discount_rep = np.repeat(orders["discount_pct"].to_numpy(), n_items_per_order)
    customer_id_rep = np.repeat(orders["customer_id"].to_numpy(), n_items_per_order)

    customer_region = customers.set_index("customer_id")["region"]
    region_rep = customer_region.reindex(customer_id_rep).to_numpy()

    product_idx = rng.integers(0, len(products), size=n_items_total)
    top_category_ids = products["top_category_id"].to_numpy()

    # --- Verdad plantada: rotura de stock (categoría objetivo, ventana fija) ---
    stockout_start = pd.Timestamp(stockout["start"])
    stockout_end = pd.Timestamp(stockout["end"])
    in_stockout_window = (order_date_rep >= stockout_start.to_numpy()) & (
        order_date_rep <= stockout_end.to_numpy()
    )
    stockout_top_id = _top_category_id(products, stockout["category"])
    is_stockout_category = top_category_ids[product_idx] == stockout_top_id
    suppress = in_stockout_window & is_stockout_category & (
        rng.random(n_items_total) < stockout["suppression"]
    )
    if suppress.any():
        non_target_mask = top_category_ids != stockout_top_id
        replacement_pool = np.nonzero(non_target_mask)[0]
        product_idx[suppress] = rng.choice(replacement_pool, size=suppress.sum())

    product_ids = products["product_id"].to_numpy()[product_idx]
    base_prices = products["price"].to_numpy()[product_idx]

    # --- Verdad plantada: subida de precio regional en una categoría, en una fecha fija ---
    price_change_date = pd.Timestamp(price_change["date"]).to_numpy()
    price_change_top_id = _top_category_id(products, price_change["category"])
    affected = (
        (region_rep == price_change["region"])
        & (top_category_ids[product_idx] == price_change_top_id)
        & (order_date_rep >= price_change_date)
    )
    price_multiplier = np.where(affected, 1 + price_change["pct_increase"], 1.0)

    noise = rng.uniform(0.97, 1.03, size=n_items_total)
    unit_price = np.round(base_prices * price_multiplier * noise * (1 - discount_rep), 2)

    quantity = rng.choice(_QUANTITY_CHOICES, size=n_items_total, p=_QUANTITY_WEIGHTS)

    return pd.DataFrame(
        {
            "order_item_id": [f"item-{i:08d}" for i in range(n_items_total)],
            "order_id": order_id_rep,
            "product_id": product_ids,
            "quantity": quantity,
            "unit_price": unit_price,
        }
    )


def _top_category_id(products: pd.DataFrame, top_category_name: str) -> str:
    """Resuelve el id de nivel superior (p.ej. 'cat-00') a partir del nombre,
    usando el prefijo compartido por todas las subcategorías de ese
    producto en `products.category_id` (formato 'cat-NN-M')."""
    # Los ids de subcategoría comparten prefijo "cat-NN" con su padre; como
    # aquí solo tenemos `products` (no el árbol de categorías), resolvemos
    # por convención de nombres pasada desde el builder de categorías.
    from .reference_data import CATEGORY_TREE

    top_names = list(CATEGORY_TREE.keys())
    top_idx = top_names.index(top_category_name)
    return f"cat-{top_idx:02d}"


def build_returns(
    rng: np.random.Generator, order_items: pd.DataFrame, orders: pd.DataFrame, returns_rate: float
) -> pd.DataFrame:
    n_items = len(order_items)
    is_returned = rng.random(n_items) < returns_rate
    returned = order_items.loc[is_returned, ["order_item_id", "order_id"]].reset_index(drop=True)

    order_date = orders.set_index("order_id")["order_date"]
    base_dates = order_date.reindex(returned["order_id"]).to_numpy()
    delay_days = rng.integers(2, 31, size=len(returned))
    return_dates = base_dates + delay_days.astype("timedelta64[D]")

    reasons = rng.choice(RETURN_REASONS, size=len(returned))

    return pd.DataFrame(
        {
            "return_id": [f"ret-{i:06d}" for i in range(len(returned))],
            "order_item_id": returned["order_item_id"],
            "return_date": return_dates,
            "reason": reasons,
        }
    )


def build_shipments(
    rng: np.random.Generator, orders: pd.DataFrame, delay_threshold_days: int
) -> pd.DataFrame:
    online = orders[orders["channel"] == "online"].reset_index(drop=True)
    n = len(online)

    prep_days = rng.integers(1, 3, size=n)
    transit_days = rng.integers(1, 4, size=n)
    promised_date = online["order_date"].to_numpy() + (prep_days + transit_days).astype(
        "timedelta64[D]"
    )

    # La mayoría llega a tiempo o antes; una cola de retrasos (algunos
    # graves) alimenta la verdad plantada de churn en growth.py.
    on_time = rng.random(n) < 0.82
    delay_days = np.where(
        on_time,
        rng.integers(-1, 1, size=n),
        rng.integers(1, delay_threshold_days + 6, size=n),
    )
    actual_date = promised_date + delay_days.astype("timedelta64[D]")

    carriers = rng.choice(CARRIERS, size=n)

    return pd.DataFrame(
        {
            "shipment_id": [f"ship-{i:07d}" for i in range(n)],
            "order_id": online["order_id"].to_numpy(),
            "promised_date": promised_date,
            "actual_date": actual_date,
            "carrier": carriers,
        }
    )


def build_inventory_snapshots(
    rng: np.random.Generator,
    products: pd.DataFrame,
    calendar: pd.DataFrame,
    n_locations: int,
    stockout: dict,
) -> pd.DataFrame:
    weekly_dates = calendar.loc[calendar["date"].dt.weekday == 0, "date"].reset_index(drop=True)
    location_ids = [f"dc-{i:02d}" for i in range(n_locations)]

    n_products = len(products)
    n_weeks = len(weekly_dates)

    # Nivel base de stock por producto y almacén (algunos productos rotan
    # mucho más que otros).
    base_stock = rng.integers(20, 400, size=(n_products, n_locations))

    product_ids = products["product_id"].to_numpy()
    target_category = _top_category_id(products, stockout["category"])
    is_target = products["top_category_id"].to_numpy() == target_category
    stockout_start = pd.Timestamp(stockout["start"])
    stockout_end = pd.Timestamp(stockout["end"])
    in_window = (weekly_dates >= stockout_start) & (weekly_dates <= stockout_end)

    dates_rep = np.repeat(weekly_dates.to_numpy(), n_products * n_locations)
    products_rep = np.tile(np.repeat(product_ids, n_locations), n_weeks)
    locations_rep = np.tile(location_ids, n_products * n_weeks)
    is_target_rep = np.tile(np.repeat(is_target, n_locations), n_weeks)

    noise = rng.uniform(0.7, 1.3, size=n_products * n_locations * n_weeks)
    stock_qty = np.tile(base_stock.flatten(), n_weeks) * noise
    in_window_rep = np.repeat(in_window.to_numpy(), n_products * n_locations)
    stock_qty = np.where(in_window_rep & is_target_rep, rng.integers(0, 3, size=stock_qty.size), stock_qty)
    stock_qty = np.round(np.clip(stock_qty, 0, None)).astype(int)

    return pd.DataFrame(
        {
            "snapshot_date": dates_rep,
            "product_id": products_rep,
            "location_id": locations_rep,
            "stock_qty": stock_qty,
        }
    )
