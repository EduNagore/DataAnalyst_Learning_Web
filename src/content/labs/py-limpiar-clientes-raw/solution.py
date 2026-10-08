import re

import pandas as pd
from datakit.data import load_raw

raw = load_raw("customers")
print(raw.shape, raw["customer_id"].nunique())

REGIONES = [
    "Andalucía", "Aragón", "Asturias", "Canarias", "Cantabria", "Castilla y León",
    "Castilla-La Mancha", "Cataluña", "Comunidad Valenciana", "Extremadura", "Galicia",
    "Illes Balears", "Madrid", "Navarra", "País Vasco", "Región de Murcia",
]
MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7,
    "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
}
COLUMNAS = [
    "customer_id", "signup_date", "acquisition_channel", "region", "province", "segment",
    "marketing_consent",
]


def parsear_fecha(texto: str) -> pd.Timestamp:
    """Convierte AAAA-MM-DD, DD/MM/AAAA o «D de mes de AAAA» en una fecha."""
    t = str(texto).strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", t):
        return pd.Timestamp(t)
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", t)
    if m:
        return pd.Timestamp(int(m[3]), int(m[2]), int(m[1]))
    m = re.fullmatch(r"(\d{1,2}) de (\w+) de (\d{4})", t)
    if m:
        return pd.Timestamp(int(m[3]), MESES[m[2].lower()], int(m[1]))
    raise ValueError(f"Formato de fecha no reconocido: {texto!r}")


def limpiar_clientes(raw: pd.DataFrame) -> pd.DataFrame:
    """Una fila por cliente, con las columnas COLUMNAS, ordenado por customer_id."""
    oficial = {r.lower(): r for r in REGIONES}
    df = raw.assign(
        region=raw["region"].str.strip().str.lower().map(oficial),
        signup_date=raw["signup_date"].map(parsear_fecha),
    )
    provincia_de = df.dropna(subset=["province"]).drop_duplicates("region").set_index("region")["province"]
    df = df.assign(province=df["province"].fillna(df["region"].map(provincia_de)))
    return df.drop_duplicates("customer_id").sort_values("customer_id")[COLUMNAS].reset_index(drop=True)


print(limpiar_clientes(raw).head())
