import pandas as pd


def test_k_sin_fecha(ns):
    """Con región, segmento y canal, el grupo más pequeño tiene 6 clientes: 384 combinaciones y ninguna única"""
    c, cuasi = ns["clientes"], ns["CUASI"]
    assert ns["k_anonimato"](c, cuasi) == 6
    p = ns["perfil_de_unicidad"](c, cuasi)
    assert p["grupos"] == 384 and p["unicos"] == 0 and p["k"] == 6 and p["pct_en_riesgo"] == 0


def test_la_fecha_exacta_reidentifica(ns):
    """Añadir el día de alta deja a 45.882 clientes únicos (76 %) y al 99,8 % en grupos de menos de 5"""
    c = ns["clientes"]
    x = c.assign(fecha_g=ns["generalizar_fecha"](c, "signup_date", "dia"))
    p = ns["perfil_de_unicidad"](x, [*ns["CUASI"], "fecha_g"])
    assert p["grupos"] == 52389 and p["unicos"] == 45882 and p["k"] == 1
    assert abs(p["pct_en_riesgo"] - 99.84) < 0.01


def test_generalizar_reduce_el_riesgo(ns):
    """Mes: 30,0 % en riesgo; trimestre: 7,6 %; año: 0,6 % (11 clientes únicos)"""
    c = ns["clientes"]
    esperado = {"mes": (12804, 29.98), "trimestre": (5101, 7.56), "anio": (1531, 0.62)}
    for nivel, (grupos, riesgo) in esperado.items():
        x = c.assign(fecha_g=ns["generalizar_fecha"](c, "signup_date", nivel))
        p = ns["perfil_de_unicidad"](x, [*ns["CUASI"], "fecha_g"])
        assert p["grupos"] == grupos and abs(p["pct_en_riesgo"] - riesgo) < 0.01, nivel
    assert ns["nivel_minimo"](c, ns["CUASI"], "signup_date", k=5, max_supresion=1.0)[0] == "anio"
    nivel, pct = ns["nivel_minimo"](c, ns["CUASI"], "signup_date", k=5, max_supresion=10.0)
    assert nivel == "trimestre" and abs(pct - 7.56) < 0.01


def test_hidden_caso_pequeno(ns):
    """Seis filas a mano: k, supresión de grupos pequeños y niveles de fecha (test oculto)"""
    df = pd.DataFrame(
        {
            "zona": ["A", "A", "A", "B", "B", "C"],
            "sexo": ["h", "h", "h", "m", "m", "h"],
            "alta": pd.to_datetime(["2025-01-10", "2025-02-11", "2025-03-12", "2025-05-02", "2025-06-30", "2026-01-01"]),
        }
    )
    assert ns["k_anonimato"](df, ["zona", "sexo"]) == 1
    limpio, pct = ns["suprimir_raros"](df, ["zona", "sexo"], 2)
    assert len(limpio) == 5 and abs(pct - 100 / 6) < 1e-9 and ns["k_anonimato"](limpio, ["zona", "sexo"]) == 2
    assert list(ns["generalizar_fecha"](df, "alta", "trimestre"))[:4] == ["2025-T1", "2025-T1", "2025-T1", "2025-T2"]
    assert list(ns["generalizar_fecha"](df, "alta", "mes"))[0] == "2025-01"
    assert ns["generalizar_fecha"](df, "alta", "anio").iloc[-1] == "2026"
    try:
        ns["generalizar_fecha"](df, "alta", "siglo")
        fallo = False
    except ValueError:
        fallo = True
    assert fallo
    try:
        ns["nivel_minimo"](df, ["zona", "sexo"], "alta", k=10, max_supresion=0)
        sin = False
    except ValueError:
        sin = True
    assert sin
