-- Date spine: el calendario manda (izquierda del LEFT JOIN) y los huecos se rellenan con 0.
SELECT CAST(s.d AS DATE) AS dia, COALESCE(o.pedidos, 0) AS pedidos
FROM generate_series(DATE '2023-01-01', DATE '2023-01-15', INTERVAL 1 DAY) AS s(d)
LEFT JOIN (
  SELECT order_date, COUNT(*) AS pedidos FROM orders GROUP BY order_date
) AS o ON o.order_date = s.d
ORDER BY dia;
