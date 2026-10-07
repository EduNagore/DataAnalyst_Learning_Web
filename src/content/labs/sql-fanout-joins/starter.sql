-- Esta consulta suma el envío de los pedidos con productos de Electrónica,
-- pero la cifra sale inflada. Corrígela sin usar DISTINCT.
SELECT ROUND(SUM(o.shipping_cost), 2) AS envio_total
FROM orders AS o
JOIN order_items AS i ON i.order_id = o.order_id
JOIN products AS p ON p.product_id = i.product_id
JOIN categories AS sub ON sub.category_id = p.category_id
WHERE sub.parent_category_id = 'cat-00';
