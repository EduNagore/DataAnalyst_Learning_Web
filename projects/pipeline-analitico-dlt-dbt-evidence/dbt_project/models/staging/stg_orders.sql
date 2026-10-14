-- Staging de pedidos: renombrado, tipos y limpieza mínima. Sin lógica de negocio.
-- TODO: ¿qué columnas necesitas? ¿qué tipo tiene order_date? ¿hay que normalizar status?
select
    order_id,
    customer_id,
    cast(order_date as timestamp) as ordered_at,
    channel,
    status,
    discount_pct,
    shipping_cost
from {{ source('raw', 'orders') }}
