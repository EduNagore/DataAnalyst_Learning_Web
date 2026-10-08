import numpy as np
import pandas as pd
from datakit.data import load_raw, load_table
from datakit.testing import assert_columns, assert_frame_equivalent


def _importes():
    orders = load_table("orders")
    items = load_table("order_items")
    ped = orders[(orders["status"] != "cancelado") & (orders["order_date"].dt.year == 2025)]
    return (
        (items["quantity"] * items["unit_price"])
        .groupby(items["order_id"])
        .sum()
        .reindex(ped["order_id"])
        .reset_index(drop=True)
    )


def test_tasa_ausentes_columnas_y_cifras(ns):
    """tasa_ausentes_por_grupo devuelve filas, ausentes y porcentaje por segmento"""
    clientes = load_raw("customers").drop_duplicates("customer_id")
    r = ns["tasa_ausentes_por_grupo"](clientes, "province", "segment")
    assert_columns(r, ["segment", "filas", "ausentes", "pct_ausentes"])
    esperado = (
        clientes.assign(falta=clientes["province"].isna())
        .groupby("segment", as_index=False)
        .agg(filas=("customer_id", "size"), ausentes=("falta", "sum"))
    )
    esperado["ausentes"] = esperado["ausentes"].astype(int)
    esperado["pct_ausentes"] = (esperado["ausentes"] / esperado["filas"] * 100).round(1)
    assert_frame_equivalent(r, esperado, sort_by=["segment"], tol=0.051)


def test_iqr_cifras(ns):
    """atipicos_iqr marca los pedidos fuera de Q1-1,5·IQR y Q3+1,5·IQR"""
    x = _importes()
    r = ns["atipicos_iqr"](x)
    q1, q3 = np.percentile(x, [25, 75])
    esperado = int(((x < q1 - 1.5 * (q3 - q1)) | (x > q3 + 1.5 * (q3 - q1))).sum())
    assert isinstance(r, pd.Series) and r.dtype == bool, "Devuelve una Serie booleana."
    assert int(r.sum()) == esperado, f"Marcas {int(r.sum())} pedidos y se esperaban {esperado}."


def test_mad_cifras(ns):
    """atipicos_mad marca |z modificado| > 3,5"""
    x = _importes()
    r = ns["atipicos_mad"](x)
    med = np.median(x)
    mad = np.median(np.abs(x - med))
    esperado = int((np.abs(0.6745 * (x - med) / mad) > 3.5).sum())
    assert int(r.sum()) == esperado, f"Marcas {int(r.sum())} pedidos y se esperaban {esperado}."


def test_las_reglas_difieren(ns):
    """Las dos reglas marcan muchos pedidos en una variable asimétrica (>5 %)"""
    x = _importes()
    for nombre in ["atipicos_iqr", "atipicos_mad"]:
        pct = ns[nombre](x).mean() * 100
        assert pct > 5, f"{nombre} marca solo el {pct:.1f} %: revisa la regla."


def test_hidden_casos_pequenos(ns):
    """Serie pequeña con un extremo y un nulo (test oculto)"""
    x = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 100.0, np.nan], index=list("abcdefg"))
    iqr = ns["atipicos_iqr"](x)
    mad = ns["atipicos_mad"](x)
    for nombre, r in [("IQR", iqr), ("MAD", mad)]:
        assert list(r.index) == list("abcdefg"), f"{nombre}: conserva el índice original."
        assert bool(r["f"]) is True, f"{nombre}: 100 debe ser atípico."
        assert bool(r["g"]) is False, f"{nombre}: un nulo nunca es atípico."
        assert int(r.sum()) == 1, f"{nombre}: solo el 100 es atípico."
    df = pd.DataFrame({"g": ["a", "a", "b", "b"], "v": [1, None, None, None]})
    t = ns["tasa_ausentes_por_grupo"](df, "v", "g").set_index("g")
    assert t.loc["a", "ausentes"] == 1 and t.loc["b", "pct_ausentes"] == 100.0
