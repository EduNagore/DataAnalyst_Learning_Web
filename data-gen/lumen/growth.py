"""Tablas de crecimiento y soporte: experiments, experiment_assignments,
experiment_metrics, subscriptions, support_tickets.

Cuatro verdades plantadas (ver docs/DATASET.md §5): lift real de
experimento (#3), SRM (#4), base para CUPED (#5, ver nota más abajo),
incrementalidad de campaña vs atribución last-click (#9), y churn de
suscripción por retrasos de envío (#8).
"""

import numpy as np
import pandas as pd

from .reference_data import SUBSCRIPTION_PLANS

_GENERIC_EXPERIMENT_NAMES = [
    "Rediseño de la ficha de producto",
    "Nuevo algoritmo de envío gratis",
    "Banner de urgencia en checkout",
    "Test de precios ancla",
    "Nuevo flujo de registro",
    "Chatbot de soporte en el carrito",
    "Recomendaciones personalizadas en email",
    "Página de categoría rediseñada",
    "Copy de notificaciones push",
    "Nuevo diseño del carrito",
    "Programa de referidos",
]
_METRIC_BASELINES = {
    "conversion_rate": (0.04, 0.09),
    "revenue_per_user": (15, 45),
    "click_through_rate": (0.02, 0.10),
    "retention_7d": (0.25, 0.45),
    "aov": (30, 85),
}


def build_experiments(rng: np.random.Generator, calendar: pd.DataFrame, planted: dict) -> pd.DataFrame:
    period_start = calendar["date"].min()
    period_end = calendar["date"].max() - pd.Timedelta(days=45)

    named = [
        (planted["experiment_lift"]["id"], "Nuevo flujo de checkout", "conversion_rate"),
        (planted["experiment_srm"]["id"], "Motor de recomendaciones v2", "click_through_rate"),
        (planted["experiment_cuped"]["id"], "Onboarding de nuevos clientes", "revenue_per_user"),
        (
            planted["experiment_campaign_incrementality"]["id"],
            "Holdout geográfico de anuncios en redes sociales",
            "revenue_per_user",
        ),
    ]

    rows = []
    for i, (exp_id, name, metric) in enumerate(named):
        start = period_start + pd.Timedelta(days=int(60 + i * 120))
        rows.append(
            {
                "experiment_id": exp_id,
                "name": name,
                "start_date": start,
                "end_date": start + pd.Timedelta(days=28),
                "primary_metric": metric,
            }
        )

    total_days = (period_end - period_start).days
    for i, name in enumerate(_GENERIC_EXPERIMENT_NAMES):
        start = period_start + pd.Timedelta(days=int(rng.integers(0, total_days)))
        duration = int(rng.integers(14, 46))
        metric = rng.choice(list(_METRIC_BASELINES.keys()))
        rows.append(
            {
                "experiment_id": f"exp-generic-{i:02d}",
                "name": name,
                "start_date": start,
                "end_date": start + pd.Timedelta(days=duration),
                "primary_metric": metric,
            }
        )

    return pd.DataFrame(rows)


def build_experiment_assignments(
    rng: np.random.Generator,
    experiments: pd.DataFrame,
    customers: pd.DataFrame,
    planted: dict,
    n_per_experiment: int,
) -> pd.DataFrame:
    srm_id = planted["experiment_srm"]["id"]
    srm_split = planted["experiment_srm"]["actual_split"]

    rows = []
    for exp_id in experiments["experiment_id"]:
        pool_size = min(n_per_experiment, len(customers))
        idx = rng.choice(len(customers), size=pool_size, replace=False)
        customer_ids = customers["customer_id"].to_numpy()[idx]

        split = srm_split if exp_id == srm_id else [0.5, 0.5]
        variant = rng.choice(["control", "tratamiento"], size=pool_size, p=split)

        rows.append(
            pd.DataFrame({"experiment_id": exp_id, "customer_id": customer_ids, "variant": variant})
        )
    return pd.concat(rows, ignore_index=True)


