import numpy as np
import pandas as pd
from datakit.data import load_table
from datakit.lumen import panel_bajas
from sklearn.ensemble import HistGradientBoostingClassifier


def _panel():
    p = panel_bajas(load_table("subscriptions"), load_table("shipments"), load_table("orders"))
    p["anual"] = (p["plan"] == "anual").astype(int)
    p["activa_hoy"] = p["cancelled_at"].isna().astype(int)
    return p


def test_division_temporal(ns):
    """194.309 filas de entrenamiento y 134.471 de prueba, sin solapamiento temporal"""
    train, test = ns["dividir_temporal"](_panel(), "2025-07-01")
    assert (len(train), len(test)) == (194309, 134471), f"{len(train)} / {len(test)}"
    assert train["t"].max() < test["t"].min()


def test_auc_honesto_y_con_fuga(ns):
    """expuesto: 0,635; boosting: 0,635; con activa_hoy (fuga): 0,917"""
    train, test = ns["dividir_temporal"](_panel(), "2025-07-01")
    assert abs(ns["auc_logistico"](train, test, ["expuesto"]) - 0.635) < 0.01
    assert abs(ns["auc_boosting"](train, test, ["expuesto", "anual", "mrr_eur", "k"]) - 0.635) < 0.01
    fuga = ns["auc_logistico"](train, test, ["expuesto", "activa_hoy"])
    assert abs(fuga - 0.917) < 0.02, f"AUC con fuga: {fuga:.3f}"


def test_importancia_por_permutacion(ns):
    """Barajar `expuesto` hunde el AUC ≈ 0,138; el resto de variables no importa"""
    train, test = ns["dividir_temporal"](_panel(), "2025-07-01")
    cols = ["expuesto", "anual", "mrr_eur", "k"]
    gb = HistGradientBoostingClassifier(random_state=0).fit(train[cols], train["cancela"])
    imp = ns["importancia_permutacion"](gb, test[cols], test["cancela"])
    assert imp.index[0] == "expuesto" and abs(imp["expuesto"] - 0.138) < 0.02
    assert imp.drop("expuesto").abs().max() < 0.01 and imp.is_monotonic_decreasing


def test_hidden_permutacion_en_datos_sinteticos(ns):
    """Una variable informativa pesa más que el ruido y la entrada no se modifica (test oculto)"""
    rng = np.random.default_rng(0)
    n = 4000
    util, ruido = rng.normal(size=n), rng.normal(size=n)
    y = (util + rng.normal(0, 0.5, n) > 0).astype(int)
    X = pd.DataFrame({"util": util, "ruido": ruido})
    modelo = HistGradientBoostingClassifier(random_state=0).fit(X, y)
    copia = X.copy()
    imp = ns["importancia_permutacion"](modelo, X, y, n_rep=3, seed=1)
    assert imp.index[0] == "util" and imp["util"] > 0.3 and abs(imp["ruido"]) < 0.08
    assert X.equals(copia), "No modifiques X: baraja una copia."
    a = ns["importancia_permutacion"](modelo, X, y, n_rep=2, seed=5)
    b = ns["importancia_permutacion"](modelo, X, y, n_rep=2, seed=5)
    assert a.equals(b)
