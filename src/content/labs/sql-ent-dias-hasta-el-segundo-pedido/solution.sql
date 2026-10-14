WITH p AS (
  SELECT customer_id, order_date,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS n
  FROM orders
  WHERE status <> 'cancelado'
), d AS (
  SELECT a.customer_id, date_diff('day', a.order_date, b.order_date) AS dias
  FROM p AS a JOIN p AS b ON a.customer_id = b.customer_id AND a.n = 1 AND b.n = 2
)
SELECT c.acquisition_channel, COUNT(*) AS clientes, ROUND(AVG(d.dias), 1) AS dias_medios
FROM d JOIN customers AS c USING (customer_id)
GROUP BY 1;
