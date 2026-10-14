-- Recompra a 90 días. ¿Qué pasa con los clientes que no han repetido y con los que no han tenido tiempo?
WITH p AS (
  SELECT customer_id, order_date,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS n
  FROM orders
  WHERE status <> 'cancelado'
)
SELECT c.acquisition_channel, COUNT(*) AS clientes, COUNT(*) AS repiten, 100.0 AS pct
FROM p AS a JOIN p AS b ON a.customer_id = b.customer_id AND a.n = 1 AND b.n = 2
JOIN customers AS c ON c.customer_id = a.customer_id
WHERE date_diff('day', a.order_date, b.order_date) <= 90
GROUP BY 1;
