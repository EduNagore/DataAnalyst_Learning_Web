"""Diccionario de datos de Lumen, para `/datos/` (ver docs/DATASET.md).

Es la fuente de verdad *humana* de qué significa cada columna; `build.py`
comprueba en tiempo de generación que coincide exactamente con las
columnas que de verdad produce cada builder, para que nunca se desincronice
en silencio.
"""

SCHEMA: dict[str, dict] = {
    "customers": {
        "description": "Clientes de Lumen, con su canal de adquisición y segmento.",
        "columns": {
            "customer_id": "Identificador único del cliente.",
            "signup_date": "Fecha de alta.",
            "acquisition_channel": "Canal de marketing por el que llegó.",
            "region": "Comunidad autónoma.",
            "province": "Provincia (representativa de la región).",
            "segment": "Segmento asignado por CRM: nuevo, ocasional, habitual, vip.",
            "marketing_consent": "Si ha dado consentimiento de marketing.",
        },
    },
    "categories": {
        "description": "Árbol de categorías de producto (2 niveles).",
        "columns": {
            "category_id": "Identificador de categoría.",
            "parent_category_id": "Categoría padre (nulo en el nivel superior).",
            "name": "Nombre de la categoría.",
        },
    },
    "products": {
        "description": "Catálogo de productos.",
        "columns": {
            "product_id": "Identificador de producto.",
            "category_id": "Subcategoría a la que pertenece.",
            "name": "Nombre del producto.",
            "price": "Precio de venta (EUR, antes de descuentos).",
            "cost": "Coste (EUR).",
            "brand": "Marca.",
        },
    },
    "stores": {
        "description": "Tiendas físicas.",
        "columns": {
            "store_id": "Identificador de tienda.",
            "city": "Ciudad.",
            "region": "Comunidad autónoma.",
            "size_m2": "Superficie en metros cuadrados.",
            "opened_date": "Fecha de apertura.",
        },
    },
    "orders": {
        "description": "Pedidos (online y en tienda).",
        "columns": {
            "order_id": "Identificador de pedido.",
            "customer_id": "Cliente que hizo el pedido.",
            "order_date": "Fecha del pedido (UTC).",
            "channel": "online o store.",
            "device": "mobile, desktop o tablet (n/a si es en tienda).",
            "discount_pct": "Descuento aplicado (0-1).",
            "shipping_cost": "Coste de envío (EUR, 0 si es en tienda).",
            "status": "completado, cancelado o devuelto_parcial.",
            "store_id": "Tienda (nulo si el pedido es online).",
        },
    },
    "order_items": {
        "description": "Líneas de pedido.",
        "columns": {
            "order_item_id": "Identificador de línea de pedido.",
            "order_id": "Pedido al que pertenece.",
            "product_id": "Producto comprado.",
            "quantity": "Cantidad.",
            "unit_price": "Precio unitario final (ya con descuento aplicado).",
        },
    },
    "returns": {
        "description": "Devoluciones de líneas de pedido.",
        "columns": {
            "return_id": "Identificador de devolución.",
            "order_item_id": "Línea de pedido devuelta.",
            "return_date": "Fecha de la devolución.",
            "reason": "Motivo declarado.",
        },
    },
    "shipments": {
        "description": "Envíos de pedidos online.",
        "columns": {
            "shipment_id": "Identificador de envío.",
            "order_id": "Pedido al que corresponde.",
            "promised_date": "Fecha de entrega prometida.",
            "actual_date": "Fecha de entrega real.",
            "carrier": "Transportista.",
        },
    },
    "inventory_snapshots": {
        "description": "Fotos semanales de stock por producto y centro de distribución.",
        "columns": {
            "snapshot_date": "Fecha de la foto (siempre un lunes).",
            "product_id": "Producto.",
            "location_id": "Centro de distribución (dc-00..dc-03).",
            "stock_qty": "Unidades en stock.",
        },
    },
    "web_sessions": {
        "description": "Sesiones web/app, convertidas o no.",
        "columns": {
            "session_id": "Identificador de sesión.",
            "customer_id": "Cliente (nulo si la sesión es anónima).",
            "started_at": "Inicio de la sesión (UTC).",
            "device": "mobile, desktop o tablet.",
            "channel": "Canal de marketing de origen.",
            "region": "Comunidad autónoma del visitante.",
            "app_version": "Versión de la app (solo sesiones mobile).",
        },
    },
    "events": {
        "description": "Eventos del funnel por sesión (muestra, no exhaustiva).",
        "columns": {
            "event_id": "Identificador de evento.",
            "session_id": "Sesión a la que pertenece.",
            "event_type": "page_view, add_to_cart, checkout o purchase.",
            "occurred_at": "Momento del evento (UTC).",
            "app_version": "Versión de la app en ese momento (sesiones mobile).",
            "properties": "Propiedades adicionales del evento (JSON como texto).",
        },
    },
    "marketing_spend": {
        "description": "Inversión de marketing diaria por canal.",
        "columns": {
            "date": "Fecha.",
            "channel": "Canal de marketing.",
            "spend_eur": "Inversión (EUR).",
        },
    },
    "campaigns": {
        "description": "Campañas de marketing.",
        "columns": {
            "campaign_id": "Identificador de campaña.",
            "channel": "Canal en el que corre.",
            "start_date": "Fecha de inicio.",
            "end_date": "Fecha de fin.",
            "budget_eur": "Presupuesto total (EUR).",
        },
    },
    "experiments": {
        "description": "Experimentos A/B.",
        "columns": {
            "experiment_id": "Identificador del experimento.",
            "name": "Nombre descriptivo.",
            "start_date": "Fecha de inicio.",
            "end_date": "Fecha de fin.",
            "primary_metric": "Métrica principal del experimento.",
        },
    },
    "experiment_assignments": {
        "description": "Asignación de clientes a variantes de experimento.",
        "columns": {
            "experiment_id": "Experimento.",
            "customer_id": "Cliente asignado.",
            "variant": "control o tratamiento.",
        },
    },
    "experiment_metrics": {
        "description": "Métricas diarias por variante de experimento.",
        "columns": {
            "experiment_id": "Experimento.",
            "date": "Fecha.",
            "variant": "control o tratamiento.",
            "metric_name": "Nombre de la métrica.",
            "value": "Valor de la métrica ese día.",
        },
    },
    "subscriptions": {
        "description": "Suscripciones a Lumen+.",
        "columns": {
            "subscription_id": "Identificador de suscripción.",
            "customer_id": "Cliente suscrito.",
            "plan": "mensual o anual.",
            "started_at": "Fecha de alta.",
            "cancelled_at": "Fecha de baja (nulo si sigue activa).",
            "mrr_eur": "Ingreso mensual recurrente (EUR).",
        },
    },
    "support_tickets": {
        "description": "Tickets de atención al cliente, con texto libre en español.",
        "columns": {
            "ticket_id": "Identificador de ticket.",
            "customer_id": "Cliente que lo abrió.",
            "created_at": "Fecha de apertura.",
            "category": "Tema del ticket (envio, devoluciones, app, pagos, producto).",
            "text": "Texto libre del ticket.",
            "label": "Etiqueta asignada a mano (solo en una muestra; nulo en el resto).",
        },
    },
    "calendar": {
        "description": "Calendario de festivos y eventos comerciales.",
        "columns": {
            "date": "Fecha.",
            "is_holiday_national": "Si es festivo nacional.",
            "national_holiday_name": "Nombre del festivo nacional.",
            "is_holiday_regional": "Si es festivo regional (simplificado, ver docs/DATASET.md).",
            "regional_holiday_name": "Nombre del festivo regional.",
            "regional_holiday_region": "Región a la que aplica el festivo regional.",
            "is_sale_event": "Si cae en un periodo comercial (rebajas, Black Friday, Navidad).",
            "sale_event_name": "Nombre del periodo comercial.",
            "demand_multiplier": (
                "Multiplicador de demanda usado para generar el dataset "
                "(no es un dato real, es metadato del generador)."
            ),
        },
    },
}
