import pandas as pd
from datakit.data import load_raw, load_table
from datakit.testing import assert_columns, assert_frame_equivalent

COLUMNAS = [
    "customer_id", "signup_date", "acquisition_channel", "region", "province", "segment",
    "marketing_consent",
]


def test_columnas_y_filas(ns):
    """Devuelve las columnas pedidas y una fila por cliente (5.000)"""
    r = ns["limpiar_clientes"](load_raw("customers"))
    assert_columns(r, COLUMNAS)
    assert len(r) == 5000, f"Esperaba 5.000 clientes únicos y hay {len(r)} filas."
    assert r["customer_id"].is_unique, "Quedan customer_id repetidos."


def test_region_oficial(ns):
    """Las regiones son las 16 oficiales"""
    r = ns["limpiar_clientes"](load_raw("customers"))
    assert not r["region"].isna().any(), "Hay regiones sin normalizar (nulos)."
    assert r["region"].nunique() == 16, f"Hay {r['region'].nunique()} regiones distintas; se esperaban 16."


def test_fechas_son_fechas(ns):
    """signup_date es una fecha real"""
    r = ns["limpiar_clientes"](load_raw("customers"))
    assert pd.api.types.is_datetime64_any_dtype(r["signup_date"]), "signup_date debe ser de tipo fecha."


def test_provincia_sin_huecos(ns):
    """province no tiene huecos"""
    r = ns["limpiar_clientes"](load_raw("customers"))
    assert not r["province"].isna().any(), f"Quedan {int(r['province'].isna().sum())} provincias vacías."


def test_coincide_con_la_tabla_limpia(ns):
    """El resultado coincide con la tabla limpia de Lumen"""
    r = ns["limpiar_clientes"](load_raw("customers"))
    limpia = load_table("customers")
    esperado = limpia[limpia["customer_id"].isin(r["customer_id"])][COLUMNAS]
    assert_frame_equivalent(r, esperado, sort_by=["customer_id"])


def test_no_modifica_la_entrada(ns):
    """No modifica el DataFrame de entrada"""
    raw = load_raw("customers")
    antes = raw.copy()
    ns["limpiar_clientes"](raw)
    assert raw.equals(antes), "Has modificado `raw`. Trabaja con copias (assign) y devuelve un resultado nuevo."


def test_hidden_casos_limite(ns):
    """Casos límite: fecha ambigua, mayúsculas, espacios y duplicado disfrazado (test oculto)"""
    raw = pd.DataFrame(
        {
            "customer_id": ["c1", "c2", "c2", "c3", "c4"],
            "signup_date": [
                "03/04/2024",
                "2025-12-31",
                "31 de diciembre de 2025",
                "5 de marzo de 2023",
                "01/02/2026",
            ],
            "acquisition_channel": ["email", "direct", "direct", "organic", "email"],
            "region": [" MADRID ", "castilla-la mancha", "Castilla-La Mancha ", "CASTILLA Y LEÓN", "madrid"],
            "province": ["Madrid", "Toledo", None, None, None],
            "segment": ["nuevo", "vip", "vip", "habitual", "nuevo"],
            "marketing_consent": [True, False, False, True, True],
        }
    )
    r = ns["limpiar_clientes"](raw).set_index("customer_id")
    assert list(r.index) == ["c1", "c2", "c3", "c4"], f"Clientes devueltos: {list(r.index)}"
    assert r.loc["c1", "signup_date"] == pd.Timestamp(2024, 4, 3), "03/04/2024 es el 3 de abril (DD/MM/AAAA)."
    assert r.loc["c1", "region"] == "Madrid"
    assert r.loc["c2", "region"] == "Castilla-La Mancha"
    assert r.loc["c2", "province"] == "Toledo"
    assert r.loc["c4", "province"] == "Madrid", "La provincia de c4 debe recuperarse a partir de su región."
    assert pd.isna(r.loc["c3", "province"]), (
        "c3 es de Castilla y León y no hay otra fila con provincia para esa región: no inventes un valor."
    )
