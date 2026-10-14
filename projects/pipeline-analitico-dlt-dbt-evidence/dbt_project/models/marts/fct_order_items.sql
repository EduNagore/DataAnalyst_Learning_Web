-- Hecho de líneas de pedido. Grano: UNA FILA POR LÍNEA DE PEDIDO (decláralo en _models.yml).
-- TODO: une con stg_orders para traer fecha, canal y cliente; excluye cancelados; calcula el importe.
select
    i.order_item_id,
    o.order_id,
    o.customer_id,
    o.ordered_at,
    o.channel,
    i.product_id,
    i.quantity,
    i.quantity * i.unit_price as revenue
from {{ ref('stg_order_items') }} as i
join {{ ref('stg_orders') }} as o using (order_id)
where o.status <> 'cancelado'
