import numpy as np
import pandas as pd
from datakit.data import load_table
from sklearn.metrics import adjusted_rand_score


def _rfm(ns):
    return ns["calcular_rfm"](load_table("orders"), load_table("order_items"), "2025-12-31")


def test_rfm_y_quintiles(ns):
    """44.737 clientes; mediana de frecuencia 4; 8.577 campeones; cada quintil de F tiene ≈ el mismo tamaño"""
    r = _rfm(ns)
    assert len(r) == 44737 and list(r.columns) == ["customer_id", "recencia", "frecuencia", "monetario"]
    assert r["frecuencia"].median() == 4 and abs(r["monetario"].mean() - 1725.7) < 1.0
    p = ns["puntuar_quintiles"](r)
    assert ((p["R"] >= 4) & (p["F"] >= 4) & (p["M"] >= 4)).sum() == 8577
    assert p["F"].value_counts().min() >= 8947
    # el cliente más reciente puntúa 5 en R
    assert p.loc[p["recencia"].idxmin(), "R"] == 5 and p.loc[p["recencia"].idxmax(), "R"] == 1


def test_kmeans_y_silueta(ns):
    """k = 4: segmentos de 17.253 / 11.835 / 9.771 / 5.878 clientes y silueta ≈ 0,33"""
    r = _rfm(ns)
    et = ns["kmeans_rfm"](r, 4)
    assert sorted(pd.Series(et).value_counts().tolist(), reverse=True) == [17253, 11835, 9771, 5878]
    assert abs(ns["silueta"](r, et) - 0.330) < 0.01
    assert abs(ns["silueta"](r, ns["kmeans_rfm"](r, 2)) - 0.381) < 0.01


def test_perfil_y_estabilidad(ns):
    """El mejor segmento tiene ≈ 3.820 € y 12 pedidos; con otra semilla la partición es casi idéntica"""
    r = _rfm(ns)
    et = ns["kmeans_rfm"](r, 4)
    perfil = ns["perfil_clusters"](r, et)
    assert list(perfil.columns) == ["clientes", "recencia", "frecuencia", "monetario"]
    assert perfil["monetario"].is_monotonic_decreasing
    top = perfil.iloc[0]
    assert abs(top["monetario"] - 3820) < 15 and abs(top["frecuencia"] - 12.0) < 0.2 and top["clientes"] == 11835
    assert adjusted_rand_score(et, ns["kmeans_rfm"](r, 4, seed=3, n_init=1)) > 0.9


def test_hidden_datos_pequenos(ns):
    """Fecha de corte, cancelados y quintiles con empates en datos pequeños (test oculto)"""
    orders = pd.DataFrame(
        {
            "order_id": ["a", "b", "c", "d", "e"],
            "customer_id": ["c1", "c1", "c2", "c2", "c3"],
            "order_date": pd.to_datetime(["2025-01-01", "2025-03-01", "2025-02-01", "2025-06-01", "2025-02-10"]),
            "status": ["completado", "completado", "completado", "cancelado", "completado"],
        }
    )
    items = pd.DataFrame(
        {"order_id": ["a", "b", "c", "d", "e"], "quantity": [1, 2, 1, 1, 3], "unit_price": [10.0, 5.0, 7.0, 99.0, 2.0]}
    )
    r = ns["calcular_rfm"](orders, items, "2025-04-01").set_index("customer_id")
    assert r.loc["c1", "recencia"] == 31 and r.loc["c1", "frecuencia"] == 2 and r.loc["c1", "monetario"] == 20.0
    assert r.loc["c2", "frecuencia"] == 1 and r.loc["c2", "monetario"] == 7.0, "Excluye cancelados."
    assert "c3" in r.index
    antes = ns["calcular_rfm"](orders, items, "2025-02-05")
    assert set(antes["customer_id"]) == {"c1", "c2"}, "No incluyas pedidos posteriores a la fecha de corte."
    grande = pd.DataFrame(
        {"customer_id": [f"c{i}" for i in range(100)], "recencia": np.arange(100), "frecuencia": 1, "monetario": 5.0}
    )
    p = ns["puntuar_quintiles"](grande)
    assert p["F"].value_counts().to_dict() == {1: 20, 2: 20, 3: 20, 4: 20, 5: 20}
