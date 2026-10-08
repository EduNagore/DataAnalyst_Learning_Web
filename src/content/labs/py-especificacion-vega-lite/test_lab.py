import json
import re

import pandas as pd

TITULO = "Alimentación vende más unidades (13,5 %) y Moda menos (11,6 %)"


def _espec(ns, df=None, titulo=TITULO):
    df = ns["cuotas"] if df is None else df
    return ns["espec_barras_ordenadas"](df, "categoria", "pct", titulo)


def test_estructura_basica(ns):
    """La especificación es Vega-Lite v6, con título, datos y marca de barras"""
    e = _espec(ns)
    assert isinstance(e, dict), "Devuelve un diccionario."
    assert "vega-lite/v6" in e.get("$schema", ""), "Usa el `$schema` de Vega-Lite v6."
    assert e.get("title") == TITULO, "El título debe ser el que se pasa como argumento."
    assert len(e["data"]["values"]) == 8, "Debe haber una fila por categoría (8)."
    marca = e["mark"]["type"] if isinstance(e["mark"], dict) else e["mark"]
    assert marca == "bar", f"La marca debe ser `bar` y es {marca!r}."
    json.dumps(e)


def test_codificacion_correcta(ns):
    """Categoría en y (nominal, ordenada de mayor a menor) y valor en x (cuantitativo, desde cero)"""
    enc = _espec(ns)["encoding"]
    assert enc["y"]["field"] == "categoria" and enc["y"]["type"] == "nominal", "y debe ser la categoría (nominal)."
    assert enc["x"]["field"] == "pct" and enc["x"]["type"] == "quantitative", "x debe ser el valor (cuantitativo)."
    assert enc["y"].get("sort") in ("-x", "descending"), "Ordena las barras de mayor a menor con sort: '-x'."


def test_eje_en_cero(ns):
    """El eje de las barras empieza en cero (no se recorta)"""
    escala = _espec(ns)["encoding"]["x"].get("scale", {})
    dominio = escala.get("domain")
    assert escala.get("zero") is True or (dominio and dominio[0] == 0), "Las barras deben empezar en cero: scale.domain[0] == 0 o scale.zero == True."


def test_titulo_que_concluye(ns):
    """El título del ejemplo concluye (contiene números y la categoría líder)"""
    t = _espec(ns)["title"]
    assert re.search(r"\d", t) and "Alimentación" in t, "El título debe contener un número y la categoría líder."


def test_elegir_grafico(ns):
    """elegir_grafico devuelve el texto indicado para cada intención"""
    f = ns["elegir_grafico"]
    assert f("comparar", 8) == "barras horizontales ordenadas"
    assert f("comparar", 40) == "top N y otras"
    assert f("tiempo") == "líneas" and f("distribucion") == "histograma"
    assert f("relacion") == "dispersión" and f("exacto") == "tabla"
    assert f("composicion", 3) == "barra apilada al 100 %" and f("composicion", 6) == "barras ordenadas"


def test_hidden_otros_datos_y_error(ns):
    """Funciona con otros datos (ordena y empieza en cero) y rechaza intenciones desconocidas (test oculto)"""
    df = pd.DataFrame({"tienda": ["a", "b", "c"], "ventas": [120.0, 80.0, 200.0]})
    e = ns["espec_barras_ordenadas"](df, "tienda", "ventas", "La tienda c vende 200 unidades, más que a y b")
    assert e["encoding"]["y"]["field"] == "tienda" and e["encoding"]["x"]["field"] == "ventas"
    dominio = e["encoding"]["x"].get("scale", {}).get("domain")
    assert (dominio and dominio[0] == 0 and dominio[1] >= 200) or e["encoding"]["x"].get("scale", {}).get("zero") is True
    try:
        ns["elegir_grafico"]("mapa")
    except ValueError:
        return
    raise AssertionError("Una intención desconocida debe lanzar ValueError.")
