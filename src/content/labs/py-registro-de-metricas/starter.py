ESTADOS = {"certificada", "en_revision", "obsoleta"}

# Registro de métricas de Lumen: nombre, definición, responsable, estado, de qué métricas depende y qué paneles la usan
registro = [
    {"nombre": "ingresos_brutos", "definicion": "SUM(quantity * unit_price)", "responsable": "finanzas", "estado": "certificada", "depende_de": [], "paneles": ["ventas"]},
    {"nombre": "devoluciones", "definicion": "SUM(quantity * unit_price) FILTER (WHERE devuelta)", "responsable": "finanzas", "estado": "certificada", "depende_de": [], "paneles": []},
    {"nombre": "ingresos_netos", "definicion": "ingresos_brutos - devoluciones", "responsable": "finanzas", "estado": "certificada", "depende_de": ["ingresos_brutos", "devoluciones"], "paneles": ["ventas", "consejo"]},
    {"nombre": "pedidos", "definicion": "COUNT(DISTINCT order_id)", "responsable": "operaciones", "estado": "certificada", "depende_de": [], "paneles": ["ventas"]},
    {"nombre": "ticket_medio", "definicion": "ingresos_netos / pedidos", "responsable": "finanzas", "estado": "certificada", "depende_de": ["ingresos_netos", "pedidos"], "paneles": ["consejo"]},
    {"nombre": "ventas_totales", "definicion": "SUM(quantity * unit_price)", "responsable": "marketing", "estado": "en_revision", "depende_de": [], "paneles": ["campanas"]},
    {"nombre": "ingresos_viejos", "definicion": "SUM(quantity * unit_price) FILTER (WHERE status = 'completado')", "responsable": "", "estado": "obsoleta", "depende_de": [], "paneles": ["campanas"]},
    {"nombre": "clientes_activos", "definicion": "COUNT(DISTINCT customer_id)", "responsable": "producto", "estado": "certificada", "depende_de": ["ventas_totales"], "paneles": ["producto"]},
]


def normalizar(definicion: str) -> str:
    """Definición sin espacios sobrantes y en minúsculas, para comparar expresiones iguales escritas distinto."""
    # TODO
    ...


def validar_registro(registro: list[dict]) -> list[tuple]:
    """Problemas de gobierno, ordenados por (métrica, problema): (nombre, «sin_responsable») si el responsable está
    vacío; (nombre, «estado_invalido»); (nombre, «dependencia_inexistente», dep); (nombre, «certificada_depende_de_no_certificada», dep);
    (nombre, «obsoleta_en_uso», panel) por cada panel que usa una métrica obsoleta; y (nombre, «nombre_duplicado»)
    para cada nombre repetido (una vez)."""
    # TODO
    ...


def definiciones_duplicadas(registro: list[dict]) -> list[list[str]]:
    """Grupos de métricas con nombres distintos pero la misma definición normalizada (la misma métrica dos veces).
    Cada grupo ordenado alfabéticamente; los grupos, por su primer nombre."""
    # TODO
    ...


def impacto_de_cambio(registro: list[dict], nombre: str) -> dict:
    """Qué se ve afectado si cambia la definición de `nombre`: las métricas que dependen de ella, directa o
    indirectamente (`metricas`), y los paneles de esas métricas y de la propia (`paneles`), ambos como listas ordenadas."""
    # TODO
    ...


for problema in validar_registro(registro):
    print(problema)
print(definiciones_duplicadas(registro))
print(impacto_de_cambio(registro, "ingresos_brutos"))
