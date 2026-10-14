def test_coste_de_una_llamada(ns):
    """Los precios son € por millón de tokens: 1.000 tokens de entrada a 3 € y 100 de salida a 15 € cuestan 0,0045 €"""
    assert abs(ns["coste_llamada"](1000, 100, 3.0, 15.0) - 0.0045) < 1e-12
    assert ns["coste_llamada"](0, 0, 3.0, 15.0) == 0


def test_plan_sin_y_con_deduplicacion(ns):
    """15.000 llamadas frente a 94 textos distintos: el ahorro es del 99,4 %"""
    textos = list(ns["TICKETS"]["text"])
    args = (ns["PROMPT_BASE"], 3, ns["PRECIO_ENTRADA"], ns["PRECIO_SALIDA"])
    todo = ns["plan_de_coste"](textos, *args)
    unico = ns["plan_de_coste"](textos, *args, deduplicar=True)
    assert todo["llamadas"] == 15000 and unico["llamadas"] == 94
    assert todo["tokens_salida"] == 45000 and unico["tokens_salida"] == 282
    assert todo["tokens_entrada"] == 1953565 and unico["tokens_entrada"] == 12365
    assert abs(todo["coste"] - 6.5357) < 0.001 and abs(unico["coste"] - 0.0413) < 0.001
    assert abs(1 - unico["coste"] / todo["coste"] - 0.9937) < 0.001


def test_margen_y_tamano_de_muestra(ns):
    """385 casos para ±5 puntos, 1.537 para ±2,5 y 9.604 para ±1 en el peor caso; 1.200 casos con p = 0,84 dan ±2,07 puntos"""
    assert [ns["tamano_muestra"](m) for m in (0.05, 0.025, 0.01)] == [385, 1537, 9604]
    assert abs(ns["margen_error"](0.84, 1200) - 0.02074) < 1e-4
    assert abs(ns["margen_error"](0.9, 30) - 0.1074) < 1e-3
    assert ns["tamano_muestra"](0.05, p=0.9) == 139
    assert ns["margen_error"](0.5, ns["tamano_muestra"](0.03)) <= 0.03


def test_hidden_muestra_estratificada(ns):
    """Mínimo por clase, tope por el tamaño de la clase y proporción en el resto (test oculto)"""
    r = ns["asignar_muestra"]({"a": 900, "b": 80, "c": 20}, 100, 10)
    assert r == {"a": 90, "b": 10, "c": 10}
    assert ns["asignar_muestra"]({"a": 900, "c": 4}, 100, 10) == {"a": 100, "c": 4}
    ls = list(dict.fromkeys(["x", "y", "x", "z", "y"]))
    p = ns["plan_de_coste"](["x", "y", "x", "z", "y"], "base", 1, 1.0, 1.0, deduplicar=True)
    assert p["llamadas"] == len(ls) == 3
