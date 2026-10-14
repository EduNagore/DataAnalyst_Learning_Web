import numpy as np
import pandas as pd


def test_plantillas(ns):
    """Normaliza números y categorías: de 15.000 tickets (94 textos distintos) quedan 25 plantillas de unos 600 tickets"""
    n = ns["normalizar_plantilla"]
    assert n("Mi pedido lleva 14 días de retraso") == "Mi pedido lleva N días de retraso"
    assert n("¿Puedo pagar a plazos un pedido de la categoría Juguetes y bebé?") == "¿Puedo pagar a plazos un pedido de la categoría X?"
    assert n("El producto de la categoría Deporte no coincide con la descripción.") == "El producto de la categoría X no coincide con la descripción."
    pl = ns["plantillas"](ns["TICKETS"])
    assert list(pl.columns) == ["plantilla", "categoria", "n"] and len(pl) == 25 and pl["n"].sum() == 15000
    assert pl.loc[0, "plantilla"] == "La dirección de entrega era correcta pero el paquete volvió al almacén." and pl.loc[0, "n"] == 637
    assert pl["n"].is_monotonic_decreasing and pl["n"].min() == 566


def test_tokenizar_y_tfidf(ns):
    """Sin acentos ni palabras vacías; filas de norma 1; idf = ln((1+n)/(1+df)) + 1"""
    assert ns["tokenizar"]("¡Me han cobrado DOS veces en la App!") == ["han", "cobrado", "dos", "veces", "app"]
    X, vocab = ns["tfidf"](["gato negro", "gato blanco", "perro"])
    assert vocab == ["blanco", "gato", "negro", "perro"] and X.shape == (3, 4)
    assert np.allclose(np.linalg.norm(X, axis=1), 1)
    idf_gato, idf_negro = np.log(4 / 3) + 1, np.log(4 / 2) + 1
    assert abs(X[0, 1] / X[0, 2] - idf_gato / idf_negro) < 1e-9 and X[0, 3] == 0
    assert abs(ns["similitud"](X)[0, 1] - X[0, 1] * X[1, 1]) < 1e-9


def test_el_par_casi_duplicado(ns):
    """Con 25 plantillas y 109 palabras, solo un par supera 0,5: «cobrado dos veces» en pagos y en app, con similitud ≈ 0,82"""
    pl = ns["plantillas"](ns["TICKETS"])
    X, vocab = ns["tfidf"](list(pl["plantilla"]))
    assert len(vocab) == 109
    S = ns["similitud"](X)
    pares = ns["pares_parecidos"](S, 0.5)
    assert len(pares) == 1
    i, j, s = pares[0]
    assert abs(s - 0.82) < 0.01
    assert {pl.loc[i, "categoria"], pl.loc[j, "categoria"]} == {"pagos", "app"}
    assert all("cobrado dos veces" in pl.loc[x, "plantilla"] for x in (i, j))
    assert ns["vecinos"](S, i, 1) == [j] and ns["vecinos"](S, j, 1) == [i]


def test_agrupar_no_reproduce_las_categorias(ns):
    """K-means sobre las plantillas nunca llega a la pureza de 0,85 respecto a la categoría, y con 8 grupos depende de la semilla"""
    pl = ns["plantillas"](ns["TICKETS"])
    X, _ = ns["tfidf"](list(pl["plantilla"]))
    cats = list(pl["categoria"])
    assert abs(ns["pureza"]([0, 0, 1, 1], ["a", "a", "a", "b"]) - 0.75) < 1e-9
    for k in (5, 8, 12):
        lo, hi = ns["rango_pureza"](X, cats, k, range(6))
        assert 0.3 < lo <= hi < 0.85
    lo, hi = ns["rango_pureza"](X, cats, 8, range(6))
    assert hi - lo > 0.05, "Con 8 grupos la pureza cambia con la semilla: la agrupación no es estable."


def test_hidden_empates_y_umbral(ns):
    """Los vecinos se ordenan por similitud y luego por índice; pares_parecidos respeta i < j y el umbral (test oculto)"""
    S = np.array([[1.0, 0.5, 0.5, 0.1], [0.5, 1.0, 0.2, 0.9], [0.5, 0.2, 1.0, 0.0], [0.1, 0.9, 0.0, 1.0]])
    assert ns["vecinos"](S, 0, 2) == [1, 2] and ns["vecinos"](S, 3, 3) == [1, 0, 2]
    assert ns["pares_parecidos"](S, 0.5) == [(1, 3, 0.9), (0, 1, 0.5), (0, 2, 0.5)]
    assert ns["pares_parecidos"](S, 0.95) == []
    assert isinstance(ns["plantillas"](pd.DataFrame({"text": ["a 1", "a 2", "b"], "category": ["x", "x", "y"]})), pd.DataFrame)
