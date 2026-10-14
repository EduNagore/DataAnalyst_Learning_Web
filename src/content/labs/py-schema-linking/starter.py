import re
import unicodedata

ESQUEMA = {
    "orders": ["order_id", "customer_id", "order_date", "channel", "device", "discount_pct", "shipping_cost", "status", "store_id"],
    "order_items": ["order_item_id", "order_id", "product_id", "quantity", "unit_price"],
    "products": ["product_id", "category_id", "name", "price", "cost", "brand"],
    "categories": ["category_id", "parent_category_id", "name"],
    "customers": ["customer_id", "signup_date", "acquisition_channel", "region", "province", "segment", "marketing_consent"],
    "returns": ["return_id", "order_item_id", "return_date", "reason"],
    "shipments": ["shipment_id", "order_id", "promised_date", "actual_date", "carrier"],
    "subscriptions": ["subscription_id", "customer_id", "plan", "started_at", "cancelled_at", "mrr_eur"],
    "support_tickets": ["ticket_id", "customer_id", "created_at", "category", "text", "label"],
}

# Descripciones en lenguaje de negocio (lo que una capa semántica o un diccionario de datos aportaría)
DESCRIPCIONES = {
    "orders.order_id": "pedido identificador número de pedidos",
    "orders.order_date": "fecha del pedido día mes año cuándo se compró",
    "orders.channel": "canal de venta online tienda",
    "orders.device": "dispositivo móvil escritorio tablet",
    "orders.discount_pct": "descuento aplicado porcentaje",
    "orders.shipping_cost": "coste de envío gastos de transporte",
    "orders.status": "estado del pedido completado cancelado devuelto",
    "order_items.quantity": "cantidad unidades vendidas",
    "order_items.unit_price": "precio unitario importe venta ingresos facturación",
    "order_items.product_id": "producto vendido artículo",
    "products.category_id": "categoría del producto",
    "products.name": "nombre del producto",
    "products.cost": "coste del producto margen beneficio",
    "products.brand": "marca fabricante",
    "categories.name": "nombre de la categoría familia de productos",
    "customers.region": "región comunidad autónoma del cliente",
    "customers.segment": "segmento del cliente vip habitual ocasional nuevo",
    "customers.marketing_consent": "consentimiento de marketing comunicaciones comerciales permiso",
    "customers.customer_id": "cliente identificador número de clientes",
    "customers.acquisition_channel": "canal de adquisición origen del cliente",
    "returns.reason": "motivo de la devolución razón",
    "returns.return_date": "fecha de devolución",
    "shipments.promised_date": "fecha de entrega prometida",
    "shipments.actual_date": "fecha de entrega real llegada retraso",
    "shipments.carrier": "transportista empresa de reparto",
    "subscriptions.mrr_eur": "ingreso mensual recurrente mrr suscripción euros",
    "subscriptions.plan": "plan de suscripción mensual anual",
    "subscriptions.cancelled_at": "fecha de baja cancelación activa vigente",
    "support_tickets.category": "categoría del ticket de soporte tema consulta",
    "support_tickets.created_at": "fecha de creación del ticket cuándo se abrió",
    "support_tickets.ticket_id": "ticket de soporte incidencia identificador",
}

PARADAS = {"de", "del", "la", "el", "los", "las", "un", "una", "por", "en", "que", "con", "y", "a", "al", "se", "su", "sus", "es", "mas", "cuantos", "cuantas", "cual", "cuales", "hubo", "hay", "ultimo"}

PREGUNTAS_ORO = [
    ("¿Cuántos pedidos no cancelados hubo por canal en 2025?", {"orders.order_id", "orders.status", "orders.channel", "orders.order_date"}),
    ("Ingresos por categoría de producto", {"order_items.quantity", "order_items.unit_price", "products.category_id", "categories.name"}),
    ("¿Qué porcentaje de entregas llega con retraso por transportista?", {"shipments.promised_date", "shipments.actual_date", "shipments.carrier"}),
    ("MRR de las suscripciones activas por plan", {"subscriptions.mrr_eur", "subscriptions.plan", "subscriptions.cancelled_at"}),
    ("Motivos de devolución más frecuentes", {"returns.reason"}),
    ("Clientes por región y segmento con consentimiento de marketing", {"customers.region", "customers.segment", "customers.marketing_consent", "customers.customer_id"}),
    ("Tickets de soporte por categoría en el último mes", {"support_tickets.category", "support_tickets.created_at", "support_tickets.ticket_id"}),
    ("Margen bruto por marca", {"order_items.quantity", "order_items.unit_price", "products.cost", "products.brand"}),
]


def normalizar(texto: str) -> set[str]:
    """Conjunto de tokens normalizados: minúsculas, sin tildes, solo [a-z0-9], sin palabras vacías (PARADAS) y con
    una raíz sencilla: si el token tiene más de 4 letras y acaba en «es», se le quita «es»; si no, si tiene más de 3
    letras y acaba en «s», se le quita la «s»."""
    # TODO
    ...


def documento(tabla: str, columna: str, descripciones: dict | None) -> set[str]:
    """Tokens que describen una columna: los de su nombre (separando por «_»), los de su tabla y, si hay, los de su descripción."""
    # TODO
    ...


def enlazar(pregunta: str, esquema: dict, descripciones: dict | None, k: int) -> list[str]:
    """Las `k` columnas «tabla.columna» más relacionadas con la pregunta: puntuación = nº de tokens de la pregunta que
    aparecen en el documento de la columna. Solo se devuelven columnas con puntuación > 0; empates, por orden en el esquema."""
    # TODO
    ...


def recall_en_k(oro: list, esquema: dict, descripciones: dict | None, k: int) -> float:
    """Recall medio: para cada pregunta, la fracción de las columnas necesarias que aparecen entre las `k` primeras enlazadas;
    después, la media sobre todas las preguntas."""
    # TODO
    ...


for k in (4, 6, 8):
    print(f"k={k}: solo nombres {recall_en_k(PREGUNTAS_ORO, ESQUEMA, None, k):.3f} | con descripciones {recall_en_k(PREGUNTAS_ORO, ESQUEMA, DESCRIPCIONES, k):.3f}")
print(enlazar(PREGUNTAS_ORO[1][0], ESQUEMA, DESCRIPCIONES, 6))
