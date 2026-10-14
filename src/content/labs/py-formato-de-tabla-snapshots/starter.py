import pandas as pd
from datakit.data import load_table

orders = load_table("orders")


class ConflictoDeEscritura(Exception):
    """Otro escritor confirmó un cambio después de que leyeras la tabla."""


class Tabla:
    """Una tabla mínima con instantáneas (snapshots) al estilo de Iceberg o Delta Lake:
    los ficheros de datos son inmutables y cada confirmación (commit) crea una instantánea nueva
    con la lista de ficheros que forman la tabla en ese momento."""

    def __init__(self):
        self.ficheros: dict[str, pd.DataFrame] = {}  # nombre → datos (inmutables)
        self.snapshots: list[dict] = []  # {id, operacion, ficheros: tuple[str, ...]}

    @property
    def ultimo(self) -> int | None:
        """Identificador de la última instantánea (None si la tabla está vacía)."""
        return self.snapshots[-1]["id"] if self.snapshots else None

    def commit(self, operacion: str, anade: dict | None = None, elimina: tuple = (), base: int | None = None) -> int:
        """Crea una instantánea que parte de la última: quita los ficheros `elimina` y añade los de `anade`.
        `base` es la instantánea sobre la que trabajó el escritor: si no coincide con la última, lanza
        ConflictoDeEscritura y no cambia nada (concurrencia optimista). Devuelve el id de la nueva instantánea."""
        # TODO
        ...

    def leer(self, snapshot: int | None = None) -> pd.DataFrame:
        """Contenido de la tabla en una instantánea (la última por defecto): «viaje en el tiempo»."""
        # TODO
        ...

    def historial(self) -> pd.DataFrame:
        """Una fila por instantánea: id, operacion, n_ficheros y filas."""
        # TODO
        ...

    def compactar(self) -> int:
        """Sustituye todos los ficheros por uno solo (problema de los ficheros pequeños). Los antiguos siguen
        existiendo para las instantáneas anteriores."""
        # TODO
        ...

    def borrar(self, predicado) -> int:
        """Borra las filas que cumplen `predicado(df) -> máscara booleana` reescribiendo solo los ficheros
        afectados (copy-on-write). Devuelve el id de la nueva instantánea."""
        # TODO
        ...


def mes(df: pd.DataFrame, texto: str) -> pd.DataFrame:
    inicio = pd.Timestamp(texto + "-01")
    return df[(df["order_date"] >= inicio) & (df["order_date"] < inicio + pd.offsets.MonthBegin(1))].reset_index(drop=True)


t = Tabla()
for m in ("2025-10", "2025-11", "2025-12"):
    t.commit(f"añadir {m}", anade={f"pedidos-{m}": mes(orders, m)}, base=t.ultimo)
t.compactar()
t.borrar(lambda df: df["status"] == "cancelado")
print(t.historial())
print("filas en la instantánea 2:", len(t.leer(2)), "| ahora:", len(t.leer()))
