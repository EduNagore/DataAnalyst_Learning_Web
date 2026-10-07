"""`lumen_raw/`: copias "sucias" de customers, orders y events para los
labs de limpieza de datos (ver docs/DATASET.md §4). Los problemas son
intencionados y están documentados aquí, no son bugs del generador.
"""

import numpy as np
import pandas as pd

_SPANISH_MONTHS = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]  # fmt: skip


def _mangle_date(d: pd.Timestamp, variant: int) -> str:
    if variant == 0:
        return d.strftime("%Y-%m-%d")
    if variant == 1:
        return d.strftime("%d/%m/%Y")
    return f"{d.day} de {_SPANISH_MONTHS[d.month - 1]} de {d.year}"


def _mangle_text(value: str, variant: int) -> str:
    if variant == 0:
        return value.upper()
    if variant == 1:
        return value.lower()
    if variant == 2:
        return f" {value} "
    return value


def corrupt_customers(rng: np.random.Generator, customers: pd.DataFrame, n_sample: int) -> pd.DataFrame:
    seed = int(rng.integers(0, 2**31))
    sample = customers.sample(n=min(n_sample, len(customers)), random_state=seed).copy()

    text_variant = rng.integers(0, 4, size=len(sample))
    sample["region"] = [
        _mangle_text(r, v) for r, v in zip(sample["region"], text_variant, strict=False)
    ]

    date_variant = rng.integers(0, 3, size=len(sample))
    sample["signup_date"] = [
        _mangle_date(d, v) for d, v in zip(sample["signup_date"], date_variant, strict=False)
    ]

    # Nulos donde en la tabla limpia nunca los hay.
    null_mask = rng.random(len(sample)) < 0.06
    sample.loc[null_mask, "province"] = None

    sample["marketing_consent"] = sample["marketing_consent"].astype(str)

    # Duplicados exactos y casi-duplicados (mismo id, un espacio de más en la región).
    dup_idx = rng.choice(len(sample), size=max(int(len(sample) * 0.03), 1), replace=False)
    near_dup = sample.iloc[dup_idx].copy()
    near_dup["region"] = near_dup["region"].astype(str) + " "
    sample = pd.concat([sample, sample.iloc[dup_idx], near_dup], ignore_index=True)

    return sample.sample(frac=1, random_state=int(rng.integers(0, 2**31))).reset_index(drop=True)


def corrupt_orders(
    rng: np.random.Generator, orders: pd.DataFrame, n_sample: int, fake_customer_ids: list[str]
) -> pd.DataFrame:
    sample = orders.sample(n=min(n_sample, len(orders)), random_state=int(rng.integers(0, 2**31))).copy()

    date_variant = rng.integers(0, 3, size=len(sample))
    sample["order_date"] = [
        _mangle_date(d, v) for d, v in zip(sample["order_date"], date_variant, strict=False)
    ]

    # Importes con coma decimal, como string (Excel/es-ES).
    sample["shipping_cost"] = sample["shipping_cost"].map(lambda v: f"{v:.2f}".replace(".", ","))

    # IDs huérfanos: unos pocos clientes que no existen en ninguna copia de customers.
    orphan_mask = rng.random(len(sample)) < 0.02
    n_orphans = int(orphan_mask.sum())
    if n_orphans:
        sample.loc[orphan_mask, "customer_id"] = rng.choice(fake_customer_ids, size=n_orphans)

    null_mask = rng.random(len(sample)) < 0.04
    sample.loc[null_mask, "store_id"] = None

    dup_idx = rng.choice(len(sample), size=max(int(len(sample) * 0.02), 1), replace=False)
    sample = pd.concat([sample, sample.iloc[dup_idx]], ignore_index=True)

    return sample.sample(frac=1, random_state=int(rng.integers(0, 2**31))).reset_index(drop=True)


def corrupt_events(rng: np.random.Generator, events: pd.DataFrame, n_sample: int) -> pd.DataFrame:
    sample = events.sample(n=min(n_sample, len(events)), random_state=int(rng.integers(0, 2**31))).copy()

    null_mask = rng.random(len(sample)) < 0.03
    sample.loc[null_mask, "app_version"] = None

    dup_idx = rng.choice(len(sample), size=max(int(len(sample) * 0.015), 1), replace=False)
    sample = pd.concat([sample, sample.iloc[dup_idx]], ignore_index=True)

    return sample.sample(frac=1, random_state=int(rng.integers(0, 2**31))).reset_index(drop=True)
