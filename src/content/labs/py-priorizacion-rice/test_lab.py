PETS = [
    {"nombre": "Limpieza de clientes", "alcance": 60000, "impacto": 1, "confianza": 0.8, "esfuerzo": 2},
    {"nombre": "Retrasos y cancelaciones", "alcance": 13347, "impacto": 2, "confianza": 0.8, "esfuerzo": 1.5},
    {"nombre": "Listado VIP por región", "alcance": 5868, "impacto": 0.25, "confianza": 1.0, "esfuerzo": 0.5},
    {"nombre": "Cuadro de mando de tiendas", "alcance": 5000, "impacto": 0.5, "confianza": 1.0, "esfuerzo": 1},
    {"nombre": "Incrementalidad de afiliación", "alcance": 1763, "impacto": 1, "confianza": 0.5, "esfuerzo": 2},
]


def test_puntuacion(ns):
    """60.000 × 1 × 0,8 ÷ 2 = 24.000; 13.347 × 2 × 0,8 ÷ 1,5 = 14.236,8"""
    f = ns["puntuacion_rice"]
    assert f(60000, 1, 0.8, 2) == 24000.0
    assert f(13347, 2, 0.8, 1.5) == 14236.8
    assert f(1763, 1, 0.5, 2) == 440.8 or f(1763, 1, 0.5, 2) == 440.7


def test_orden(ns):
    """El orden de la lección: limpieza, retrasos, VIP, tiendas e incrementalidad"""
    orden = [p["nombre"] for p in ns["priorizar"](PETS)]
    assert orden == [
        "Limpieza de clientes",
        "Retrasos y cancelaciones",
        "Listado VIP por región",
        "Cuadro de mando de tiendas",
        "Incrementalidad de afiliación",
    ]
    assert ns["priorizar"](PETS)[0]["rice"] == 24000.0


def test_capacidad(ns):
    """Con 3,5 personas-mes entran la limpieza (2) y los retrasos (1,5)"""
    assert ns["seleccionar"](PETS, 3.5) == ["Limpieza de clientes", "Retrasos y cancelaciones"]
    assert ns["seleccionar"](PETS, 0.4) == []


def test_hidden_validacion_y_desempate(ns):
    """Entradas inválidas, no mutar la lista y desempates por esfuerzo y nombre (test oculto)"""
    f = ns["puntuacion_rice"]
    for args in [(100, 4, 0.8, 1), (100, 1, 0, 1), (100, 1, 1.2, 1), (100, 1, 0.8, 0)]:
        try:
            f(*args)
        except ValueError:
            continue
        raise AssertionError(f"Debe lanzar ValueError con {args}.")

    original = [dict(p) for p in PETS]
    ns["priorizar"](PETS)
    assert original == PETS and "rice" not in PETS[0]

    empate = [
        {"nombre": "B", "alcance": 100, "impacto": 1, "confianza": 1.0, "esfuerzo": 1},
        {"nombre": "A", "alcance": 200, "impacto": 1, "confianza": 1.0, "esfuerzo": 2},
        {"nombre": "C", "alcance": 50, "impacto": 2, "confianza": 1.0, "esfuerzo": 1},
    ]
    # Las tres puntúan 100: gana el de menor esfuerzo y, entre B y C, el nombre
    assert [p["nombre"] for p in ns["priorizar"](empate)] == ["B", "C", "A"]
    # Una petición grande que no cabe no bloquea a las siguientes
    cola = [
        {"nombre": "Grande", "alcance": 1000, "impacto": 3, "confianza": 1.0, "esfuerzo": 5},
        {"nombre": "Pequeña", "alcance": 10, "impacto": 1, "confianza": 1.0, "esfuerzo": 1},
    ]
    assert ns["seleccionar"](cola, 2) == ["Pequeña"]
