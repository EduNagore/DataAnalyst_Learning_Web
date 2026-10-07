"""Tablas de comportamiento: web_sessions, events, marketing_spend, campaigns.

Contiene dos verdades plantadas (ver docs/DATASET.md §5): la paradoja de
Simpson en conversión por dispositivo × región (#2) y el bug de eventos
duplicados de la app v4.2 (#7).
"""

import numpy as np
import pandas as pd

from .reference_data import MARKETING_CHANNELS, REGION_NAMES, REGION_WEIGHTS

# Versiones de la app a lo largo del tiempo (simplificado: todo el mundo
# está en la versión "vigente" en cada fecha, sin rollout escalonado).
_APP_VERSION_TIMELINE = [
    ("3.8.0", "2023-01-01", "2024-02-01"),
    ("4.0.0", "2024-02-01", "2024-08-01"),
    ("4.1.0", "2024-08-01", "2024-11-10"),
    ("4.2.0", "2024-11-10", "2025-02-01"),
    ("4.3.0", "2025-02-01", "2025-08-01"),
    ("4.4.0", "2025-08-01", "2026-12-31"),
]

_STAGE_COLUMNS = ["page_view", "add_to_cart", "checkout", "purchase"]


def _app_version_for_dates(dates: np.ndarray) -> np.ndarray:
    versions = np.full(dates.shape, "", dtype=object)
    for version, start, end in _APP_VERSION_TIMELINE:
        mask = (dates >= pd.Timestamp(start).to_numpy()) & (dates < pd.Timestamp(end).to_numpy())
        versions[mask] = version
    return versions


def build_web_sessions(
    rng: np.random.Generator,
    n_sessions: int,
    customers: pd.DataFrame,
    calendar: pd.DataFrame,
    simpson: dict,
) -> pd.DataFrame:
    day_weights = calendar["demand_multiplier"].to_numpy()
    day_weights = day_weights / day_weights.sum()
    day_idx = rng.choice(len(calendar), size=n_sessions, p=day_weights)
    session_dates = calendar["date"].to_numpy()[day_idx]
    # Hora del día: pico en horario de tarde/noche (distribución normal
    # envuelta sobre 24h, centrada en las 20:00).
    hours = np.mod(rng.normal(loc=20, scale=3.5, size=n_sessions), 24)
    started_at = session_dates + (hours * 3600 * 1e9).astype("timedelta64[ns]")

    region_weights = np.array(REGION_WEIGHTS, dtype=float)
    region_weights = region_weights / region_weights.sum()
    regions = rng.choice(REGION_NAMES, size=n_sessions, p=region_weights)

    is_high = regions == simpson["high_conversion_region"]
    is_low = regions == simpson["low_conversion_region"]
    mobile_share = np.full(n_sessions, simpson["default_mobile_share"])
    mobile_share[is_high] = simpson["mobile_share_in_high_conversion_region"]
    mobile_share[is_low] = simpson["mobile_share_in_low_conversion_region"]

    is_mobile = rng.random(n_sessions) < mobile_share
    remaining_is_desktop = rng.random(n_sessions) < 0.85
    device = np.where(is_mobile, "mobile", np.where(remaining_is_desktop, "desktop", "tablet"))

    # --- Verdad plantada: paradoja de Simpson (conversión por dispositivo x región) ---
    base_rate = np.full(n_sessions, simpson["default_base_rate"])
    base_rate[is_high] = simpson["high_conversion_base_rate"]
    base_rate[is_low] = simpson["low_conversion_base_rate"]
    device_factor = np.where(device == "mobile", 1 - simpson["mobile_conversion_gap"], 1.0)
    effective_rate = base_rate * device_factor

    channel_weights = np.array([0.18, 0.14, 0.12, 0.08, 0.28, 0.20])
    channels = rng.choice(MARKETING_CHANNELS, size=n_sessions, p=channel_weights)

    # ~45% de sesiones de un cliente identificado; el resto, anónimas.
    is_known = rng.random(n_sessions) < 0.45
    customer_idx = rng.integers(0, len(customers), size=n_sessions)
    customer_ids = np.where(is_known, customers["customer_id"].to_numpy()[customer_idx], None)

    app_version = np.where(device == "mobile", _app_version_for_dates(session_dates), None)

    converted = rng.random(n_sessions) < effective_rate
    dropoff_stage = rng.choice(
        ["page_view", "add_to_cart", "checkout"], size=n_sessions, p=[0.55, 0.30, 0.15]
    )
    reached_stage = np.where(converted, "purchase", dropoff_stage)

    sessions = pd.DataFrame(
        {
            "session_id": [f"sess-{i:08d}" for i in range(n_sessions)],
            "customer_id": customer_ids,
            "started_at": started_at,
            "device": device,
            "channel": channels,
            "region": regions,
            "app_version": app_version,
            "_reached_stage": reached_stage,  # auxiliar para build_events; no se publica
        }
    )
    return sessions


