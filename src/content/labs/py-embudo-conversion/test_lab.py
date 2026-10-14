import pandas as pd
from datakit.data import load_table


def _t(ns, por=None):
    return ns["embudo"](load_table("events"), load_table("web_sessions"), por)


def test_embudo_global(ns):
    """1.000.000 → 473.364 (47,3 %) → 186.148 (39,3 %) → 42.277 (22,7 %): 4,23 % en total"""
    t = _t(ns)
    assert list(t["paso"].astype(str)) == ["page_view", "add_to_cart", "checkout", "purchase"]
    assert list(t["sesiones"]) == [1000000, 473364, 186148, 42277]
    assert abs(t["conv_paso"].iloc[1] - 47.34) < 0.01 and abs(t["conv_paso"].iloc[3] - 22.71) < 0.01
    assert abs(t["conv_total"].iloc[3] - 4.23) < 0.01 and pd.isna(t["conv_paso"].iloc[0])
    assert ns["mayor_fuga"](t) == "purchase"


def test_web_frente_a_app(ns):
    """Web 4,52 % y app 3,96 %; la diferencia está en el último paso (23,9 % frente a 21,6 %)"""
    t = _t(ns, "plataforma")
    assert set(t["plataforma"]) == {"web", "app"}
    web = t[t["plataforma"] == "web"].set_index("paso")
    app = t[t["plataforma"] == "app"].set_index("paso")
    assert abs(web.loc["purchase", "conv_total"] - 4.52) < 0.01 and abs(app.loc["purchase", "conv_total"] - 3.96) < 0.01
    assert abs(web.loc["purchase", "conv_paso"] - 23.94) < 0.02 and abs(app.loc["purchase", "conv_paso"] - 21.56) < 0.02
    assert abs(web.loc["add_to_cart", "conv_paso"] - app.loc["add_to_cart", "conv_paso"]) < 0.6


def test_contraste(ns):
    """Web frente a app: +0,558 puntos porcentuales, z ≈ 13,8"""
    r = ns["comparar_proporciones"](21535, 476467, 20742, 523533)
    assert abs(r["diferencia_pp"] - 0.5578) < 0.005 and abs(r["z"] - 13.845) < 0.05 and r["p"] < 1e-30


def test_hidden_segmentacion_y_contraste_simple(ns):
    """Segmentar por dispositivo suma lo mismo y un contraste sin diferencia da p alto (test oculto)"""
    t = _t(ns, "device")
    totales = t[t["paso"].astype(str) == "page_view"]["sesiones"].sum()
    assert totales == 1000000 and set(t["device"]) == {"mobile", "desktop", "tablet"}
    r = ns["comparar_proporciones"](50, 1000, 50, 1000)
    assert r["diferencia_pp"] == 0 and r["z"] == 0 and abs(r["p"] - 1) < 1e-12
    ev = pd.DataFrame(
        {
            "event_id": ["a", "b", "c", "d"],
            "session_id": ["s1", "s1", "s1", "s2"],
            "event_type": ["page_view", "add_to_cart", "add_to_cart", "page_view"],
        }
    )
    ses = pd.DataFrame(
        {"session_id": ["s1", "s2"], "app_version": [None, "4.4.0"], "device": ["desktop", "mobile"], "channel": ["email", "direct"]}
    )
    u = ns["embudo"](ev, ses)
    assert list(u["sesiones"]) == [2, 1], "Cuenta sesiones distintas, no eventos."
