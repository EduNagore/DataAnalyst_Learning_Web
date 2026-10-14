-- Pedidos por estado. Falta el porcentaje sobre el total.
SELECT status, COUNT(*) AS pedidos
FROM orders
GROUP BY status;
