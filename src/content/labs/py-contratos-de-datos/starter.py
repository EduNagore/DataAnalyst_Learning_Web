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
    # TODO
    ...


def validar_contrato(df: pd.DataFrame, contrato: dict) -> list[tuple]:
    """Incumplimientos del contrato, ordenados por columna: (columna, «falta»), (columna, «sobra»),
    (columna, «tipo», esperado, real) y (columna, «nulos», nº de nulos). El orden de las columnas no importa;
    las columnas que faltan o sobran no se comprueban más."""
    # TODO
    ...


def inferir_contrato(df: pd.DataFrame) -> dict:
    """Contrato que describe el DataFrame actual: el tipo lógico de cada columna y not_null si no tiene nulos."""
    # TODO
    ...


def cambios_incompatibles(antiguo: dict, nuevo: dict) -> list[tuple]:
    """Cambios que rompen a los consumidores al pasar de un contrato a otro, ordenados por columna:
    (columna, «columna_eliminada»), (columna, «tipo_cambiado») y (columna, «restriccion_eliminada»)
    (un not_null que desaparece). Añadir columnas es compatible."""
    # TODO
    ...


print("pedidos limpios:", validar_contrato(pedidos, contrato_pedidos))
print("pedidos crudos:", validar_contrato(pedidos_crudos, contrato_pedidos))
