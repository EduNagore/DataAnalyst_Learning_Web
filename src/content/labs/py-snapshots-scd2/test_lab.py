import pandas as pd


def _historiales(ns):
    ids = ns["ids"]
    s1 = ns["snapshot"](ns["vacio"], ns["extracto"]("2026-01-01"), "customer_id", "2026-01-01")
    s2 = ns["snapshot"](s1, ns["extracto"]("2026-02-01", {ids[0]: "vip", ids[1]: "vip"}), "customer_id", "2026-02-01")
    s3 = ns["snapshot"](
        s2, ns["extracto"]("2026-03-01", {ids[0]: "habitual"}, quitar=(ids[5],)), "customer_id", "2026-03-01", hard_deletes="invalidate"
    )
    return s1, s2, s3


def test_carga_inicial_y_cambios(ns):
    """2.000 filas al inicio; dos cambios en febrero (2.002) y uno en marzo (2.003); un borrado invalidado"""
    s1, s2, s3 = _historiales(ns)
    assert len(s1) == 2000 and s1["dbt_valid_to"].isna().all()
    assert len(s2) == 2002 and int(s2["dbt_valid_to"].notna().sum()) == 2
    assert len(s3) == 2003 and int(s3["dbt_valid_to"].notna().sum()) == 4
    v = ns["vigentes"](s3)
    assert len(v) == 1999 and v["customer_id"].is_unique


def test_viaje_en_el_tiempo(ns):
    """El segmento del primer cliente fue su original, luego vip (febrero) y habitual (marzo)"""
    ids = ns["ids"]
    _, _, s3 = _historiales(ns)
    original = ns["base"].loc[0, "segment"]
    seg = lambda fecha: ns["en_fecha"](s3, fecha).set_index("customer_id").loc[ids[0], "segment"]  # noqa: E731
    assert seg("2026-01-15") == original and seg("2026-02-15") == "vip" and seg("2026-03-15") == "habitual"
    assert len(ns["en_fecha"](s3, "2026-02-15")) == 2000 and len(ns["en_fecha"](s3, "2026-03-15")) == 1999
    assert ids[5] not in set(ns["en_fecha"](s3, "2026-03-15")["customer_id"])


def test_idempotencia(ns):
    """Ejecutar el mismo snapshot dos veces no añade filas"""
    ids = ns["ids"]
    s1, s2, _ = _historiales(ns)
    extracto = ns["extracto"]("2026-02-01", {ids[0]: "vip", ids[1]: "vip"})
    otra = ns["snapshot"](s2, extracto, "customer_id", "2026-02-02")
    assert len(otra) == len(s2)


def test_hidden_estrategia_check_y_borrados(ns):
    """Con estrategia check, la versión nueva empieza «ahora»; con hard_deletes ignore la fila sigue abierta (test oculto)"""
    cols = ["id", "estado", "dbt_valid_from", "dbt_valid_to"]
    hist = pd.DataFrame(
        {
            "id": ["a", "b"],
            "estado": ["activo", "activo"],
            "dbt_valid_from": pd.to_datetime(["2026-01-01", "2026-01-01"]),
            "dbt_valid_to": pd.to_datetime([None, None]),
        }
    )
    actual = pd.DataFrame({"id": ["a"], "estado": ["baja"]})
    s = ns["snapshot"](hist, actual, "id", "2026-05-10", estrategia="check", check_cols=["estado"])
    assert len(s) == 3
    a = s[s["id"] == "a"].sort_values("dbt_valid_from")
    assert list(a["estado"]) == ["activo", "baja"]
    assert a.iloc[0]["dbt_valid_to"] == pd.Timestamp("2026-05-10") and a.iloc[1]["dbt_valid_from"] == pd.Timestamp("2026-05-10")
    assert pd.isna(a.iloc[1]["dbt_valid_to"])
    b = s[s["id"] == "b"]
    assert len(b) == 1 and pd.isna(b.iloc[0]["dbt_valid_to"]), "hard_deletes='ignore': b desapareció de la fuente pero no se cierra."
    s2 = ns["snapshot"](hist, actual, "id", "2026-05-10", estrategia="check", check_cols=["estado"], hard_deletes="invalidate")
    assert not pd.isna(s2[s2["id"] == "b"].iloc[0]["dbt_valid_to"])
    assert list(s.columns) == cols
