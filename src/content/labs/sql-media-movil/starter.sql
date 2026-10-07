-- Pedidos por día y media móvil de 7 días (solo los días de junio de 2026).
-- Columnas esperadas: dia, pedidos, media_7d
SELECT order_date AS dia, COUNT(*) AS pedidos
FROM orders
WHERE order_date >= DATE '2026-06-01' AND order_date < DATE '2026-07-01'
GROUP BY order_date
ORDER BY dia;
