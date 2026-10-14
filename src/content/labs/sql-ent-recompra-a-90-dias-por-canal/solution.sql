WITH p AS (
  SELECT customer_id, order_date,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS n
  FROM orders
  WHERE status <> 'cancelado'
), f AS (
  SELECT a.customer_id,
         COALESCE(date_diff('day', a.order_date, b.order_date) <= 90, FALSE) AS repite
  FROM p AS a LEFT JOIN p AS b ON a.customer_id = b.customer_id AND b.n = 2
  WHERE a.n = 1 AND a.order_date < TIMESTAMP '2026-04-01'
)
SELECT c.acquisition_channel, COUNT(*) AS clientes, SUM(f.repite::INT) AS repiten,
       ROUND(100.0 * AVG(f.repite::INT), 1) AS pct
FROM f JOIN customers AS c USING (customer_id)
GROUP BY 1;
