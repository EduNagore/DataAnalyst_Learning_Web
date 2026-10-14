import pandas as pd
from datakit.data import load_raw, load_table
from pandas.api import types as pdt

pedidos = load_table("orders")
pedidos_crudos = load_raw("orders")

# Contrato del modelo «pedidos»: columnas, tipo lógico y si admite nulos
contrato_pedidos = {
    "order_id": {"tipo": "string", "not_null": True},
    "customer_id": {"tipo": "string", "not_null": True},
    "order_date": {"tipo": "datetime", "not_null": True},
    "channel": {"tipo": "string", "not_null": True},
    "device": {"tipo": "string", "not_null": True},
    "discount_pct": {"tipo": "float", "not_null": True},
    "shipping_cost": {"tipo": "float", "not_null": True},
    "status": {"tipo": "string", "not_null": True},
    "store_id": {"tipo": "string", "not_null": False},  # los pedidos online no tienen tienda
}


def tipo_logico(serie: pd.Series) -> str:
    """«bool», «int», «float», «datetime» o «string» (cualquier otro tipo, incluidos los objetos)."""
    if pdt.is_bool_dtype(serie):
        return "bool"
    if pdt.is_integer_dtype(serie):
        return "int"
    if pdt.is_float_dtype(serie):
        return "float"
    if pdt.is_datetime64_any_dtype(serie):
        return "datetime"
    return "string"


def validar_contrato(df: pd.DataFrame, contrato: dict) -> list[tuple]:
    """Incumplimientos del contrato, ordenados por columna: (columna, «falta»), (columna, «sobra»),
    (columna, «tipo», esperado, real) y (columna, «nulos», nº de nulos). El orden de las columnas no importa;
    las columnas que faltan o sobran no se comprueban más."""
    fallos = []
    for col in sorted(set(contrato) | set(df.columns)):
        if col not in df.columns:
            fallos.append((col, "falta"))
        elif col not in contrato:
            fallos.append((col, "sobra"))
        else:
            real = tipo_logico(df[col])
            if real != contrato[col]["tipo"]:
                fallos.append((col, "tipo", contrato[col]["tipo"], real))
            if contrato[col].get("not_null") and df[col].isna().any():
                fallos.append((col, "nulos", int(df[col].isna().sum())))
    return fallos


def inferir_contrato(df: pd.DataFrame) -> dict:
    """Contrato que describe el DataFrame actual: el tipo lógico de cada columna y not_null si no tiene nulos."""
    return {c: {"tipo": tipo_logico(df[c]), "not_null": bool(df[c].notna().all())} for c in df.columns}


def cambios_incompatibles(antiguo: dict, nuevo: dict) -> list[tuple]:
    """Cambios que rompen a los consumidores al pasar de un contrato a otro, ordenados por columna:
    (columna, «columna_eliminada»), (columna, «tipo_cambiado») y (columna, «restriccion_eliminada»)
    (un not_null que desaparece). Añadir columnas es compatible."""
    cambios = []
    for col in sorted(antiguo):
        if col not in nuevo:
            cambios.append((col, "columna_eliminada"))
            continue
        if antiguo[col]["tipo"] != nuevo[col]["tipo"]:
            cambios.append((col, "tipo_cambiado"))
        if antiguo[col].get("not_null") and not nuevo[col].get("not_null"):
            cambios.append((col, "restriccion_eliminada"))
    return cambios


print("pedidos limpios:", validar_contrato(pedidos, contrato_pedidos))
print("pedidos crudos:", validar_contrato(pedidos_crudos, contrato_pedidos))
