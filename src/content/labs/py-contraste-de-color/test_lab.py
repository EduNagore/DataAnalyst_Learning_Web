def test_luminancia(ns):
    """Blanco = 1, negro = 0"""
    assert ns["luminancia"]("#FFFFFF") == 1.0
    assert ns["luminancia"]("#000000") == 0.0
    assert abs(ns["luminancia"]("#808080") - 0.215861) < 0.00002


def test_contraste_conocido(ns):
    """Negro sobre blanco es 21:1; el amarillo de Okabe-Ito sobre blanco es 1,32:1"""
    c = ns["contraste"]
    assert c("#000000", "#FFFFFF") == 21.0
    assert c("#FFFFFF", "#000000") == 21.0, "El contraste es simétrico."
    assert abs(c("#F0E442", "#FFFFFF") - 1.32) < 0.011
    assert abs(c("#0072B2", "#FFFFFF") - 5.19) < 0.011
    assert abs(c("#009E73", "#0B1220") - 5.47) < 0.011


def test_umbrales(ns):
    """El azul cumple el texto sobre blanco; el naranja no cumple ni el gráfico; el verde azulado cumple solo el gráfico"""
    f = ns["cumple_wcag"]
    assert f("#0072B2", "#FFFFFF", "texto") is True
    assert f("#E69F00", "#FFFFFF", "grafico") is False
    assert f("#009E73", "#FFFFFF", "grafico") is True and f("#009E73", "#FFFFFF", "texto") is False
    assert f("#000000", "#0B1220", "grafico") is False, "El negro sobre un fondo oscuro no contrasta."


def test_paleta_sobre_blanco(ns):
    """De los ocho colores de Okabe-Ito, cinco cumplen 3:1 sobre blanco (verde, azul, bermellón, púrpura y negro)"""
    ok = [n for n, h in ns["OKABE_ITO"].items() if ns["cumple_wcag"](h, ns["BLANCO"], "grafico")]
    assert sorted(ok) == sorted(["verde azulado", "azul", "bermellón", "púrpura rojizo", "negro"]), f"Cumplen: {ok}"


def test_banda_de_ruido(ns):
    """Con p = 4,24 % y n = 707, el 2,66 % está fuera de la banda y el 4,0 % dentro"""
    assert ns["fuera_de_banda"](4.24, 707, 2.66) is True
    assert ns["fuera_de_banda"](4.24, 707, 4.0) is False


def test_hidden_uso_invalido_y_banda_amplia(ns):
    """Un uso desconocido lanza ValueError; con pocas observaciones la banda es más ancha (test oculto)"""
    try:
        ns["cumple_wcag"]("#000000", "#FFFFFF", "decoracion")
    except ValueError:
        pass
    else:
        raise AssertionError("Un uso desconocido debe lanzar ValueError.")
    assert ns["fuera_de_banda"](4.24, 707, 5.4) is False
    assert ns["fuera_de_banda"](4.24, 7000, 5.4) is True, "Con 10 veces más observaciones, 5,4 % ya queda fuera de la banda."
