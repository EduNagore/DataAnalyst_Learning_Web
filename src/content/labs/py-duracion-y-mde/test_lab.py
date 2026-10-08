import pandas as pd
from datakit.data import load_table


def test_trafico_diario(ns):
    """Últimos 90 días de web_sessions: 759 sesiones al día de media"""
    t = ns["trafico_diario"](load_table("web_sessions"))
    assert abs(t - 758.97) < 0.5, f"Tráfico: {t:.2f}"


def test_tamano_y_plan(ns):
    """+8 % sobre 5,4 % → 44.582 por rama, 118 días y 17 semanas; +20 % → 20 días y 3 semanas"""
    assert ns["tamano_por_rama"](0.054, 0.08) == 44582
    p = ns["plan"](0.054, 0.08, 758.97)
    assert p == {"n_por_rama": 44582, "dias": 118, "semanas": 17}, f"Plan: {p}"
    p = ns["plan"](0.054, 0.20, 758.97)
    assert p["dias"] == 20 and p["semanas"] == 3


def test_mde_alcanzable(ns):
    """Con 4 semanas (10.626 por rama) el MDE es 16,7 %; con 17 semanas, 8,0 %"""
    assert abs(ns["mde_alcanzable"](0.054, 10626) - 0.167) < 0.002
    assert abs(ns["mde_alcanzable"](0.054, 45160) - 0.0795) < 0.002


def test_hidden_coherencia(ns):
    """El MDE invierte el tamaño de muestra y el plan respeta ramas y semanas completas (test oculto)"""
    for mde in (0.05, 0.12, 0.3):
        n = ns["tamano_por_rama"](0.054, mde)
        assert abs(ns["mde_alcanzable"](0.054, n) - mde) < 0.002
    assert ns["mde_alcanzable"](0.054, 20000) < ns["mde_alcanzable"](0.054, 5000)
    tres = ns["plan"](0.054, 0.10, 700, ramas=3)
    dos = ns["plan"](0.054, 0.10, 700, ramas=2)
    assert tres["dias"] > dos["dias"] and tres["semanas"] == -(-tres["dias"] // 7)
    sesiones = pd.DataFrame({"started_at": pd.to_datetime(["2026-01-01 10:00"] * 3 + ["2026-01-02 09:00"] * 5)})
    assert ns["trafico_diario"](sesiones, dias=2) == 4.0
    assert ns["trafico_diario"](sesiones, dias=1) == 5.0
