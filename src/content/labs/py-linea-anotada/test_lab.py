import json

import pandas as pd

TITULO = "Los ingresos netos casi se duplican en 2025"


def _tipo(capa):
    m = capa.get("mark")
    return m["type"] if isinstance(m, dict) else m


def _espec(ns):
    return ns["espec_linea_anotada"](
        ns["mensual"], "mes", "m", TITULO, "2025-03-01", "Fin de las rebajas: +22,6 % sobre febrero", "M€"
    )


def test_datos_de_ingresos(ns):
    """La serie mensual de 2025 va de 2,94 M€ (enero) a 5,48 M€ (diciembre)"""
    m = ns["mensual"].set_index("mes")["m"]
    assert len(m) == 12 and abs(m.iloc[0] - 2.94) < 0.011 and abs(m.iloc[-1] - 5.48) < 0.011


def test_titulo_y_capas(ns):
    """Hay título y tres capas: línea, regla y texto"""
    e = _espec(ns)
    titulo = e["title"]["text"] if isinstance(e["title"], dict) else e["title"]
    assert titulo == TITULO, "El título debe ser el pasado como argumento."
    assert "layer" in e and len(e["layer"]) == 3, "Usa `layer` con tres capas."
    assert [_tipo(c) for c in e["layer"]] == ["line", "rule", "text"], "Las capas deben ser line, rule y text (en ese orden)."
    json.dumps(e)


def test_codificacion_y_unidades(ns):
    """La línea usa x temporal e y cuantitativo, con la unidad en el título del eje"""
    linea = _espec(ns)["layer"][0]["encoding"]
    assert linea["x"]["type"] == "temporal" and linea["y"]["type"] == "quantitative", "x temporal e y cuantitativo."
    assert "M€" in str(linea["y"].get("title")), "El título del eje y debe incluir la unidad (M€)."


def test_anotacion(ns):
    """La regla y el texto apuntan a marzo y contienen el texto de la anotación"""
    e = _espec(ns)
    regla, texto = e["layer"][1], e["layer"][2]
    assert "2025-03-01" in json.dumps(regla), "La regla debe estar en 2025-03-01."
    assert "Fin de las rebajas" in json.dumps(texto), "La capa de texto debe contener el texto de la anotación."


def test_hidden_otra_serie(ns):
    """Funciona con otra serie, otra unidad y otro hito (test oculto)"""
    df = pd.DataFrame({"dia": ["2026-01-01", "2026-01-02", "2026-01-03"], "pedidos": [100, 120, 90]})
    e = ns["espec_linea_anotada"](df, "dia", "pedidos", "Los pedidos caen el 3 de enero", "2026-01-03", "Festivo", "pedidos")
    assert len(e["data"]["values"]) == 3 and "pedidos" in str(e["layer"][0]["encoding"]["y"].get("title"))
    assert "2026-01-03" in json.dumps(e["layer"][1]) and "Festivo" in json.dumps(e["layer"][2])
