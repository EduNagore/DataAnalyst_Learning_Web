import numpy as np
import pandas as pd
from datakit.data import load_table


def _z(ns):
    s = ns["ingresos_diarios"](load_table("orders"), load_table("order_items"))
    e = ns["errores_log"](s)
    m, sg = ns["parametros_robustos"](e.loc[:"2026-02-28"])
    return s, e, m, sg, ns["puntuaciones_z"](e, m, sg)


def test_serie_y_errores(ns):
    """912 días de ingresos y 532 errores de 19 orígenes; sigma robusto ≈ 0,079"""
    s, e, m, sg, _ = _z(ns)
    assert len(s) == 912
    assert len(e) == 532 and e.index[0] == pd.Timestamp("2025-01-01")
    assert abs(m - 0.0030) < 0.004 and abs(sg - 0.0788) < 0.006


def test_la_rotura_de_stock_de_marzo(ns):
    """La primera racha es de 21 días de baja del 1 al 21 de marzo de 2026, con z medio ≈ −5,3"""
    _, _, _, _, z = _z(ns)
    r = ns["rachas_anomalas"](z)
    assert list(r.columns) == ["inicio", "fin", "dias", "direccion", "z_medio"]
    primera = r.iloc[0]
    assert primera["inicio"] == pd.Timestamp("2026-03-01") and primera["fin"] == pd.Timestamp("2026-03-21")
    assert primera["dias"] == 21 and primera["direccion"] == "baja" and abs(primera["z_medio"] + 5.3) < 0.4
    assert (r.loc[r["direccion"] == "baja", "dias"] == 21).all(), "No hay otras rachas de baja."


def test_hidden_rachas_sinteticas(ns):
    """Rachas, signos y longitud mínima en una serie z construida a mano (test oculto)"""
    idx = pd.date_range("2026-01-01", periods=15, freq="D")
    z = pd.Series([0, 4, 4, 4, 0, -4, -4, 0, 4, 4, 0, 4, -4, -4, -4], index=idx, dtype=float)
    r = ns["rachas_anomalas"](z, umbral=3, minimo=3)
    assert len(r) == 2 and list(r["dias"]) == [3, 3]
    assert list(r["direccion"]) == ["sube", "baja"]
    assert r.iloc[0]["inicio"] == idx[1] and r.iloc[1]["fin"] == idx[-1]
    r1 = ns["rachas_anomalas"](z, umbral=3, minimo=1)
    assert list(r1["dias"]) == [3, 2, 2, 1, 3]
    assert len(ns["rachas_anomalas"](pd.Series(np.zeros(10), index=pd.date_range("2026-01-01", periods=10)))) == 0
    m, sg = ns["parametros_robustos"](pd.Series([1.0, 2.0, 3.0, 4.0, 100.0]))
    assert m == 3.0 and abs(sg - 1.4826 * 1.0) < 1e-9
