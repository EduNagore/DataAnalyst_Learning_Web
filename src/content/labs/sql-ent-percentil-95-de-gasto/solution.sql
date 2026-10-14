WITH g AS (
  SELECT o.customer_id, SUM(oi.quantity * oi.unit_price) AS gasto
  FROM orders AS o JOIN order_items AS oi USING (order_id)
  WHERE o.status <> 'cancelado'
  GROUP BY 1
)
SELECT c.segment, COUNT(*) AS clientes,
       ROUND(quantile_cont(g.gasto, 0.5), 0) AS mediana,
       ROUND(quantile_cont(g.gasto, 0.95), 0) AS p95
FROM g JOIN customers AS c USING (customer_id)
GROUP BY 1;
