import pandas as pd
from datakit.data import load_table

orders = load_table("orders")
order_items = load_table("order_items")


def ingresos_por_pedido(orders: pd.DataFrame, order_items: pd.DataFrame) -> pd.DataFrame:
    """`orders` + columna `ingresos` (suma de quantity * unit_price; 0 si no hay líneas)."""
    por_pedido = (order_items["quantity"] * order_items["unit_price"]).groupby(order_items["order_id"]).sum()
    out = orders.copy()
    out["ingresos"] = out["order_id"].map(por_pedido).fillna(0.0)
    return out


def agrupar_por(df: pd.DataFrame, campo: str, valor: str, funcion: str = "sum") -> pd.DataFrame:
    """Equivalente de AGRUPARPOR: columnas `campo` y `valor`, de mayor a menor `valor`."""
    out = df.groupby(campo)[valor].agg(funcion).reset_index()
    return out.sort_values(valor, ascending=False, ignore_index=True)


def pivotar_por(
    df: pd.DataFrame, filas: str, columnas: str, valor: str, funcion: str = "sum", totales: bool = True
) -> pd.DataFrame:
    """Equivalente de PIVOTARPOR: filas en el índice, columnas en las columnas y totales `Total`."""
    return df.pivot_table(
        index=filas,
        columns=columnas,
        values=valor,
        aggfunc=funcion,
        margins=totales,
        margins_name="Total",
        fill_value=0,
    )


def diferencia_cuadre(pivot: pd.DataFrame, df: pd.DataFrame, valor: str) -> float:
    """|total general de la tabla - suma de `valor` en el origen|, a 2 decimales."""
    return round(abs(float(pivot.loc["Total", "Total"]) - float(df[valor].sum())), 2)


pedidos = ingresos_por_pedido(orders, order_items)
tabla = pivotar_por(pedidos, "channel", "status", "ingresos")
print(tabla.round(2))
print(diferencia_cuadre(tabla, pedidos, "ingresos"))
