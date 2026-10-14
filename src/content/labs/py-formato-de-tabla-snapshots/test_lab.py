import pandas as pd
from datakit.data import load_table


def _mes(df, texto):
    inicio = pd.Timestamp(texto + "-01")
    return df[(df["order_date"] >= inicio) & (df["order_date"] < inicio + pd.offsets.MonthBegin(1))].reset_index(drop=True)


def _tabla(ns):
    orders = load_table("orders")
    t = ns["Tabla"]()
    for m in ("2025-10", "2025-11", "2025-12"):
        t.commit(f"añadir {m}", anade={f"pedidos-{m}": _mes(orders, m)}, base=t.ultimo)
    return t


def test_commits_e_historial(ns):
    """Tres commits crean tres instantáneas con 1, 2 y 3 ficheros y 16.438, 32.821 y 51.666 filas"""
    t = _tabla(ns)
    h = t.historial()
    assert list(h["id"]) == [1, 2, 3] and list(h["n_ficheros"]) == [1, 2, 3]
    assert list(h["filas"]) == [16438, 32821, 51666]
    assert t.ultimo == 3 and list(h["operacion"])[0] == "añadir 2025-10"


def test_viaje_en_el_tiempo(ns):
    """Cada instantánea conserva su contenido aunque la tabla siga cambiando"""
    t = _tabla(ns)
    t.compactar()
    t.borrar(lambda df: df["status"] == "cancelado")
    assert len(t.leer(1)) == 16438 and len(t.leer(2)) == 32821 and len(t.leer(3)) == 51666
    assert len(t.leer(4)) == 51666 and len(t.leer()) == 49538 == len(t.leer(5))
    assert (t.leer()["status"] != "cancelado").all() and (t.leer(3)["status"] == "cancelado").any()
    h = t.historial()
    assert list(h["n_ficheros"]) == [1, 2, 3, 1, 1] and list(h["operacion"])[3:] == ["compactar", "borrar"]


def test_concurrencia_optimista(ns):
    """Un escritor con una base antigua recibe un conflicto y la tabla no cambia"""
    t = _tabla(ns)
    filas = len(t.leer())
    n_snap = len(t.snapshots)
    try:
        t.commit("tardío", anade={"x": pd.DataFrame({"a": [1]})}, base=2)
        fallo = False
    except ns["ConflictoDeEscritura"]:
        fallo = True
    assert fallo, "Debe lanzar ConflictoDeEscritura si la base no es la última instantánea."
    assert len(t.snapshots) == n_snap and len(t.leer()) == filas


def test_hidden_copy_on_write(ns):
    """Borrar solo reescribe los ficheros afectados y compactar conserva los datos (test oculto)"""
    t = ns["Tabla"]()
    t.commit("a", anade={"f1": pd.DataFrame({"id": [1, 2], "v": ["x", "x"]})}, base=None)
    t.commit("b", anade={"f2": pd.DataFrame({"id": [3, 4], "v": ["x", "y"]})}, base=1)
    t.borrar(lambda df: df["v"] == "y")
    ficheros = t.snapshots[-1]["ficheros"]
    assert "f1" in ficheros and "f2" not in ficheros and len(ficheros) == 2, "f1 no tenía filas a borrar: se reutiliza."
    assert sorted(t.leer()["id"]) == [1, 2, 3] and sorted(t.leer(2)["id"]) == [1, 2, 3, 4]
    t.compactar()
    assert len(t.snapshots[-1]["ficheros"]) == 1 and sorted(t.leer()["id"]) == [1, 2, 3]
    assert sorted(t.leer(3)["id"]) == [1, 2, 3], "Las instantáneas anteriores siguen siendo legibles."
    vacia = ns["Tabla"]()
    assert vacia.ultimo is None and vacia.historial().empty
