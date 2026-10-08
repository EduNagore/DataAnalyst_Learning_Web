def test_r1c1(ns):
    """Desde F8, «=F7*Supuestos!$B$2» es «=R[-1]C[0]*Supuestos!R2C2»"""
    f = ns["a_r1c1"]
    assert f("=F7*Supuestos!$B$2", "F8") == "=R[-1]C[0]*Supuestos!R2C2"
    assert f("=SUM(B8:E8)", "F8") == "=SUM(R[0]C[-4]:R[0]C[-1])"
    assert f("=A1+$A1+A$1+$A$1", "B2") == "=R[-1]C[-1]+R[-1]C1+R1C[-1]+R1C1"


def test_misma_formula_copiada_es_igual(ns):
    """La misma fórmula copiada a otra celda tiene el mismo patrón R1C1"""
    f = ns["a_r1c1"]
    assert f("=B7*Supuestos!$B$2", "B8") == f("=C7*Supuestos!$B$2", "C8") == f("=AA7*Supuestos!$B$2", "AA8")


def test_inconsistentes(ns):
    """Detecta la referencia sin anclar (F8) y el valor pegado (G8)"""
    serie = {f"{c}8": f"={c}7*Supuestos!$B$2" for c in "BCDE"}
    serie["F8"] = "=F7*Supuestos!F2"
    serie["G8"] = 4120.5
    serie["H8"] = "=H7*Supuestos!$B$2"
    assert ns["celdas_inconsistentes"](serie) == ["F8", "G8"]
    assert ns["celdas_inconsistentes"]({f"{c}1": f"={c}2" for c in "ABC"}) == []


def test_suma_incompleta(ns):
    """B9:L9 no llega a M9; B9:M9 sí"""
    f = ns["suma_incompleta"]
    assert f("=SUM(B9:L9)", "M9") is True
    assert f("=SUM(B9:M9)", "M9") is False
    assert f("=SUMA(B2:B98)", "B99") is True


def test_numeros_como_texto(ns):
    """«1.250», «12,5» y « 7 » son números escritos como texto; «n/a» y los números reales, no"""
    r = ns["numeros_como_texto"]({"A1": "1.250", "A2": "12,5", "A3": " 7 ", "A4": "n/a", "A5": 1250, "A6": "abc1"})
    assert r == ["A1", "A2", "A3"], f"Resultado: {r}"


def test_hidden_casos_borde(ns):
    """Mayoría con constantes, sumas verticales o con $, y series vacías (test oculto)"""
    assert ns["celdas_inconsistentes"]({}) == []
    assert ns["celdas_inconsistentes"]({"A1": 1, "A2": 2}) == ["A1", "A2"]
    col = {f"B{i}": f"=A{i}*2" for i in range(2, 6)}
    col["B4"] = "=A4*3"
    assert ns["celdas_inconsistentes"](col) == ["B4"]
    assert ns["suma_incompleta"]("=SUM($B$2:$B$98)", "B99") is True
    assert ns["suma_incompleta"]("=SUM(B2:B99)", "B99") is False
    assert ns["suma_incompleta"]("=B2+B3", "B99") is False
    assert ns["a_r1c1"]("=AB10", "AC11") == "=R[-1]C[-1]"
