def test_redondeo_significativo(ns):
    """49.460.756,64 con 3 cifras es 49.500.000; 0,004567 con 2 es 0,0046; el 0 se queda en 0"""
    f = ns["redondear_significativo"]
    assert f(49460756.64) == 49500000.0
    assert abs(f(0.004567, 2) - 0.0046) < 1e-12
    assert f(0) == 0 and f(-1234.5, 2) == -1200.0


def test_formato_espanol(ns):
    """1234,56 con un decimal es «1.234,6»; 1234567,891 con 2 es «1.234.567,89»"""
    f = ns["formatear_es"]
    assert f(1234.56, 1) == "1.234,6"
    assert f(1234567.891, 2) == "1.234.567,89"
    assert f(0.5, 0) in ("0", "1") and f(12.0, 0) == "12"


def test_millones(ns):
    """49.460.756,64 € son «49,5 M€»"""
    assert ns["en_millones"](49460756.64) == "49,5 M€"
    assert ns["en_millones"](22441854, 2) == "22,44 M€"


def test_describir_cambio(ns):
    """Ingresos: +120,4 % (de 22,4 M€ a 49,5 M€); Conversión: -0,12 pp (del 4,29 % al 4,17 %)"""
    d = ns["describir_cambio"]
    assert d("Ingresos", 49460757, 22441854, "euros") == "Ingresos: +120,4 % (de 22,4 M€ a 49,5 M€)"
    assert d("Conversión", 4.17, 4.29, "tasa") == "Conversión: -0,12 pp (del 4,29 % al 4,17 %)"


def test_rango(ns):
    """Una muestra con media 301,7 y error estándar 66,41 da «entre 172 y 432 €»"""
    assert ns["rango_texto"](301.7, 66.41) == "entre 172 y 432 € (95 % de confianza)"
    assert ns["rango_texto"](10.0, 1.0, unidad="días") == "entre 8 y 12 días (95 % de confianza)"


def test_hidden_casos_limite(ns):
    """Importes pequeños, bajadas en euros y tipo desconocido (test oculto)"""
    d = ns["describir_cambio"]
    assert d("Ticket", 305.87, 303.35, "euros") == "Ticket: +0,8 % (de 303 € a 306 €)"
    assert d("Margen", 35.05, 35.71, "tasa") == "Margen: -0,66 pp (del 35,71 % al 35,05 %)"
    assert d("Pedidos", 100000, 120000, "euros") == "Pedidos: -16,7 % (de 120.000 € a 100.000 €)"
    try:
        d("X", 1, 2, "otro")
    except ValueError:
        return
    raise AssertionError("Un tipo desconocido debe lanzar ValueError.")
