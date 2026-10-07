"""Tablas de dimensión: categories, products, stores, customers."""

import numpy as np
import pandas as pd

from .reference_data import (
    ACQUISITION_CHANNELS,
    BRANDS,
    CATEGORY_TREE,
    CUSTOMER_SEGMENT_WEIGHTS,
    CUSTOMER_SEGMENTS,
    REGION_NAMES,
    REGION_TO_PROVINCE,
    REGION_WEIGHTS,
)

# Rango de precio base (EUR) por categoría de nivel superior; da variedad
# realista entre, p.ej., Alimentación (barato) y Electrónica (caro).
_PRICE_RANGES = {
    "Electrónica": (25, 900),
    "Hogar": (8, 350),
    "Moda": (10, 150),
    "Deporte": (12, 200),
    "Belleza": (4, 60),
    "Alimentación": (1, 18),
    "Juguetes y bebé": (6, 120),
    "Papelería y oficina": (1, 80),
}


def build_categories() -> pd.DataFrame:
    rows = []
    for top_idx, (top_name, subs) in enumerate(CATEGORY_TREE.items()):
        top_id = f"cat-{top_idx:02d}"
        rows.append({"category_id": top_id, "parent_category_id": None, "name": top_name})
        for sub_idx, sub_name in enumerate(subs):
            rows.append(
                {
                    "category_id": f"{top_id}-{sub_idx}",
                    "parent_category_id": top_id,
                    "name": sub_name,
                }
            )
    return pd.DataFrame(rows)


def build_products(rng: np.random.Generator, n_products: int, categories: pd.DataFrame) -> pd.DataFrame:
    leaf_categories = categories[categories["parent_category_id"].notna()].reset_index(drop=True)
    top_name_by_id = categories.set_index("category_id")["name"].to_dict()
    parent_by_leaf = leaf_categories["parent_category_id"].to_numpy()

    leaf_idx = rng.integers(0, len(leaf_categories), size=n_products)
    category_ids = leaf_categories["category_id"].to_numpy()[leaf_idx]
    top_ids = parent_by_leaf[leaf_idx]
    top_names = np.array([top_name_by_id[t] for t in top_ids])

    prices = np.empty(n_products)
    for top_name, (lo, hi) in _PRICE_RANGES.items():
        mask = top_names == top_name
        # Log-normal truncada al rango: da una cola larga de productos caros
        # dentro de cada categoría, más realista que uniforme.
        n = mask.sum()
        if n == 0:
            continue
        raw = rng.lognormal(mean=np.log((lo + hi) / 3), sigma=0.5, size=n)
        prices[mask] = np.clip(raw, lo, hi)
    prices = np.round(prices, 2)

    margin = rng.uniform(0.30, 0.55, size=n_products)  # margen bruto sobre el precio
    costs = np.round(prices * (1 - margin), 2)

    brands = rng.choice(BRANDS, size=n_products)
    leaf_names = leaf_categories["name"].to_numpy()[leaf_idx]
    skus = rng.integers(1000, 9999, size=n_products)
    names = [f"{leaf_names[i]} {brands[i]} {skus[i]}" for i in range(n_products)]

    return pd.DataFrame(
        {
            "product_id": [f"prod-{i:05d}" for i in range(n_products)],
            "category_id": category_ids,
            # Prefijo "cat-NN" de nivel superior, derivado del id de
            # subcategoría ("cat-NN-M"). Se usa internamente (p.ej. para
            # las verdades plantadas de transactions.py) y no se publica
            # como columna del Parquet final (ver write.py).
            "top_category_id": [c[:6] for c in category_ids],
            "name": names,
            "price": prices,
            "cost": costs,
            "brand": brands,
        }
    )


def build_stores(rng: np.random.Generator, n_stores: int, date_start: str) -> pd.DataFrame:
    weights = np.array(REGION_WEIGHTS, dtype=float)
    weights = weights / weights.sum()
    regions = rng.choice(REGION_NAMES, size=n_stores, p=weights)

    # Fecha de apertura: la mayoría de tiendas ya existían antes del periodo
    # analizado; algunas (expansión) abren durante el propio periodo.
    period_start = pd.Timestamp(date_start)
    earliest_opening = period_start - pd.Timedelta(days=365 * 8)
    days_before = rng.integers(0, (period_start - earliest_opening).days, size=n_stores)
    opened = [earliest_opening + pd.Timedelta(days=int(d)) for d in days_before]
    # ~15% abren durante el periodo de análisis (crecimiento de la red).
    expansion_mask = rng.random(n_stores) < 0.15
    period_end = period_start + pd.Timedelta(days=365 * 2)
    days_into_period = rng.integers(0, (period_end - period_start).days, size=expansion_mask.sum())
    expansion_dates = [period_start + pd.Timedelta(days=int(d)) for d in days_into_period]
    opened_arr = np.array(opened, dtype="datetime64[ns]")
    opened_arr[expansion_mask] = expansion_dates

    # Ciudades: la capital representativa de la región, con sufijo si hay
    # más de una tienda en la misma región.
    cities = []
    seen_count: dict[str, int] = {}
    for region in regions:
        base_city = REGION_TO_PROVINCE[region]
        seen_count[base_city] = seen_count.get(base_city, 0) + 1
        suffix = "" if seen_count[base_city] == 1 else f" {seen_count[base_city]}"
        cities.append(f"{base_city}{suffix}")

    size_m2 = rng.integers(300, 2500, size=n_stores)

    return pd.DataFrame(
        {
            "store_id": [f"store-{i:02d}" for i in range(n_stores)],
            "city": cities,
            "region": regions,
            "size_m2": size_m2,
            "opened_date": pd.to_datetime(opened_arr),
        }
    )


def build_customers(
    rng: np.random.Generator, n_customers: int, date_start: str, date_end: str
) -> pd.DataFrame:
    start = pd.Timestamp(date_start)
    end = pd.Timestamp(date_end)
    total_days = (end - start).days

    # Más altas hacia el final del periodo (la empresa crece): rampa lineal
    # de probabilidad en vez de uniforme.
    day_offsets = np.arange(total_days + 1)
    weights = 1 + 2 * (day_offsets / total_days)
    weights = weights / weights.sum()
    signup_offsets = rng.choice(day_offsets, size=n_customers, p=weights)
    signup_dates = start + pd.to_timedelta(signup_offsets, unit="D")

    region_weights = np.array(REGION_WEIGHTS, dtype=float)
    region_weights = region_weights / region_weights.sum()
    regions = rng.choice(REGION_NAMES, size=n_customers, p=region_weights)
    provinces = np.array([REGION_TO_PROVINCE[r] for r in regions])

    channel_weights = np.array([0.18, 0.14, 0.12, 0.08, 0.28, 0.20])  # ver ACQUISITION_CHANNELS
    acquisition = rng.choice(ACQUISITION_CHANNELS, size=n_customers, p=channel_weights)

    segments = rng.choice(CUSTOMER_SEGMENTS, size=n_customers, p=CUSTOMER_SEGMENT_WEIGHTS)
    consent = rng.random(n_customers) < 0.70

    return pd.DataFrame(
        {
            "customer_id": [f"cust-{i:06d}" for i in range(n_customers)],
            "signup_date": signup_dates,
            "acquisition_channel": acquisition,
            "region": regions,
            "province": provinces,
            "segment": segments,
            "marketing_consent": consent,
        }
    )
