-- 15 filas (1 al 15 de enero de 2023), con 0 en los días sin pedidos.
-- Columnas esperadas: dia, pedidos
SELECT order_date AS dia, COUNT(*) AS pedidos
FROM orders
WHERE order_date >= DATE '2023-01-01' AND order_date <= DATE '2023-01-15'
GROUP BY order_date
ORDER BY dia;
