import pandas as pd


def _chico(ns):
    y_true = ["neg", "pos", "neg", "neu", "pos"]
    y_pred = ["neg", "pos", "neg", "neu", "neg"]
    return ns["matriz_confusion"](y_true, y_pred, ["neg", "neu", "pos"])


def test_matriz_de_confusion(ns):
    """Filas = real, columnas = predicha, en el orden de las clases; enteros"""
    m = _chico(ns)
    assert list(m.index) == ["neg", "neu", "pos"] and list(m.columns) == ["neg", "neu", "pos"]
    assert m.values.tolist() == [[2, 0, 0], [0, 1, 0], [1, 0, 1]]
    assert all(pd.api.types.is_integer_dtype(t) for t in m.dtypes)


def test_metricas_y_exactitud(ns):
    """En el ejemplo pequeño: neg tiene precisión 2/3 y exhaustividad 1; pos tiene precisión 1 y exhaustividad 1/2"""
    met = ns["metricas_por_clase"](_chico(ns))
    assert list(met.columns) == ["precision", "exhaustividad", "f1", "soporte"]
    assert abs(met.loc["neg", "precision"] - 2 / 3) < 1e-9 and abs(met.loc["neg", "exhaustividad"] - 1) < 1e-9
    assert abs(met.loc["pos", "precision"] - 1) < 1e-9 and abs(met.loc["pos", "exhaustividad"] - 0.5) < 1e-9
    assert abs(met.loc["neg", "f1"] - 0.8) < 1e-9 and met["soporte"].tolist() == [2, 1, 2]
    assert abs(ns["exactitud"](_chico(ns)) - 0.8) < 1e-9
    assert abs(ns["f1_macro"](met) - (0.8 + 1.0 + 2 / 3) / 3) < 1e-9


def test_kappa_de_cohen(ns):
    """Con el ejemplo de la documentación de scikit-learn, κ = 0,6875"""
    assert abs(ns["kappa_cohen"](_chico(ns)) - 0.6875) < 1e-9


def test_clasificador_de_reglas_sobre_la_muestra(ns):
    """1.200 tickets etiquetados: exactitud 0,838, F1 macro 0,841 y κ 0,797; confunde devoluciones, envíos y productos"""
    e = ns["ETIQUETADOS"]
    assert len(e) == 1200
    pred = [ns["clasificar_por_reglas"](t) for t in e["text"]]
    m = ns["matriz_confusion"](e["label"], pred, ns["CLASES"])
    met = ns["metricas_por_clase"](m)
    assert abs(ns["exactitud"](m) - 0.8375) < 0.001
    assert abs(ns["f1_macro"](met) - 0.8410) < 0.001
    assert abs(ns["kappa_cohen"](m) - 0.7966) < 0.001
    assert ns["errores_frecuentes"](m) == [("devoluciones", "producto", 104), ("producto", "pagos", 48), ("envio", "producto", 43)]
    assert abs(met.loc["devoluciones", "exhaustividad"] - 0.5574) < 0.001 and abs(met.loc["producto", "precision"] - 0.58) < 0.001


def test_hidden_clase_sin_predicciones(ns):
    """Una clase que nunca se predice tiene precisión 0 (no un error de división) y los empates se ordenan alfabéticamente"""
    m = ns["matriz_confusion"](["a", "a", "b", "b", "c"], ["a", "a", "a", "a", "a"], ["a", "b", "c"])
    met = ns["metricas_por_clase"](m)
    assert met.loc["b", "precision"] == 0 and met.loc["b", "exhaustividad"] == 0 and met.loc["b", "f1"] == 0
    assert abs(met.loc["a", "precision"] - 0.4) < 1e-9 and abs(ns["exactitud"](m) - 0.4) < 1e-9
    assert ns["errores_frecuentes"](m, k=5) == [("b", "a", 2), ("c", "a", 1)]
    assert abs(ns["kappa_cohen"](m)) < 1e-9, "Predecir siempre la misma clase no mejora el azar: κ = 0."
