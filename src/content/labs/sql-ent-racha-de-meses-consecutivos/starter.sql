-- Rachas de meses consecutivos. Aquí solo cuentas meses con compra, no si son seguidos.
WITH m AS (
  SELECT DISTINCT customer_id, CAST(date_trunc('month', order_date) AS DATE) AS mes
  FROM orders
  WHERE status <> 'cancelado'
)
SELECT COUNT(*) FILTER (WHERE meses >= 3) AS clientes_con_racha_3, MAX(meses) AS racha_maxima
FROM (SELECT customer_id, COUNT(*) AS meses FROM m GROUP BY 1);
