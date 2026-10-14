-- Reactivaciones: ojo, aquí miras desde el primer pedido, no desde el anterior.
WITH p AS (
  SELECT customer_id, order_date, MIN(order_date) OVER (PARTITION BY customer_id) AS primero
  FROM orders
  WHERE status <> 'cancelado'
)
SELECT year(order_date) AS anio, COUNT(*) AS reactivaciones, COUNT(DISTINCT customer_id) AS clientes
FROM p
WHERE date_diff('day', primero, order_date) >= 180
GROUP BY 1;
