"""Orquestación: construye todas las tablas de Lumen para una semilla y una
escala dadas, en el orden correcto de dependencias (ver docs/DATASET.md).
"""

from pathlib import Path

import pandas as pd

from . import behavior, dimensions, growth, raw_variant, transactions
from . import calendar as calendar_mod
from .io_utils import compute_checksums, total_size_mb, write_csv, write_parquet
from .rng import sub_rng
from .schema_doc import SCHEMA

# Qué claves de `sizes` se escalan por `scale.variant` (volumen de datos) y
# cuáles se mantienen fijas (estructura: nº de categorías, de ubicaciones
# de almacén, de experimentos...) o son tasas (nunca se escalan).
_SCALED_SIZE_KEYS = {
    "customers",
    "products",
    "stores",
    "orders",
    "web_sessions",
    "subscriptions",
    "support_tickets",
    "support_tickets_labeled_sample",
    "experiment_assignment_customers",
}


def _scaled_sizes(sizes: dict, scale: float) -> dict:
    scaled = dict(sizes)
    for key in _SCALED_SIZE_KEYS:
        scaled[key] = max(1, round(sizes[key] * scale))
    return scaled


def _check_schema(name: str, df: pd.DataFrame) -> None:
    expected = set(SCHEMA[name]["columns"].keys())
    actual = set(df.columns)
    if expected != actual:
        missing = expected - actual
        extra = actual - expected
        raise ValueError(
            f"Esquema desincronizado en '{name}': faltan {missing or '—'}, "
            f"sobran {extra or '—'} (ver lumen/schema_doc.py)."
        )


def build_lumen(config: dict, seed: int, scale: float) -> dict[str, pd.DataFrame]:
    sizes = _scaled_sizes(config["sizes"], scale)
    planted = config["planted_truths"]
    date_start, date_end = config["date_start"], config["date_end"]

    cal = calendar_mod.build_calendar(date_start, date_end, config["sale_events"])

    categories = dimensions.build_categories()
    products = dimensions.build_products(sub_rng(seed, "products"), sizes["products"], categories)
    stores = dimensions.build_stores(sub_rng(seed, "stores"), sizes["stores"], date_start)
    customers = dimensions.build_customers(
        sub_rng(seed, "customers"), sizes["customers"], date_start, date_end
    )

    orders = transactions.build_orders(
        sub_rng(seed, "orders"), sizes["orders"], customers, stores, cal, sizes["online_share"]
    )
    order_items = transactions.build_order_items(
        sub_rng(seed, "order_items"),
        orders,
        products,
        customers,
        sizes["avg_items_per_order"],
        planted["price_change"],
        planted["stockout"],
    )
    returns = transactions.build_returns(
        sub_rng(seed, "returns"), order_items, orders, sizes["returns_rate"]
    )
    shipments = transactions.build_shipments(
        sub_rng(seed, "shipments"), orders, planted["shipment_delay_churn"]["delay_threshold_days"]
    )
    inventory_snapshots = transactions.build_inventory_snapshots(
        sub_rng(seed, "inventory"), products, cal, sizes["inventory_locations"], planted["stockout"]
    )

    web_sessions = behavior.build_web_sessions(
        sub_rng(seed, "web_sessions"), sizes["web_sessions"], customers, cal, planted["simpson"]
    )
    events = behavior.build_events(sub_rng(seed, "events"), web_sessions, planted["app_bug_duplicate_events"])

    campaigns = behavior.build_campaigns(sub_rng(seed, "campaigns"), sizes["campaigns"], cal)
    marketing_spend = behavior.build_marketing_spend(sub_rng(seed, "marketing_spend"), cal, campaigns)

    experiments = growth.build_experiments(sub_rng(seed, "experiments"), cal, planted)
    experiment_assignments = growth.build_experiment_assignments(
        sub_rng(seed, "experiment_assignments"),
        experiments,
        customers,
        planted,
        sizes["experiment_assignment_customers"],
    )
    experiment_metrics = growth.build_experiment_metrics(
        sub_rng(seed, "experiment_metrics"), experiments, planted
    )

    subscriptions = growth.build_subscriptions(
        sub_rng(seed, "subscriptions"),
        sizes["subscriptions"],
        customers,
        orders,
        shipments,
        date_start,
        date_end,
        planted["shipment_delay_churn"],
    )
    support_tickets = growth.build_support_tickets(
        sub_rng(seed, "support_tickets"),
        sizes["support_tickets"],
        customers,
        date_start,
        date_end,
        planted["support_topics"],
        sizes["support_tickets_labeled_sample"],
    )

    # Pedidos que caerían después del fin del calendario: se descartan con todo lo que cuelga de ellos.
    beyond = orders["_beyond_calendar"].to_numpy()
    dropped_order_ids = set(orders.loc[beyond, "order_id"])
    orders = orders.loc[~beyond].drop(columns=["_beyond_calendar"]).reset_index(drop=True)
    dropped_item_ids = set(order_items.loc[order_items["order_id"].isin(dropped_order_ids), "order_item_id"])
    order_items = order_items.loc[~order_items["order_id"].isin(dropped_order_ids)].reset_index(drop=True)
    returns = returns.loc[~returns["order_item_id"].isin(dropped_item_ids)].reset_index(drop=True)
    shipments = shipments.loc[~shipments["order_id"].isin(dropped_order_ids)].reset_index(drop=True)

    tables = {
        "customers": customers,
        "categories": categories,
        "products": products.drop(columns=["top_category_id"]),
        "stores": stores,
        "orders": orders,
        "order_items": order_items,
        "returns": returns,
        "shipments": shipments,
        "inventory_snapshots": inventory_snapshots,
        "web_sessions": web_sessions.drop(columns=["_reached_stage"]),
        "events": events,
        "marketing_spend": marketing_spend,
        "campaigns": campaigns,
        "experiments": experiments,
        "experiment_assignments": experiment_assignments,
        "experiment_metrics": experiment_metrics,
        "subscriptions": subscriptions,
        "support_tickets": support_tickets,
        "calendar": cal,
    }
    for name, df in tables.items():
        _check_schema(name, df)
    return tables


def build_raw_variant(config: dict, seed: int, tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    rng = sub_rng(seed, "raw_variant")
    all_customer_ids = tables["customers"]["customer_id"].tolist()
    fake_ids = [f"cust-raw-fake-{i:03d}" for i in range(20)]
    return {
        "customers": raw_variant.corrupt_customers(rng, tables["customers"], n_sample=5000),
        "orders": raw_variant.corrupt_orders(
            rng, tables["orders"], n_sample=8000, fake_customer_ids=fake_ids + all_customer_ids[:1]
        ),
        "events": raw_variant.corrupt_events(rng, tables["events"], n_sample=10000),
    }


def write_all(
    output_root: Path,
    main_tables: dict[str, pd.DataFrame],
    variant_tables: dict[str, pd.DataFrame],
    raw_tables: dict[str, pd.DataFrame],
    extra_tables: dict[str, pd.DataFrame],
) -> dict:
    for name, df in main_tables.items():
        write_parquet(df, output_root / "lumen" / f"{name}.parquet")
    for name, df in variant_tables.items():
        write_parquet(df, output_root / "lumen_variant" / f"{name}.parquet")
    for name, df in raw_tables.items():
        write_csv(df, output_root / "lumen_raw" / f"{name}.csv")
    for name, df in extra_tables.items():
        write_csv(df, output_root / "extra" / f"{name}.csv")

    checksums = compute_checksums(output_root)
    size_mb = total_size_mb(output_root)
    return {"checksums": checksums, "size_mb": size_mb}
