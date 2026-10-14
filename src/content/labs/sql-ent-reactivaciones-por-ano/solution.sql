WITH p AS (
  SELECT customer_id, order_date,
         LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS anterior
  FROM orders
  WHERE status <> 'cancelado'
)
SELECT year(order_date) AS anio, COUNT(*) AS reactivaciones, COUNT(DISTINCT customer_id) AS clientes
FROM p
WHERE date_diff('day', anterior, order_date) >= 180
GROUP BY 1;
