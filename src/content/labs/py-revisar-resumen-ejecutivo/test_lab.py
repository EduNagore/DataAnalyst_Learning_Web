def test_el_resumen_de_la_leccion_es_valido(ns):
    """El resumen «después» cumple todas las reglas (≈ 100 palabras, ≥ 3 cifras, recomendación, límite y paso)"""
    r = ns["revisar_resumen"](ns["DESPUES"])
    assert r["valido"] is True, f"Problemas: {r['problemas']}"
    assert r["empieza_con_recomendacion"] and r["tiene_limite"] and r["tiene_siguiente_paso"]
    assert 80 <= r["palabras"] <= 120 and r["cifras"] >= 8, f"Palabras y cifras: {r['palabras']}, {r['cifras']}"


def test_el_resumen_antes_falla_en_cuatro_reglas(ns):
    """El resumen «antes» no recomienda, no tiene cifras suficientes, ni límite ni siguiente paso"""
    r = ns["revisar_resumen"](ns["ANTES"])
    assert r["valido"] is False
    esperados = {
        "No empieza por una recomendación",
        "Faltan cifras (mínimo 3)",
        "No declara ningún límite",
        "No propone un siguiente paso",
    }
    assert set(r["problemas"]) == esperados, f"Problemas devueltos: {r['problemas']}"


def test_formato_del_resultado(ns):
    """El resultado lleva exactamente las claves pedidas"""
    r = ns["revisar_resumen"]("Recomendamos aprobar el plan. Costará 3 M€, rendirá 5 M€ y tardará 2 años. Límite: es una estimación. Siguiente paso: pilotar.")
    assert set(r) == {"palabras", "cifras", "empieza_con_recomendacion", "tiene_limite", "tiene_siguiente_paso", "problemas", "valido"}
    assert r["valido"] is True, f"Problemas: {r['problemas']}"


def test_hidden_longitud_y_markdown(ns):
    """Detecta un texto demasiado largo y no cuenta los asteriscos de Markdown (test oculto)"""
    largo = "**Recomendación:** aprobar. " + "dato " * 130 + "Límite: pocos datos. Siguiente paso: validar con 3 pilotos de 5 días y 10 tiendas."
    r = ns["revisar_resumen"](largo)
    assert "Supera las 120 palabras" in r["problemas"], f"Problemas: {r['problemas']}"
    r2 = ns["revisar_resumen"](largo, max_palabras=500)
    assert "Supera las 500 palabras" not in r2["problemas"] and r2["valido"] is True, f"Problemas: {r2['problemas']}"
    corto = ns["revisar_resumen"]("**Recomendación:** aprobar el plan")
    assert corto["palabras"] == 4, f"«**» no cuenta como palabra: {corto['palabras']}"
    assert set(corto["problemas"]) == {"Faltan cifras (mínimo 3)", "No declara ningún límite", "No propone un siguiente paso"}


def test_hidden_la_primera_frase_manda(ns):
    """Una recomendación enterrada al final no cuenta como primera frase (test oculto)"""
    t = "Hemos revisado muchos datos de ventas. Después de eso, recomendamos lanzar el piloto. Límite: es pequeño. Siguiente paso: 2 semanas, 3 tiendas, 1 informe."
    r = ns["revisar_resumen"](t)
    assert r["empieza_con_recomendacion"] is False and "No empieza por una recomendación" in r["problemas"]
