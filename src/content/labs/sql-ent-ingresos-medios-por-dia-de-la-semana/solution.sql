WITH d AS (
  SELECT CAST(o.order_date AS DATE) AS dia, SUM(oi.quantity * oi.unit_price) AS ingresos
  FROM orders AS o JOIN order_items AS oi USING (order_id)
  WHERE o.status <> 'cancelado' AND year(o.order_date) = 2025
  GROUP BY 1
)
SELECT isodow(dia) AS dia_semana, COUNT(*) AS dias, ROUND(AVG(ingresos), 0) AS ingresos_medios
FROM d
GROUP BY 1;
