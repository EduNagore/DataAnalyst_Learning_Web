IMPACTOS = {3, 2, 1, 0.5, 0.25}

PETICIONES = [
    {"nombre": "Limpieza de clientes", "alcance": 60000, "impacto": 1, "confianza": 0.8, "esfuerzo": 2},
    {"nombre": "Retrasos y cancelaciones", "alcance": 13347, "impacto": 2, "confianza": 0.8, "esfuerzo": 1.5},
    {"nombre": "Listado VIP por región", "alcance": 5868, "impacto": 0.25, "confianza": 1.0, "esfuerzo": 0.5},
    {"nombre": "Cuadro de mando de tiendas", "alcance": 5000, "impacto": 0.5, "confianza": 1.0, "esfuerzo": 1},
    {"nombre": "Incrementalidad de afiliación", "alcance": 1763, "impacto": 1, "confianza": 0.5, "esfuerzo": 2},
]


def puntuacion_rice(alcance: float, impacto: float, confianza: float, esfuerzo: float) -> float:
    """RICE = alcance * impacto * confianza / esfuerzo, redondeado a 1 decimal."""
    # TODO: valida las entradas (ValueError) y calcula la puntuación
    ...


def priorizar(peticiones: list[dict]) -> list[dict]:
    """Devuelve copias con la clave `rice`, ordenadas por RICE desc, esfuerzo asc y nombre."""
    # TODO
    ...


def seleccionar(peticiones: list[dict], capacidad: float) -> list[str]:
    """Nombres de las peticiones priorizadas que caben en `capacidad` personas-mes."""
    # TODO
    ...


for p in priorizar(PETICIONES):
    print(f"{p['rice']:>10,.1f}  {p['nombre']}")
print(seleccionar(PETICIONES, 3.5))
