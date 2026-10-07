"""Tabla `calendar`: festivos, eventos comerciales y multiplicador de demanda.

El calendario de festivos regionales incluido aquí es una simplificación
ilustrativa con fines didácticos (un festivo representativo por
comunidad), no una referencia legal exacta de días no laborables.
"""

import numpy as np
import pandas as pd

NATIONAL_HOLIDAYS_FIXED = {
    (1, 1): "Año Nuevo",
    (1, 6): "Epifanía del Señor",
    (5, 1): "Fiesta del Trabajo",
    (8, 15): "Asunción de la Virgen",
    (10, 12): "Fiesta Nacional de España",
    (11, 1): "Todos los Santos",
    (12, 6): "Día de la Constitución",
    (12, 8): "Inmaculada Concepción",
    (12, 25): "Natividad del Señor",
}

# Un festivo representativo por comunidad autónoma (simplificado, ver docstring).
REGIONAL_HOLIDAYS = {
    (2, 28): ("Día de Andalucía", "Andalucía"),
    (9, 11): ("Diada Nacional de Catalunya", "Cataluña"),
    (5, 2): ("Día de la Comunidad de Madrid", "Madrid"),
    (10, 9): ("Día de la Comunidad Valenciana", "Comunidad Valenciana"),
    (7, 25): ("Día Nacional de Galicia", "Galicia"),
    (10, 25): ("Euskadi Eguna", "País Vasco"),
}


def _easter_sunday(year: int) -> pd.Timestamp:
    """Domingo de Resurrección (algoritmo anónimo gregoriano/Meeus-Jones-Butcher)."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7  # noqa: E741
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return pd.Timestamp(year=year, month=month, day=day)


def _fourth_friday_of_november(year: int) -> pd.Timestamp:
    novembers = pd.date_range(f"{year}-11-01", f"{year}-11-30", freq="D")
    fridays = novembers[novembers.weekday == 4]
    return fridays[3]


def build_calendar(date_start: str, date_end: str, sale_events: list[dict]) -> pd.DataFrame:
    dates = pd.date_range(date_start, date_end, freq="D")
    df = pd.DataFrame({"date": dates})
    df["is_holiday_national"] = False
    df["national_holiday_name"] = pd.array([None] * len(df), dtype="object")
    df["is_holiday_regional"] = False
    df["regional_holiday_name"] = pd.array([None] * len(df), dtype="object")
    df["regional_holiday_region"] = pd.array([None] * len(df), dtype="object")
    df["is_sale_event"] = False
    df["sale_event_name"] = pd.array([None] * len(df), dtype="object")

    years = range(dates[0].year, dates[-1].year + 1)
    date_to_idx = {d: i for i, d in enumerate(df["date"])}

    def _set(ts: pd.Timestamp, cols: dict) -> None:
        idx = date_to_idx.get(ts)
        if idx is not None:
            for col, value in cols.items():
                df.at[idx, col] = value

    for (m, d), name in NATIONAL_HOLIDAYS_FIXED.items():
        for y in years:
            _set(
                pd.Timestamp(y, m, d),
                {"is_holiday_national": True, "national_holiday_name": name},
            )

    for y in years:
        _set(
            _easter_sunday(y) - pd.Timedelta(days=2),
            {"is_holiday_national": True, "national_holiday_name": "Viernes Santo"},
        )

    for (m, d), (name, region) in REGIONAL_HOLIDAYS.items():
        for y in years:
            _set(
                pd.Timestamp(y, m, d),
                {
                    "is_holiday_regional": True,
                    "regional_holiday_name": name,
                    "regional_holiday_region": region,
                },
            )

    for y in years:
        bf = _fourth_friday_of_november(y)
        idx = date_to_idx.get(bf)
        if idx is not None:
            end_idx = min(idx + 3, len(df) - 1)  # Black Friday hasta Cyber Monday
            df.loc[idx:end_idx, "is_sale_event"] = True
            df.loc[idx:end_idx, "sale_event_name"] = "Black Friday"

    for ev in sale_events:
        for y in years:
            start = pd.Timestamp(f"{y}-{ev['start']}")
            end = pd.Timestamp(f"{y}-{ev['end']}")
            mask = (df["date"] >= start) & (df["date"] <= end)
            df.loc[mask, "is_sale_event"] = True
            df.loc[mask, "sale_event_name"] = ev["name"]

    df["demand_multiplier"] = _demand_multiplier(df)
    return df


def _demand_multiplier(df: pd.DataFrame) -> np.ndarray:
    dow = df["date"].dt.weekday  # 0 = lunes
    weekday_factor = np.select([dow.isin([4, 5]), dow == 6], [1.15, 0.9], default=1.0)
    sale_factor = np.where(df["is_sale_event"], 1.45, 1.0)
    holiday_factor = np.where(df["is_holiday_national"], 0.82, 1.0)
    days_elapsed = (df["date"] - df["date"].min()).dt.days.to_numpy()
    growth = 1 + 0.08 * (days_elapsed / 365.0)  # leve crecimiento interanual del negocio
    return weekday_factor * sale_factor * holiday_factor * growth
