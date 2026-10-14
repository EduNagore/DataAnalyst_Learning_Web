import pandas as pd
from datakit.data import load_table


def _fuente():
    return load_table("orders")


def test_carga_inicial_e_incremental(ns):
    """Carga inicial hasta 2025 (263.852 filas) y segunda carga con 129.054 nuevas: el destino iguala a la fuente"""
    f = _fuente()
    vacio = f.iloc[0:0]
    d1, r1 = ns["sincronizar"](f[f["order_date"] < "2026-01-01"], vacio, "order_date", "order_id")
    assert r1 == {"leidas": 263852, "nuevas": 263852, "actualizadas": 0} and len(d1) == 263852
    d2, r2 = ns["sincronizar"](f, d1, "order_date", "order_id")
    assert r2["nuevas"] == 129054 and r2["actualizadas"] == 0 and r2["leidas"] < 131000, "Solo se lee la cola, no toda la tabla."
    assert len(d2) == len(f) and d2["order_id"].is_unique


def test_idempotencia(ns):
    """Repetir la carga no cambia el destino: 0 filas nuevas y 0 actualizadas (aunque relea el solape)"""
    f = _fuente()
    d1, _ = ns["sincronizar"](f, f.iloc[0:0], "order_date", "order_id")
    d2, r = ns["sincronizar"](f, d1, "order_date", "order_id")
    assert r["nuevas"] == 0 and r["actualizadas"] == 0 and 0 < r["leidas"] < 3000
    pd.testing.assert_frame_equal(d1.reset_index(drop=True), d2.reset_index(drop=True))


def test_marca_de_agua_y_upsert(ns):
    """La marca de agua es la fecha máxima cargada y `cargar` sustituye por clave"""
    f = _fuente().head(1000)
    assert ns["marca_de_agua"](f.iloc[0:0], "order_date") is None
    assert ns["marca_de_agua"](f, "order_date") == f["order_date"].max()
    cambio = f.head(3).copy()
    cambio["status"] = "cancelado"
    r = ns["cargar"](f, cambio, "order_id")
    assert len(r) == 1000 and (r.set_index("order_id").loc[cambio["order_id"], "status"] == "cancelado").all()


def test_hidden_filas_tardias_y_cambios(ns):
    """Una fila tardía dentro del solape se recoge; una modificada se actualiza; una anterior al solape se pierde (test oculto)"""
    f = pd.DataFrame(
        {
            "id": ["a", "b", "c"],
            "fecha": pd.to_datetime(["2025-01-01", "2025-01-05", "2025-01-10"]),
            "estado": ["ok", "ok", "ok"],
        }
    )
    d1, _ = ns["sincronizar"](f, f.iloc[0:0], "fecha", "id")
    fuente2 = pd.concat(
        [
            f.assign(estado=["ok", "devuelto", "ok"]),
            pd.DataFrame({"id": ["d", "e"], "fecha": pd.to_datetime(["2025-01-09", "2025-01-03"]), "estado": ["ok", "ok"]}),
        ]
    )
    d2, r = ns["sincronizar"](fuente2, d1, "fecha", "id", solape=pd.Timedelta(days=2))
    assert "d" in set(d2["id"]), "La fila tardía del 9 de enero está dentro del solape (marca 10 − 2 días)."
    assert "e" not in set(d2["id"]), "La del 3 de enero queda fuera del solape: se pierde."
    assert r["nuevas"] == 1 and r["actualizadas"] == 0, "b (5 de enero) cambió pero también queda fuera del solape."
    d3, r3 = ns["sincronizar"](fuente2, d2, "fecha", "id", solape=pd.Timedelta(days=10))
    assert r3["nuevas"] == 1 and r3["actualizadas"] == 1 and set(d3["id"]) == {"a", "b", "c", "d", "e"}
    assert d3.set_index("id").loc["b", "estado"] == "devuelto"
