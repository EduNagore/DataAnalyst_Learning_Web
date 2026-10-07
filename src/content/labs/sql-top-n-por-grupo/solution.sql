-- Ranking de clientes dentro de cada región y nos quedamos con el primero.
-- La ventana se calcula sobre el resultado agregado (SUM dentro del OVER).
SELECT c.region, o.customer_id, ROUND(SUM(oi.quantity * oi.unit_price)) AS gasto
FROM orders AS o
JOIN order_items AS oi USING (order_id)
JOIN customers AS c USING (customer_id)
WHERE o.status <> 'cancelado'
GROUP BY c.region, o.customer_id
QUALIFY ROW_NUMBER() OVER (PARTITION BY c.region ORDER BY SUM(oi.quantity * oi.unit_price) DESC, o.customer_id) = 1;
