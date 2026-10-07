"""Datos de referencia fijos: regiones, categorías, canales...

Los pesos de `REGIONS` son una aproximación ilustrativa a la distribución
real de población entre comunidades autónomas españolas, usada solo para
que la generación sintética tenga una distribución geográfica plausible;
no son una fuente demográfica exacta.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Region:
    name: str
    province: str
    weight: float


REGIONS: list[Region] = [
    Region("Andalucía", "Sevilla", 18),
    Region("Cataluña", "Barcelona", 16),
    Region("Madrid", "Madrid", 15),
    Region("Comunidad Valenciana", "Valencia", 10),
    Region("Galicia", "A Coruña", 6),
    Region("Castilla y León", "Valladolid", 5),
    Region("Canarias", "Las Palmas", 5),
    Region("País Vasco", "Bilbao", 5),
    Region("Castilla-La Mancha", "Toledo", 4),
    Region("Región de Murcia", "Murcia", 3),
    Region("Aragón", "Zaragoza", 3),
    Region("Illes Balears", "Palma", 3),
    Region("Extremadura", "Badajoz", 2),
    Region("Asturias", "Oviedo", 2),
    Region("Navarra", "Pamplona", 1.5),
    Region("Cantabria", "Santander", 1.5),
]

REGION_NAMES = [r.name for r in REGIONS]
REGION_WEIGHTS = [r.weight for r in REGIONS]
REGION_TO_PROVINCE = {r.name: r.province for r in REGIONS}

# 8 categorías de nivel superior x 5 subcategorías = 40 categorías.
CATEGORY_TREE: dict[str, list[str]] = {
    "Electrónica": [
        "Móviles y accesorios",
        "Informática",
        "Audio y sonido",
        "Televisores",
        "Pequeño electrodoméstico",
    ],
    "Hogar": ["Cocina", "Decoración", "Textil hogar", "Muebles", "Jardín"],
    "Moda": ["Ropa mujer", "Ropa hombre", "Calzado", "Complementos", "Ropa infantil"],
    "Deporte": ["Running", "Fitness", "Ciclismo", "Deportes de equipo", "Montaña"],
    "Belleza": [
        "Cuidado facial",
        "Cuidado corporal",
        "Maquillaje",
        "Perfumería",
        "Cuidado del cabello",
    ],
    "Alimentación": ["Despensa", "Bebidas", "Fresco", "Snacks", "Dietética"],
    "Juguetes y bebé": [
        "Juguetes",
        "Puericultura",
        "Ropa bebé",
        "Juegos educativos",
        "Primera infancia",
    ],
    "Papelería y oficina": [
        "Material escolar",
        "Oficina",
        "Libros",
        "Arte y manualidades",
        "Tecnología de oficina",
    ],
}

MARKETING_CHANNELS = ["paid_search", "paid_social", "email", "affiliate", "direct", "organic"]
ACQUISITION_CHANNELS = MARKETING_CHANNELS  # mismo vocabulario para customers.acquisition_channel

ORDER_CHANNELS = ["online", "store"]
DEVICES = ["mobile", "desktop", "tablet"]
CARRIERS = ["CorreosExpress", "SEUR", "MRW", "GLS", "Correos"]
CUSTOMER_SEGMENTS = ["nuevo", "ocasional", "habitual", "vip"]
CUSTOMER_SEGMENT_WEIGHTS = [0.35, 0.3, 0.25, 0.1]
ORDER_STATUSES = ["completado", "cancelado", "devuelto_parcial"]
ORDER_STATUS_WEIGHTS = [0.9, 0.04, 0.06]
RETURN_REASONS = [
    "no es lo esperado",
    "talla incorrecta",
    "producto defectuoso",
    "llegó tarde",
    "cambio de opinión",
    "artículo equivocado enviado",
]
SUBSCRIPTION_PLANS = ["mensual", "anual"]
BRANDS = [f"Marca {letter}" for letter in "ABCDEFGHIJKLMNOPQRST"]
