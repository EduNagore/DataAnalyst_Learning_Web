import pandas as pd
from datakit.llm import MockLLM


def test_mismo_resultado(ns):
    """Ignora el orden de filas y columnas y los nombres; redondea a 2 decimales; distingue valores distintos"""
    m = ns["mismo_resultado"]
    a = pd.DataFrame({"canal": ["online", "store"], "n": [3, 1]})
    assert m(a, a.iloc[::-1].reset_index(drop=True)) and m(a, a.rename(columns={"canal": "x", "n": "y"})[["y", "x"]])
    assert m(pd.DataFrame({"v": [1.004]}), pd.DataFrame({"v": [1.0]})) and not m(pd.DataFrame({"v": [1.02]}), pd.DataFrame({"v": [1.0]}))
    assert not m(a, a.iloc[:1]) and not m(a, a.assign(n=[3, 2])) and m(pd.DataFrame({"v": [5]}), pd.DataFrame({"v": [5.0]}))


def test_categorias_de_cada_pregunta(ns):
    """4 correctas (q03, q06, q08, q10), 1 por casualidad (q01), 3 distintas (q02, q05, q09), 1 error y 1 abstención"""
    rs = ns["evaluar_sistema"](MockLLM(script=list(ns["RESPUESTAS"])), ns["ORO"])
    cats = {r["id"]: r["categoria"] for r in rs}
    assert cats == {
        "q01": "correcta_por_casualidad", "q02": "resultado_distinto", "q03": "correcta", "q04": "error_ejecucion",
        "q05": "resultado_distinto", "q06": "correcta", "q07": "abstencion", "q08": "correcta",
        "q09": "resultado_distinto", "q10": "correcta",
    }
    assert [r["sql"] for r in rs] == ns["RESPUESTAS"]


def test_exactitud_e_intervalo(ns):
    """La exactitud estricta es 0,4; mirando solo los datos base parece 0,5; con 10 preguntas el IC de Wilson va de 0,17 a 0,69"""
    rs = ns["evaluar_sistema"](MockLLM(script=list(ns["RESPUESTAS"])), ns["ORO"])
    assert ns["exactitud"](rs) == 0.4 and ns["exactitud"](rs, estricta=False) == 0.5
    lo, hi = ns["intervalo_wilson"](4, 10)
    assert abs(lo - 0.1682) < 0.001 and abs(hi - 0.6873) < 0.001
    lo2, hi2 = ns["intervalo_wilson"](40, 100)
    assert (hi2 - lo2) < (hi - lo) / 2, "Con diez veces más preguntas el intervalo se estrecha mucho."
    lo3, hi3 = ns["intervalo_wilson"](0, 10)
    assert lo3 == 0 or abs(lo3) < 1e-9
    assert 0 < hi3 < 0.35


def test_hidden_casos_pequenos(ns):
    """Abstención en minúsculas, valor fijo, columnas distintas y consulta correcta de otra forma (test oculto)"""
    oro = "SELECT COUNT(*) FROM customers"
    assert ns["evaluar_pregunta"](oro, "no_puedo_responder porque falta la tabla") == "abstencion"
    assert ns["evaluar_pregunta"](oro, "SELECT COUNT(customer_id) AS total FROM customers") == "correcta"
    assert ns["evaluar_pregunta"](oro, "SELECT 60000") == "correcta_por_casualidad"
    assert ns["evaluar_pregunta"](oro, "SELECT COUNT(*) FROM clientes") == "error_ejecucion"
    assert ns["evaluar_pregunta"](oro, "SELECT COUNT(*) FROM customers WHERE region = 'Madrid'") == "resultado_distinto"
    assert ns["exactitud"]([{"categoria": "correcta"}, {"categoria": "abstencion"}]) == 0.5
