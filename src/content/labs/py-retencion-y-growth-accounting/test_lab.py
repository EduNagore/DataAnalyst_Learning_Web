import pandas as pd
from datakit.data import load_table


def _act(ns):
    return ns["actividad_mensual"](load_table("orders"))


def test_matriz_de_retencion(ns):
    """Mes 1: ≈ 42 % de media; desde el mes 2 se estabiliza en torno al 14 %"""
    act = _act(ns)
    assert len(act) == 206797
    r = ns["matriz_retencion"](act)
    assert (r[0] == 1).all()
    medias = r.loc["2024-01":"2025-06", [1, 2, 3, 6, 12]].mean()
    assert abs(medias[1] - 0.419) < 0.01 and abs(medias[2] - 0.141) < 0.01 and abs(medias[12] - 0.144) < 0.015
    assert abs(r.loc["2025-01", 1] - 0.453) < 0.005


def test_growth_accounting(ns):
    """Marzo de 2026: 9.662 activos = 2.072 nuevos + 2.962 retenidos + 4.628 resucitados; 7.949 perdidos"""
    ga = ns["growth_accounting"](_act(ns))
    m = ga.loc[pd.Period("2026-03", "M")]
    assert (m["activos"], m["nuevos"], m["retenidos"], m["resucitados"], m["perdidos"]) == (9662, 2072, 2962, 4628, 7949)
    assert (ga["nuevos"] + ga["retenidos"] + ga["resucitados"] == ga["activos"]).all()
    assert abs(ns["ratio_rapido"](ga).loc[pd.Period("2026-03", "M")] - 0.84) < 0.01


def test_retencion_por_segmento(ns):
    """A 3 meses: VIP 31,6 %, habituales 18,9 %, ocasionales 9,0 % y nuevos 4,9 %"""
    s = ns["retencion_por_segmento"](_act(ns), load_table("customers"), 3)
    assert abs(s["vip"] - 0.316) < 0.005 and abs(s["habitual"] - 0.189) < 0.005
    assert abs(s["ocasional"] - 0.090) < 0.005 and abs(s["nuevo"] - 0.049) < 0.005


def test_hidden_caso_pequeno(ns):
    """Nuevos, retenidos, resucitados y perdidos a mano (test oculto)"""
    orders = pd.DataFrame(
        {
            "customer_id": ["a", "a", "b", "a", "c", "b"],
            "order_date": pd.to_datetime(
                ["2026-01-05", "2026-01-20", "2026-01-10", "2026-02-03", "2026-02-15", "2026-03-04"]
            ),
            "status": ["completado", "completado", "completado", "completado", "completado", "completado"],
        }
    )
    act = ns["actividad_mensual"](orders)
    assert len(act) == 5, "Un cliente con dos pedidos en el mismo mes cuenta una vez."
    ga = ns["growth_accounting"](act)
    ene, feb, mar = (ga.loc[pd.Period(m, "M")] for m in ("2026-01", "2026-02", "2026-03"))
    assert (ene["activos"], ene["nuevos"], ene["perdidos"]) == (2, 2, 0)
    assert (feb["nuevos"], feb["retenidos"], feb["perdidos"], feb["resucitados"]) == (1, 1, 1, 0)
    assert (mar["activos"], mar["nuevos"], mar["retenidos"], mar["resucitados"], mar["perdidos"]) == (1, 0, 0, 1, 2)
    cancelado = orders.assign(status="cancelado")
    assert len(ns["actividad_mensual"](cancelado)) == 0
