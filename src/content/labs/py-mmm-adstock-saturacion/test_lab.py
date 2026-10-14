import numpy as np


def test_adstock_y_saturacion(ns):
    """Adstock con decay 0,5 de [1, 0, 0] = [1; 0,5; 0,25]; la saturación crece y se aplana"""
    a = ns["adstock"](np.array([1.0, 0.0, 0.0, 2.0]), 0.5)
    assert np.allclose(a, [1, 0.5, 0.25, 2.125])
    s = ns["saturacion"](np.array([0.0, 1.0, 2.0, 10.0]), 1.0)
    assert s[0] == 0 and abs(s[1] - (1 - np.exp(-1))) < 1e-12
    assert np.all(np.diff(s) > 0) and s[3] < 1
    assert (s[2] - s[1]) < s[1] - s[0], "Rendimientos decrecientes."


def test_ajuste_recupera_el_arrastre(ns):
    """La rejilla recupera el decay real: 0,3 en búsqueda y 0,6 en redes; R² ≈ 0,975"""
    aj = ns["ajustar"](ns["simular_semanas"]())
    assert aj["decay"] == {"busqueda": 0.3, "redes": 0.6}
    assert abs(aj["r2"] - 0.975) < 0.005
    assert all(b > 0 for b in aj["beta"].values())


def test_roas_estimado_frente_al_verdadero(ns):
    """ROAS medio estimado ≈ 1,55 y 1,60 frente a 1,97 y 1,79 reales: el orden de los canales no es fiable"""
    df = ns["simular_semanas"]()
    r = ns["roas_medio"](df, ns["ajustar"](df))
    assert abs(r["busqueda"] - 1.55) < 0.05 and abs(r["redes"] - 1.60) < 0.05
    v = ns["roas_verdadero"](df)
    assert abs(v["busqueda"] - 1.97) < 0.02 and abs(v["redes"] - 1.79) < 0.02
    assert (r["busqueda"] > r["redes"]) != (v["busqueda"] > v["redes"]), (
        "Con saturación y β poco identificados, el estimado ordena los canales al revés del real."
    )


def test_hidden_sin_ruido_recupera_todo(ns):
    """Sin ruido, la rejilla recupera decay y k de ambos canales (test oculto)"""
    import pandas as pd

    df = ns["simular_semanas"](semilla=3)
    n = len(df)
    t = df["semana"].to_numpy(float)
    y = 20000 + 15 * t + 1500 * np.sin(2 * np.pi * t / 52)
    for c in ("busqueda", "redes"):
        d, k, b = ns["DECAY_REAL"][c], ns["K_REAL"][c], ns["BETA_REAL"][c]
        y = y + b * ns["saturacion"](ns["adstock"](df[f"gasto_{c}"].to_numpy(float), d) * (1 - d), k)
    limpio = pd.DataFrame({**{col: df[col] for col in df.columns if col != "ventas"}, "ventas": y})
    assert len(limpio) == n
    aj = ns["ajustar"](limpio)
    assert aj["decay"] == ns["DECAY_REAL"] and aj["k"] == ns["K_REAL"]
    assert aj["r2"] > 0.999999
