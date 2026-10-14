-- Clientes con pedidos en los dos canales.
SELECT COUNT(*) AS clientes_multicanal
FROM (
  SELECT customer_id
  FROM orders
  GROUP BY customer_id
  HAVING COUNT(channel) = 2
);
