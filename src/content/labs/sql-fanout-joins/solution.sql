-- El envío es un dato del pedido: filtramos pedidos con EXISTS en vez de unir
-- las líneas, así cada pedido aparece una sola vez y su envío se suma una vez.
SELECT ROUND(SUM(o.shipping_cost), 2) AS envio_total
FROM orders AS o
WHERE EXISTS (
  SELECT 1
  FROM order_items AS i
  JOIN products   AS p   ON p.product_id = i.product_id
  JOIN categories AS sub ON sub.category_id = p.category_id
  WHERE i.order_id = o.order_id
    AND sub.parent_category_id = 'cat-00'
);
