-- Una fila por región: el cliente que más ha gastado.
-- Columnas esperadas: region, customer_id, gasto
SELECT c.region, ROUND(SUM(oi.quantity * oi.unit_price)) AS gasto
FROM orders AS o
JOIN order_items AS oi USING (order_id)
JOIN customers AS c USING (customer_id)
WHERE o.status <> 'cancelado'
GROUP BY c.region;
