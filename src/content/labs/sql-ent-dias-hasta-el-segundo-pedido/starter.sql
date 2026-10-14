-- Media de días entre pedidos... pero ¿entre cuáles?
WITH p AS (
  SELECT customer_id, order_date,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS n
  FROM orders
  WHERE status <> 'cancelado'
)
SELECT c.acquisition_channel, COUNT(*) AS clientes, ROUND(AVG(date_diff('day', a.order_date, b.order_date)), 1) AS dias_medios
FROM p AS a JOIN p AS b ON a.customer_id = b.customer_id AND b.n = a.n + 1
JOIN customers AS c ON c.customer_id = a.customer_id
GROUP BY 1;
