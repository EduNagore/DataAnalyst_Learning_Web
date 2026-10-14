WITH o AS (
  SELECT o.customer_id, o.order_id, o.order_date, SUM(oi.quantity * oi.unit_price) AS importe
  FROM orders AS o JOIN order_items AS oi USING (order_id)
  WHERE o.status <> 'cancelado'
  GROUP BY 1, 2, 3
), a AS (
  SELECT *, SUM(importe) OVER (PARTITION BY customer_id ORDER BY order_date, order_id) AS acumulado
  FROM o
)
SELECT year(order_date) AS anio, COUNT(*) AS clientes
FROM (
  SELECT customer_id, order_date FROM a
  WHERE acumulado >= 1000
  QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date, order_id) = 1
)
GROUP BY 1;
