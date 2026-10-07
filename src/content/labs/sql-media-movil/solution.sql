-- ROWS BETWEEN 6 PRECEDING cuenta 7 filas (hay un día por fila, sin huecos).
-- Se filtra junio DESPUÉS de calcular la ventana para que use los días de mayo.
WITH diario AS (
  SELECT order_date AS dia, COUNT(*) AS pedidos FROM orders GROUP BY order_date
),
suavizado AS (
  SELECT dia, pedidos,
         ROUND(AVG(pedidos) OVER (ORDER BY dia ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 1) AS media_7d
  FROM diario
)
SELECT dia, pedidos, media_7d
FROM suavizado
WHERE dia >= DATE '2026-06-01' AND dia < DATE '2026-07-01'
ORDER BY dia;
