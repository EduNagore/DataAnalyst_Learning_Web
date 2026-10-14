import pandas as pd


def _tabla(ns):
    rec = ns["recorridos"]
    return {
        k: ns[f"credito_{k}"](rec)
        for k in ("ultimo_clic", "primer_clic", "lineal", "posicion", "markov")
    }


def test_ultimo_y_primer_clic(ns):
    """Último clic: 122 conversiones para búsqueda de pago y 8 para redes; primer clic: 66 y 40"""
    t = _tabla(ns)
    assert t["ultimo_clic"]["paid_search"] == 122 and t["ultimo_clic"]["paid_social"] == 8
    assert t["primer_clic"]["paid_social"] == 66 and t["primer_clic"]["paid_search"] == 40
    for k in ("ultimo_clic", "primer_clic"):
        assert abs(t[k].sum() - 193) < 1e-9, "Cada conversión reparte exactamente 1 de crédito."


def test_lineal_y_posicion(ns):
    """Lineal: búsqueda de pago 77,33 y redes 33,33; en U (40/20/40): 78,8 y 34,8"""
    t = _tabla(ns)
    assert abs(t["lineal"]["paid_search"] - 77.33) < 0.01 and abs(t["lineal"]["paid_social"] - 33.33) < 0.01
    assert abs(t["posicion"]["paid_search"] - 78.8) < 0.01 and abs(t["posicion"]["paid_social"] - 34.8) < 0.01
    assert abs(t["lineal"].sum() - 193) < 1e-9 and abs(t["posicion"].sum() - 193) < 1e-9


def test_efecto_de_eliminacion(ns):
    """Markov: el crédito suma 193; búsqueda de pago ≈ 81,7 y redes de pago ≈ 35,3 (más que con último clic)"""
    m = _tabla(ns)["markov"]
    assert abs(m.sum() - 193) < 1e-6
    assert abs(m["paid_search"] - 81.7) < 0.1 and abs(m["paid_social"] - 35.3) < 0.1
    assert m["paid_social"] > 4 * _tabla(ns)["ultimo_clic"]["paid_social"]


def test_hidden_caso_pequeno(ns):
    """Dos caminos a mano: A→B→C (4 conversiones) y A (1 conversión) (test oculto)"""
    rec = pd.DataFrame(
        {
            "camino": [("A", "B", "C"), ("A",)],
            "personas": [10, 10],
            "conversiones": [4, 1],
        }
    )
    u, p = ns["credito_ultimo_clic"](rec), ns["credito_primer_clic"](rec)
    assert u["C"] == 4 and u["A"] == 1 and p["A"] == 5
    li = ns["credito_lineal"](rec)
    assert abs(li["A"] - (4 / 3 + 1)) < 1e-9 and abs(li["B"] - 4 / 3) < 1e-9
    po = ns["credito_posicion"](rec)
    assert abs(po["A"] - 2.6) < 1e-9 and abs(po["B"] - 0.8) < 1e-9 and abs(po["C"] - 1.6) < 1e-9
    mk = ns["credito_markov"](rec)
    assert abs(mk.sum() - 5) < 1e-9
    assert mk["A"] > mk["B"], "Quitar A elimina todos los caminos; quitar B solo uno."