def build_experiment_metrics(
    rng: np.random.Generator, experiments: pd.DataFrame, planted: dict
) -> pd.DataFrame:
    lift_id = planted["experiment_lift"]["id"]
    true_lift = planted["experiment_lift"]["true_lift_pct"]
    camp_id = planted["experiment_campaign_incrementality"]["id"]
    attributed_lift = planted["experiment_campaign_incrementality"]["attributed_lift_pct"]
    true_camp_lift = planted["experiment_campaign_incrementality"]["true_lift_pct"]

    rows = []
    for _, exp in experiments.iterrows():
        dates = pd.date_range(exp["start_date"], exp["end_date"], freq="D")
        lo, hi = _METRIC_BASELINES[exp["primary_metric"]]
        baseline = rng.uniform(lo, hi)
        noise_control = rng.normal(0, baseline * 0.06, size=len(dates))
        noise_treat = rng.normal(0, baseline * 0.06, size=len(dates))

        # Solo dos experimentos tienen un efecto causal real garantizado en
        # su métrica principal (el resto, incluidos los genéricos, son
        # resultados nulos, como la mayoría de experimentos en la vida real):
        # el de lift directo, y el holdout geográfico (cuyo efecto real es
        # mucho menor que lo que luego "verá" la atribución last-click).
        if exp["experiment_id"] == lift_id:
            treat_lift = true_lift
        elif exp["experiment_id"] == camp_id:
            treat_lift = true_camp_lift
        else:
            treat_lift = 0.0

        control_values = baseline + noise_control
        treat_values = baseline * (1 + treat_lift) + noise_treat

        rows.append(
            pd.DataFrame(
                {
                    "experiment_id": exp["experiment_id"],
                    "date": dates,
                    "variant": "control",
                    "metric_name": exp["primary_metric"],
                    "value": np.round(control_values, 4),
                }
            )
        )
        rows.append(
            pd.DataFrame(
                {
                    "experiment_id": exp["experiment_id"],
                    "date": dates,
                    "variant": "tratamiento",
                    "metric_name": exp["primary_metric"],
                    "value": np.round(treat_values, 4),
                }
            )
        )

        # --- Verdad plantada: incrementalidad de campaña vs atribución last-click ---
        if exp["experiment_id"] == camp_id:
            base_rev = rng.uniform(20, 40)
            rows.append(
                pd.DataFrame(
                    {
                        "experiment_id": exp["experiment_id"],
                        "date": dates,
                        "variant": "control",
                        "metric_name": "last_click_attributed_revenue_per_user",
                        "value": np.round(base_rev + rng.normal(0, base_rev * 0.05, size=len(dates)), 2),
                    }
                )
            )
            rows.append(
                pd.DataFrame(
                    {
                        "experiment_id": exp["experiment_id"],
                        "date": dates,
                        "variant": "tratamiento",
                        "metric_name": "last_click_attributed_revenue_per_user",
                        "value": np.round(
                            base_rev * (1 + attributed_lift)
                            + rng.normal(0, base_rev * 0.05, size=len(dates)),
                            2,
                        ),
                    }
                )
            )

    return pd.concat(rows, ignore_index=True)


def build_subscriptions(
    rng: np.random.Generator,
    n_subscriptions: int,
    customers: pd.DataFrame,
    orders: pd.DataFrame,
    shipments: pd.DataFrame,
    date_start: str,
    date_end: str,
    shipment_delay_churn: dict,
) -> pd.DataFrame:
    # Precalcula, por cliente, las fechas de envíos con retraso grave.
    ship = shipments.merge(orders[["order_id", "customer_id"]], on="order_id")
    ship["delay_days"] = (ship["actual_date"] - ship["promised_date"]).dt.days
    severe = ship[ship["delay_days"] >= shipment_delay_churn["delay_threshold_days"]]
    severe_dates_by_customer: dict[str, np.ndarray] = {
        cust: np.sort(group["actual_date"].to_numpy())
        for cust, group in severe.groupby("customer_id")
    }

    weights = customers["segment"].map(
        {"nuevo": 0.5, "ocasional": 1.0, "habitual": 2.5, "vip": 4.0}
    ).to_numpy()
    weights = weights / weights.sum()
    cust_idx = rng.choice(len(customers), size=n_subscriptions, replace=False, p=weights)
    sub_customers = customers["customer_id"].to_numpy()[cust_idx]

    start = pd.Timestamp(date_start)
    end = pd.Timestamp(date_end)
    total_days = (end - start).days
    start_offsets = rng.integers(0, max(total_days - 30, 1), size=n_subscriptions)
    started_at = start + pd.to_timedelta(start_offsets, unit="D")

    plans = rng.choice(SUBSCRIPTION_PLANS, size=n_subscriptions, p=[0.7, 0.3])
    mrr = np.where(
        plans == "mensual",
        np.round(rng.uniform(9, 29, size=n_subscriptions), 2),
        np.round(rng.uniform(7, 22, size=n_subscriptions), 2),
    )

    cancelled_at = _simulate_cancellations(
        rng, sub_customers, started_at, end, severe_dates_by_customer, shipment_delay_churn
    )

    return pd.DataFrame(
        {
            "subscription_id": [f"subs-{i:06d}" for i in range(n_subscriptions)],
            "customer_id": sub_customers,
            "plan": plans,
            "started_at": started_at,
            "cancelled_at": cancelled_at,
            "mrr_eur": mrr,
        }
    )


