-- Filtramos el año con un límite semiabierto (>= inicio, < inicio del año siguiente):
-- así no depende de si la columna tiene hora y no se pierde el 31 de diciembre.
SELECT channel, COUNT(*) AS pedidos
FROM orders
WHERE order_date >= DATE '2025-01-01'
  AND order_date <  DATE '2026-01-01'
GROUP BY channel
ORDER BY channel;
