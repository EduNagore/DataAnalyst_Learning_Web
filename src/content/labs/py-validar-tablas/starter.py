import re

import pandas as pd
from datakit.data import load_raw, load_table

clientes = load_table("customers")
crudo = load_raw("orders")

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6, "julio": 7,
    "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
}


def _fecha(t: str) -> pd.Timestamp:
    t = t.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", t):
        return pd.Timestamp(t)
    if m := re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", t):
        return pd.Timestamp(int(m[3]), int(m[2]), int(m[1]))
    m = re.fullmatch(r"(\d{1,2}) de (\w+) de (\d{4})", t)
    return pd.Timestamp(int(m[3]), MESES[m[2].lower()], int(m[1]))


# Versión limpia (ya resuelta en el lab anterior): fechas, importes y duplicados.
limpio = (
    crudo.assign(
        order_date=crudo["order_date"].map(_fecha),
        shipping_cost=crudo["shipping_cost"].str.replace(",", ".").astype("float64"),
    )
    .drop_duplicates()
    .drop_duplicates("order_id")
    .reset_index(drop=True)
)


def validar_pedidos(o: pd.DataFrame, clientes: pd.DataFrame) -> dict[str, int]:
    """Nº de filas que incumplen cada una de las siete reglas (0 = todo bien)."""
    # TODO
    ...


def exigir(resultados: dict[str, int], toleradas: frozenset = frozenset()) -> None:
    """Lanza ValueError si hay fallos no tolerados."""
    # TODO
    ...


print("CRUDO ", validar_pedidos(crudo, clientes))
print("LIMPIO", validar_pedidos(limpio, clientes))
