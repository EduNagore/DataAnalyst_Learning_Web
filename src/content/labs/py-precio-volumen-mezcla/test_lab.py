import pandas as pd


def test_cifras_2024_2025(ns):
    """Volumen +26,6 M€, mezcla +0,12 M€ y precio +0,28 M€ entre 2024 y 2025"""
    r = ns["descomponer_pvm"](ns["g2024"], ns["g2025"])
    assert set(r) == {"volumen", "mezcla", "precio", "total"}, f"Claves: {sorted(r)}"
    assert abs(r["volumen"] - 26615033) < 5, f"Volumen: {r['volumen']:.0f}"
    assert abs(r["mezcla"] - 123396) < 5, f"Mezcla: {r['mezcla']:.0f}"
    assert abs(r["precio"] - 280473) < 5, f"Precio: {r['precio']:.0f}"
    assert abs(r["total"] - 27018903) < 5, f"Total: {r['total']:.0f}"


def test_los_efectos_suman_el_total(ns):
    """volumen + mezcla + precio = total (identidad)"""
    r = ns["descomponer_pvm"](ns["g2024"], ns["g2025"])
    assert abs(r["volumen"] + r["mezcla"] + r["precio"] - r["total"]) < 1, "Los tres efectos deben sumar la variación total."


def test_sin_cambios(ns):
    """Si no cambia nada, todos los efectos son cero"""
    r = ns["descomponer_pvm"](ns["g2024"], ns["g2024"])
    assert all(abs(v) < 1e-6 for v in r.values()), f"Efectos: {r}"


def test_hidden_categoria_nueva_y_precio_puro(ns):
    """Una categoría que aparece y un cambio de precio puro se reparten bien (test oculto)"""
    a = pd.DataFrame({"q": [100.0, 100.0], "r": [1000.0, 2000.0]}, index=["x", "y"])
    solo_precio = pd.DataFrame({"q": [100.0, 100.0], "r": [1100.0, 2000.0]}, index=["x", "y"])
    r = ns["descomponer_pvm"](a, solo_precio)
    assert abs(r["volumen"]) < 1e-6 and abs(r["mezcla"]) < 1e-6 and abs(r["precio"] - 100.0) < 1e-6, f"Efectos: {r}"
    nueva = pd.DataFrame({"q": [100.0, 100.0, 50.0], "r": [1000.0, 2000.0, 500.0]}, index=["x", "y", "z"])
    r2 = ns["descomponer_pvm"](a, nueva)
    assert abs(r2["volumen"] + r2["mezcla"] + r2["precio"] - r2["total"]) < 1e-6, f"Efectos: {r2}"
    assert abs(r2["total"] - 500.0) < 1e-6