def _simulate_cancellations(
    rng: np.random.Generator,
    sub_customers: np.ndarray,
    started_at: pd.DatetimeIndex,
    period_end: pd.Timestamp,
    severe_dates_by_customer: dict,
    shipment_delay_churn: dict,
) -> list:
    base_monthly_churn = 0.035
    extra = shipment_delay_churn["extra_churn_prob"]
    results: list = []
    one_month = pd.Timedelta(days=30)
    lookback = pd.Timedelta(days=30)

    for cust, t0 in zip(sub_customers, started_at, strict=True):
        t = t0
        delays = severe_dates_by_customer.get(cust)
        cancelled = None
        while True:
            t = t + one_month
            if t >= period_end:
                break
            churn_prob = base_monthly_churn
            if delays is not None and np.any((delays >= (t - lookback)) & (delays <= t)):
                churn_prob += extra
            if rng.random() < churn_prob:
                cancelled = t
                break
        results.append(cancelled)
    return results


def build_support_tickets(
    rng: np.random.Generator,
    n_tickets: int,
    customers: pd.DataFrame,
    date_start: str,
    date_end: str,
    topics: list[str],
    n_labeled: int,
) -> pd.DataFrame:
    templates: dict[str, list[str]] = {
        "envio": [
            "Mi pedido lleva {dias} días de retraso y no tengo ninguna noticia del transportista.",
            "El paquete debía llegar hace {dias} días y el seguimiento no se actualiza.",
            "¿Por qué mi envío sigue en el almacén después de {dias} días?",
            "He recibido solo parte de mi pedido, faltan artículos.",
            "La dirección de entrega era correcta pero el paquete volvió al almacén.",
        ],
        "devoluciones": [
            "Quiero devolver un producto, ¿cómo genero la etiqueta de devolución?",
            "Llevo {dias} días esperando el reembolso de mi devolución.",
            "El producto llegó defectuoso, necesito cambiarlo.",
            "He devuelto el artículo pero el estado sigue como 'pendiente'.",
            "¿Cuánto tiempo tengo para devolver un pedido de la categoría {categoria}?",
        ],
        "app": [
            "La aplicación se cierra sola al intentar pagar.",
            "No puedo iniciar sesión en la app desde la última actualización.",
            "El carrito de la app se vacía solo cada vez que lo abro.",
            "La app me ha cobrado dos veces el mismo pedido.",
            "No me llegan las notificaciones de seguimiento del pedido en la app.",
        ],
        "pagos": [
            "Me han cobrado dos veces por el mismo pedido.",
            "La tarjeta fue rechazada pero el importe se retuvo igualmente.",
            "¿Puedo pagar a plazos un pedido de la categoría {categoria}?",
            "No recibo la factura de mi última compra.",
            "El descuento del cupón no se aplicó en el pago final.",
        ],
        "producto": [
            "El producto de la categoría {categoria} no coincide con la descripción.",
            "¿Tienen disponible otra talla de este artículo?",
            "El producto llegó roto dentro de la caja.",
            "Necesito más información técnica sobre este artículo antes de comprarlo.",
            "La calidad no es la esperada para el precio pagado.",
        ],
    }

    topic_choices = rng.choice(topics, size=n_tickets)
    start = pd.Timestamp(date_start)
    end = pd.Timestamp(date_end)
    total_days = (end - start).days
    created_at = start + pd.to_timedelta(rng.integers(0, total_days, size=n_tickets), unit="D")
    cust_idx = rng.integers(0, len(customers), size=n_tickets)
    customer_ids = customers["customer_id"].to_numpy()[cust_idx]

    dias = rng.integers(2, 15, size=n_tickets)
    categoria_pool = [
        "Electrónica",
        "Hogar",
        "Moda",
        "Deporte",
        "Belleza",
        "Alimentación",
        "Juguetes y bebé",
        "Papelería y oficina",
    ]
    categorias = rng.choice(categoria_pool, size=n_tickets)

    texts = []
    for i in range(n_tickets):
        topic_templates = templates[topic_choices[i]]
        template = topic_templates[rng.integers(0, len(topic_templates))]
        texts.append(template.format(dias=dias[i], categoria=categorias[i]))

    labeled_mask = np.zeros(n_tickets, dtype=bool)
    labeled_idx = rng.choice(n_tickets, size=min(n_labeled, n_tickets), replace=False)
    labeled_mask[labeled_idx] = True
    labels = np.where(labeled_mask, topic_choices, None)

    return pd.DataFrame(
        {
            "ticket_id": [f"tick-{i:06d}" for i in range(n_tickets)],
            "customer_id": customer_ids,
            "created_at": created_at,
            "category": topic_choices,
            "text": texts,
            "label": labels,
        }
    )
