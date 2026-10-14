import numpy as np


def _lanza(f, *args):
    try:
        f(*args)
    except ValueError:
        return True
    return False


def test_confusor(ns):
    """Verdad = 2: la comparación ingenua da ≈ 5,39 y ajustar por z recupera ≈ 2,01"""
    df = ns["simular"]("confusor")
    assert set(df.columns) == {"z", "t", "y"} and len(df) == 100000
    assert abs(ns["efecto_ols"](df) - 5.39) < 0.05, "Sin controles el efecto está sesgado al alza."
    assert abs(ns["efecto_ols"](df, ["z"]) - 2.0) < 0.05
    assert ns["controles_correctos"]("confusor") == ["z"]


def test_colisionador(ns):
    """Verdad = 0,5: controlar por el colisionador c da ≈ −0,25 (signo contrario)"""
    df = ns["simular"]("colisionador")
    assert abs(ns["efecto_ols"](df) - 0.5) < 0.03
    assert abs(ns["efecto_ols"](df, ["c"]) + 0.25) < 0.03, "Controlar por c abre un camino falso."
    assert ns["controles_correctos"]("colisionador") == []


def test_mediador(ns):
    """Efecto total 0,7 (0,3 directo + 0,8·0,5 vía m); controlando m solo queda el directo"""
    df = ns["simular"]("mediador")
    assert abs(ns["efecto_ols"](df, ns["controles_correctos"]("mediador")) - 0.7) < 0.03
    assert abs(ns["efecto_ols"](df, ns["controles_correctos"]("mediador", "directo")) - 0.3) < 0.03


def test_hidden_validaciones_y_reproducibilidad(ns):
    """Escenario inexistente, semillas y tamaño de muestra (test oculto)"""
    assert _lanza(ns["simular"], "desconocido"), "Un escenario desconocido debe lanzar ValueError."
    a = ns["simular"]("mediador", n=500, seed=4)
    b = ns["simular"]("mediador", n=500, seed=4)
    assert a.equals(b) and not a.equals(ns["simular"]("mediador", n=500, seed=5))
    pequeno = ns["simular"]("confusor", n=200, seed=1)
    assert len(pequeno) == 200
    assert np.isclose(ns["efecto_ols"](pequeno, ["z"]), ns["efecto_ols"](pequeno, ("z",)))
    assert _lanza(ns["controles_correctos"], "desconocido")
