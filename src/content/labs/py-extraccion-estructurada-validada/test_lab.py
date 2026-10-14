from datakit.data import load_table
from datakit.llm import MockLLM


def test_parsear_json(ns):
    """Acepta JSON limpio, con vallas de código y con texto alrededor; devuelve None si no hay JSON válido"""
    p = ns["parsear_json"]
    assert p('{"a": 1}') == {"a": 1}
    assert p('Aquí tienes:\n```json\n{"a": 1, "b": null}\n```') == {"a": 1, "b": None}
    assert p("No puedo clasificar este mensaje.") is None
    assert p("{esto no es json}") is None


def test_validar_errores_y_orden(ns):
    """Cada error con su nombre y en el orden pedido; el objeto correcto no da errores"""
    v = ns["validar"]
    bueno = {"tema": "envio", "dias_retraso": 8, "pide_reembolso": False, "confianza": "alta"}
    assert v(bueno) == [] and v({**bueno, "dias_retraso": None}) == []
    assert v([1, 2]) == ["no_es_objeto"]
    assert v({"tema": "app", "dias_retraso": None, "pide_reembolso": False}) == ["falta:confianza"]
    assert v({**bueno, "tema": "facturacion"}) == ["tema_invalido"]
    assert v({**bueno, "dias_retraso": 999}) == ["dias_fuera_de_rango"]
    assert v({**bueno, "dias_retraso": -1}) == ["dias_fuera_de_rango"]
    assert v({**bueno, "dias_retraso": "8"}) == ["tipo_incorrecto:dias_retraso"]
    assert v({**bueno, "pide_reembolso": "si"}) == ["tipo_incorrecto:pide_reembolso"]
    assert v({**bueno, "confianza": "altísima"}) == ["confianza_invalida"]
    assert v({**bueno, "extra": 1}) == ["clave_extra:extra"]
    assert v({"tema": 3}) == ["falta:dias_retraso", "falta:pide_reembolso", "falta:confianza", "tipo_incorrecto:tema"]


def test_extraer_y_reintentos(ns):
    """Válida a la primera, válida tras un reintento (el prompt incluye el error) y descartada"""
    llm = MockLLM(script=list(ns["RESPUESTAS"]))
    rs = [ns["extraer"](llm, t) for t in ns["TICKETS"]]
    assert [r["ok"] for r in rs] == [True, True, True, False, True, True]
    assert [r["intentos"] for r in rs] == [1, 1, 2, 2, 1, 2]
    assert rs[2]["datos"]["tema"] == "devoluciones" and rs[4]["datos"]["tema"] == "producto"
    assert rs[3]["datos"] is None and rs[3]["errores"] == ["falta:confianza"] and rs[0]["errores"] == []
    assert len(llm.calls) == 9
    reintento = llm.calls[3]["prompt"]
    assert reintento.startswith(ns["construir_prompt"](ns["TICKETS"][2]))
    assert "Tu respuesta anterior no es válida: tema_invalido." in reintento and "Devuelve solo el JSON corregido." in reintento


def test_tasa_de_validez(ns):
    """3 de 6 a la primera, 2 tras reintento y 1 descartada"""
    llm = MockLLM(script=list(ns["RESPUESTAS"]))
    t = ns["tasa_validez"]([ns["extraer"](llm, x) for x in ns["TICKETS"]])
    assert abs(t["primera"] - 0.5) < 1e-9 and abs(t["tras_reintento"] - 1 / 3) < 1e-9 and abs(t["descartadas"] - 1 / 6) < 1e-9


def test_dias_con_expresion_regular(ns):
    """Una expresión regular da los días con exactitud: 2397 tickets mencionan días y la media es 8,06"""
    r = ns["resumen_dias"](load_table("support_tickets"))
    assert r["n"] == 2397 and abs(r["media"] - 8.06) < 1e-9


def test_hidden_casos_limite(ns):
    """Singular, ausencia de número, sin reintentos, mayúsculas y booleanos (test oculto)"""
    assert ns["dias_regex"]("Llevo 1 día esperando") == 1
    assert ns["dias_regex"]("¿Por qué mi envío sigue en el almacén después de 13 días?") == 13
    assert ns["dias_regex"]("La app se cierra sola") is None
    assert ns["validar"]({"tema": "Envio", "dias_retraso": True, "pide_reembolso": False, "confianza": "alta"}) == [
        "tipo_incorrecto:dias_retraso"
    ]
    llm = MockLLM(script=["basura", '{"tema": "app", "dias_retraso": null, "pide_reembolso": false, "confianza": "baja"}'])
    r = ns["extraer"](llm, "texto", max_reintentos=0)
    assert not r["ok"] and r["intentos"] == 1 and r["errores"] == ["sin_json"] and len(llm.calls) == 1
