import pandas as pd
from datakit.data import load_table


def test_duplicados(ns):
    """75 sesiones con dos eventos de compra, todas de la versión 4.2.0"""
    d = ns["sesiones_con_duplicados"](load_table("events"))
    assert len(d) == 75 and set(d["app_version"]) == {"4.2.0"} and (d["n_eventos"] == 2).all()
    assert list(d.columns) == ["session_id", "n_eventos", "app_version"]
    assert len(ns["sesiones_con_duplicados"](load_table("events"), "add_to_cart")) == 0


def test_compras_por_version(ns):
    """4.2.0: 4,29 compras por 100 sesiones si cuentas eventos y 4,08 si cuentas sesiones (+5,1 %)"""
    r = ns["compras_por_version"](load_table("events"), load_table("web_sessions"))
    assert set(r.index) == {"web", "3.8.0", "4.0.0", "4.1.0", "4.2.0", "4.3.0", "4.4.0"}
    v = r.loc["4.2.0"]
    assert v["sesiones"] == 35784 and v["eventos_compra"] == 1536 and v["sesiones_con_compra"] == 1461
    assert abs(v["por_100_eventos"] - 4.292) < 0.005 and abs(v["por_100_sesiones"] - 4.083) < 0.005
    assert abs(v["sobreestimacion_pct"] - 5.13) < 0.05
    assert r.drop("4.2.0")["sobreestimacion_pct"].abs().max() < 1e-9
    assert abs(r.loc["web", "por_100_sesiones"] - 4.520) < 0.005


def test_deduplicar_y_cobertura(ns):
    """Se eliminan exactamente 75 eventos y las compras únicas cubren el 11,2 % de los pedidos"""
    ev = load_table("events")
    limpio = ns["deduplicar"](ev)
    assert len(ev) - len(limpio) == 75 and (limpio["event_type"] == "purchase").sum() == 42277
    assert abs(ns["cobertura_frente_a_pedidos"](ev, load_table("orders")) - 11.21) < 0.05


def test_hidden_eventos_sinteticos(ns):
    """Conserva el primero, respeta propiedades distintas y no modifica la entrada (test oculto)"""
    ev = pd.DataFrame(
        {
            "event_id": ["e1", "e2", "e3", "e4", "e5"],
            "session_id": ["s1", "s1", "s1", "s2", "s2"],
            "event_type": ["purchase", "purchase", "add_to_cart", "purchase", "purchase"],
            "occurred_at": pd.to_datetime(["2026-01-01 10:00:00", "2026-01-01 10:00:01"] + ["2026-01-01 09:00:00"] * 3),
            "app_version": ["4.2.0"] * 5,
            "properties": ['{"x":1}', '{"x":1}', '{"x":1}', '{"x":1}', '{"x":2}'],
        }
    )
    copia = ev.copy()
    limpio = ns["deduplicar"](ev)
    assert list(limpio["event_id"]) == ["e1", "e3", "e4", "e5"]
    assert ev.equals(copia)
    d = ns["sesiones_con_duplicados"](ev)
    assert list(d["session_id"]) == ["s1", "s2"] and list(d["n_eventos"]) == [2, 2]
