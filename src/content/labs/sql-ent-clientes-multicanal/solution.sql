SELECT COUNT(*) AS clientes_multicanal
FROM (
  SELECT customer_id
  FROM orders
  WHERE status <> 'cancelado'
  GROUP BY customer_id
  HAVING COUNT(DISTINCT channel) = 2
);
