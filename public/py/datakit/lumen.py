"""Construcciones auxiliares sobre las tablas de Lumen que se reutilizan en varios labs."""

import numpy as np
import pandas as pd


def panel_bajas(
    subscriptions: pd.DataFrame,
    shipments: pd.DataFrame,
    orders: pd.DataFrame,
    fin: str = "2026-06-30",
) -> pd.DataFrame:
    """Panel suscripción-mes de Lumen+ (una fila por cada revisión de 30 días hasta la baja o el fin de datos).

    Columnas: las de `subscriptions` más `k` (nº de revisión), `t` (fecha de la revisión),
    `cancela` (1 si la suscripción se da de baja en esa revisión) y `expuesto` (1 si hubo un
    retraso grave de envío, de 5 días o más, en los 30 días previos a la revisión).
    """
    fin = pd.Timestamp(fin)
    s = subscriptions.copy()
    s["n_rev"] = ((fin - s["started_at"]).dt.days - 1) // 30
    s = s[s["n_rev"] >= 1].copy()
    s["k_baja"] = np.where(
        s["cancelled_at"].notna(), (s["cancelled_at"] - s["started_at"]).dt.days // 30, 10**9
    )
    s["n_uso"] = np.minimum(s["n_rev"], s["k_baja"]).astype(int)
    panel = s.loc[s.index.repeat(s["n_uso"])].copy()
    panel["k"] = panel.groupby("subscription_id").cumcount() + 1
    panel["t"] = panel["started_at"] + pd.to_timedelta(panel["k"] * 30, unit="D")
    panel["cancela"] = (panel["k"] == panel["k_baja"]).astype(int)

    graves = shipments.merge(orders[["order_id", "customer_id"]], on="order_id")
    graves = graves[(graves["actual_date"] - graves["promised_date"]).dt.days >= 5][
        ["customer_id", "actual_date"]
    ]
    cruce = panel[["subscription_id", "customer_id", "t"]].merge(graves, on="customer_id", how="left")
    cruce["impacto"] = (cruce["actual_date"] >= cruce["t"] - pd.Timedelta(days=30)) & (
        cruce["actual_date"] <= cruce["t"]
    )
    expuesto = cruce.groupby(["subscription_id", "t"])["impacto"].any()
    panel = panel.set_index(["subscription_id", "t"])
    panel["expuesto"] = expuesto.reindex(panel.index).fillna(False).astype(int).to_numpy()
    return panel.reset_index().drop(columns=["n_rev", "k_baja", "n_uso"])
