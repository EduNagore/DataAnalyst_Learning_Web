import pandas as pd


def _l(ns):
    return ns["lineas"](ns["orders"], ns["order_items"], ns["returns"], ns["products"], 2025)


def test_cinco_definiciones(ns):
    """Ingresos 2025: lista 54,89; todos 51,56; no cancelados 49,46; completados 46,29; netos 45,94 M€"""
    lin = _l(ns)
    esperado = {"lista": 54.889, "todos": 51.563, "no_cancelados": 49.461, "completados": 46.285, "netos": 45.942}
    for d, v in esperado.items():
        assert abs(ns["ingresos"](lin, d) / 1e6 - v) < 0.001, d


def test_tabla_y_dispersion(ns):
    """La definición más alta supera en un 19,5 % a la más baja: «ingresos» no es un número único"""
    t = ns["tabla_de_discrepancias"](_l(ns))
    assert list(t.index) == ["lista", "todos", "no_cancelados", "completados", "netos"] and t.is_monotonic_decreasing
    assert abs(ns["dispersion"](t) - 19.47) < 0.05


def test_pedidos_segun_definicion(ns):
    """Pedidos 2025: 168.466 con cancelados, 161.706 sin ellos y 151.469 completados"""
    o = ns["orders"]
    assert ns["pedidos"](o, 2025, "todos") == 168466
    assert ns["pedidos"](o, 2025, "no_cancelados") == 161706
    assert ns["pedidos"](o, 2025, "completados") == 151469


def test_hidden_caso_pequeno(ns):
    """Cálculo a mano con una línea cancelada, otra devuelta y definición desconocida (test oculto)"""
    lin = pd.DataFrame(
        {
            "status": ["completado", "cancelado", "devuelto_parcial", "completado"],
            "cantidad": [2, 1, 1, 3],
            "precio_lista": [10.0, 50.0, 40.0, 5.0],
            "precio_final": [9.0, 45.0, 36.0, 5.0],
            "devuelta": [False, False, True, False],
        }
    )
    assert abs(ns["ingresos"](lin, "todos") - (18 + 45 + 36 + 15)) < 1e-9
    assert abs(ns["ingresos"](lin, "no_cancelados") - (18 + 36 + 15)) < 1e-9
    assert abs(ns["ingresos"](lin, "completados") - (18 + 15)) < 1e-9
    assert abs(ns["ingresos"](lin, "netos") - (18 + 15)) < 1e-9
    assert abs(ns["ingresos"](lin, "lista") - (20 + 40 + 15)) < 1e-9
    try:
        ns["ingresos"](lin, "magia")
        fallo = False
    except ValueError:
        fallo = True
    assert fallo
