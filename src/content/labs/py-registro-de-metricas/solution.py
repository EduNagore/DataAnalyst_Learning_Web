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
    return " ".join(definicion.lower().split())


def validar_registro(registro: list[dict]) -> list[tuple]:
    """Problemas de gobierno, ordenados por (métrica, problema): (nombre, «sin_responsable») si el responsable está
    vacío; (nombre, «estado_invalido»); (nombre, «dependencia_inexistente», dep); (nombre, «certificada_depende_de_no_certificada», dep);
    (nombre, «obsoleta_en_uso», panel) por cada panel que usa una métrica obsoleta; y (nombre, «nombre_duplicado»)
    para cada nombre repetido (una vez)."""
    por_nombre = {}
    problemas = []
    vistos = set()
    for m in registro:
        n = m["nombre"]
        if n in vistos and (n, "nombre_duplicado") not in problemas:
            problemas.append((n, "nombre_duplicado"))
        vistos.add(n)
        por_nombre.setdefault(n, m)
    for m in registro:
        n = m["nombre"]
        if not m["responsable"].strip():
            problemas.append((n, "sin_responsable"))
        if m["estado"] not in ESTADOS:
            problemas.append((n, "estado_invalido"))
        for dep in m["depende_de"]:
            if dep not in por_nombre:
                problemas.append((n, "dependencia_inexistente", dep))
            elif m["estado"] == "certificada" and por_nombre[dep]["estado"] != "certificada":
                problemas.append((n, "certificada_depende_de_no_certificada", dep))
        if m["estado"] == "obsoleta":
            for p in m["paneles"]:
                problemas.append((n, "obsoleta_en_uso", p))
    return sorted(problemas, key=lambda t: (t[0], t[1], t[2] if len(t) > 2 else ""))


def definiciones_duplicadas(registro: list[dict]) -> list[list[str]]:
    """Grupos de métricas con nombres distintos pero la misma definición normalizada (la misma métrica dos veces).
    Cada grupo ordenado alfabéticamente; los grupos, por su primer nombre."""
    grupos: dict[str, list[str]] = {}
    for m in registro:
        grupos.setdefault(normalizar(m["definicion"]), []).append(m["nombre"])
    return sorted(sorted(g) for g in grupos.values() if len(g) > 1)


def impacto_de_cambio(registro: list[dict], nombre: str) -> dict:
    """Qué se ve afectado si cambia la definición de `nombre`: las métricas que dependen de ella, directa o
    indirectamente (`metricas`), y los paneles de esas métricas y de la propia (`paneles`), ambos como listas ordenadas."""
    por_nombre = {m["nombre"]: m for m in registro}
    afectadas = {nombre}
    crece = True
    while crece:
        crece = False
        for m in registro:
            if m["nombre"] not in afectadas and set(m["depende_de"]) & afectadas:
                afectadas.add(m["nombre"])
                crece = True
    paneles = {p for n in afectadas for p in por_nombre[n]["paneles"]}
    return {"metricas": sorted(afectadas - {nombre}), "paneles": sorted(paneles)}


for problema in validar_registro(registro):
    print(problema)
print(definiciones_duplicadas(registro))
print(impacto_de_cambio(registro, "ingresos_brutos"))
