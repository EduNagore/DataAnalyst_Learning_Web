def test_formato_de_la_tarjeta(ns):
    """La tarjeta lleva exactamente las seis claves pedidas"""
    t = ns["tarjeta_kpi"]("Ingresos", 120.0, 100.0, "cantidad")
    assert set(t) == {"nombre", "actual", "anterior", "variacion", "unidad", "estado"}, f"Claves: {sorted(t)}"
    assert t["variacion"] == 20.0 and t["unidad"] == "%" and t["estado"] == "verde", f"Tarjeta: {t}"


def test_tasa_en_puntos_porcentuales(ns):
    """Las tasas varían en pp: 6,33 % frente a 6,21 % es +0,12 pp"""
    t = ns["tarjeta_kpi"]("Devoluciones", 6.33, 6.21, "tasa", "menos", 0.5)
    assert abs(t["variacion"] - 0.12) < 1e-9 and t["unidad"] == "pp", f"Tarjeta: {t}"
    assert t["estado"] == "ambar", "+0,12 pp no supera el umbral de 0,5 pp: ámbar."


def test_mas_es_mejor_y_menos_es_mejor(ns):
    """Con la misma subida, ingresos es verde y devoluciones, rojo"""
    f = ns["tarjeta_kpi"]
    assert f("Ingresos", 110, 100, "cantidad", "mas", 2.0)["estado"] == "verde"
    assert f("Devoluciones", 110, 100, "cantidad", "menos", 2.0)["estado"] == "rojo"
    assert f("Devoluciones", 90, 100, "cantidad", "menos", 2.0)["estado"] == "verde"
    assert f("Ingresos", 90, 100, "cantidad", "mas", 2.0)["estado"] == "rojo"


def test_cuadro_ejecutivo_de_lumen(ns):
    """Ingresos +120,4 % (verde); ticket +0,8 % (ámbar); margen +0,66 pp (verde); guardrails ámbar"""
    c = ns["cuadro"].set_index("nombre")
    assert abs(c.loc["Ingresos netos (€)", "variacion"] - 120.4) < 0.11 and c.loc["Ingresos netos (€)", "estado"] == "verde"
    assert abs(c.loc["Ticket medio (€)", "variacion"] - 0.8) < 0.11 and c.loc["Ticket medio (€)", "estado"] == "ambar"
    assert abs(c.loc["Margen sobre ingresos (%)", "variacion"] - 0.66) < 0.02 and c.loc["Margen sobre ingresos (%)", "estado"] == "verde"
    for guardrail in ["Devoluciones (%)", "Cancelaciones (%)", "Envíos con retraso grave (%)"]:
        assert c.loc[guardrail, "estado"] == "ambar", f"{guardrail}: {c.loc[guardrail].to_dict()}"


def test_hidden_casos_limite(ns):
    """Anterior = 0, igualdad con el umbral y tipo desconocido (test oculto)"""
    f = ns["tarjeta_kpi"]
    t = f("Nuevo KPI", 10, 0, "cantidad")
    assert t["variacion"] is None and t["estado"] == "sin dato", f"Tarjeta: {t}"
    assert f("Borde", 102, 100, "cantidad", "mas", 2.0)["estado"] == "ambar", "Exactamente en el umbral es ámbar."
    try:
        f("X", 1, 1, "otro")
    except ValueError:
        return
    raise AssertionError("Un tipo desconocido debe lanzar ValueError.")
