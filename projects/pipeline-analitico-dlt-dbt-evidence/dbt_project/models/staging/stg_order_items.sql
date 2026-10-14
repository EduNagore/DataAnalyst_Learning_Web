-- TODO: staging de líneas de pedido (grano: una fila por línea).
select
    order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price
from {{ source('raw', 'order_items') }}