def build_events(
    rng: np.random.Generator, sessions: pd.DataFrame, app_bug: dict
) -> pd.DataFrame:
    stage_rank = {s: i for i, s in enumerate(_STAGE_COLUMNS)}
    reached_rank = sessions["_reached_stage"].map(stage_rank).to_numpy()

    rows_session_idx = []
    rows_event_type = []
    rows_offset_minutes = []
    for stage, rank in stage_rank.items():
        mask = reached_rank >= rank
        idx = np.nonzero(mask)[0]
        rows_session_idx.append(idx)
        rows_event_type.append(np.full(idx.shape, stage))
        # Cada paso del funnel ocurre unos minutos después del anterior.
        rows_offset_minutes.append(rank * rng.uniform(1, 6, size=idx.shape[0]))

    session_idx = np.concatenate(rows_session_idx)
    event_type = np.concatenate(rows_event_type)
    offset_minutes = np.concatenate(rows_offset_minutes)

    session_ids = sessions["session_id"].to_numpy()[session_idx]
    started_at = sessions["started_at"].to_numpy()[session_idx]
    app_version = sessions["app_version"].to_numpy()[session_idx]
    occurred_at = started_at + (offset_minutes * 60 * 1e9).astype("timedelta64[ns]")

    n_events = len(session_ids)
    events = pd.DataFrame(
        {
            "event_id": np.arange(n_events),  # se renumera tras la duplicación
            "session_id": session_ids,
            "event_type": event_type,
            "occurred_at": occurred_at,
            "app_version": app_version,
            "properties": [f'{{"stage_rank":{stage_rank[e]}}}' for e in event_type],
        }
    )

    # --- Verdad plantada: bug de tracking, eventos "purchase" duplicados
    # en la app v4.2 durante una ventana de fechas concreta ---
    bug_start = pd.Timestamp(app_bug["start"])
    bug_end = pd.Timestamp(app_bug["end"])
    is_purchase = events["event_type"].to_numpy() == "purchase"
    is_bug_version = events["app_version"].to_numpy() == app_bug["app_version"]
    in_bug_window = (events["occurred_at"] >= bug_start) & (events["occurred_at"] <= bug_end)
    eligible = is_purchase & is_bug_version & in_bug_window
    duplicate_mask = eligible & (rng.random(n_events) < app_bug["duplication_rate"])
    duplicated_rows = events.loc[duplicate_mask].copy()
    duplicated_rows["occurred_at"] = duplicated_rows["occurred_at"] + pd.Timedelta(seconds=1)

    events = pd.concat([events, duplicated_rows], ignore_index=True)
    events = events.sort_values(["session_id", "occurred_at"]).reset_index(drop=True)
    events["event_id"] = [f"evt-{i:08d}" for i in range(len(events))]
    return events[["event_id", "session_id", "event_type", "occurred_at", "app_version", "properties"]]


def build_marketing_spend(
    rng: np.random.Generator, calendar: pd.DataFrame, campaigns: pd.DataFrame
) -> pd.DataFrame:
    dates = calendar["date"]
    demand = calendar["demand_multiplier"].to_numpy()
    rows = []
    for channel in MARKETING_CHANNELS:
        base = rng.uniform(150, 600)
        daily_base = base * (0.7 + 0.3 * demand) * rng.uniform(0.85, 1.15, size=len(dates))
        channel_campaigns = campaigns[campaigns["channel"] == channel]
        extra = np.zeros(len(dates))
        for _, camp in channel_campaigns.iterrows():
            duration = max((camp["end_date"] - camp["start_date"]).days, 1)
            daily_budget = camp["budget_eur"] / duration
            mask = (dates >= camp["start_date"]) & (dates <= camp["end_date"])
            extra[mask.to_numpy()] += daily_budget
        rows.append(
            pd.DataFrame(
                {
                    "date": dates,
                    "channel": channel,
                    "spend_eur": np.round(daily_base + extra, 2),
                }
            )
        )
    return pd.concat(rows, ignore_index=True)


def build_campaigns(rng: np.random.Generator, n_campaigns: int, calendar: pd.DataFrame) -> pd.DataFrame:
    paid_channels = [c for c in MARKETING_CHANNELS if c not in ("direct", "organic")]
    channels = rng.choice(paid_channels, size=n_campaigns)
    total_days = (calendar["date"].max() - calendar["date"].min()).days
    start_offsets = rng.integers(0, total_days - 14, size=n_campaigns)
    durations = rng.integers(7, 45, size=n_campaigns)
    start_dates = calendar["date"].min() + pd.to_timedelta(start_offsets, unit="D")
    end_dates = start_dates + pd.to_timedelta(durations, unit="D")
    budgets = np.round(rng.lognormal(mean=np.log(8000), sigma=0.7, size=n_campaigns), 2)

    return pd.DataFrame(
        {
            "campaign_id": [f"camp-{i:03d}" for i in range(n_campaigns)],
            "channel": channels,
            "start_date": start_dates,
            "end_date": end_dates,
            "budget_eur": budgets,
        }
    )
