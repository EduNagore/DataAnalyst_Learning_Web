-- La ventana se calcula en un CTE con TODOS los meses, y el periodo se filtra después:
-- así el LAG de enero puede ver diciembre.
WITH mensual AS (
  SELECT DATE_TRUNC('month', o.order_date) AS mes, SUM(oi.quantity * oi.unit_price) AS ingresos
  FROM orders AS o
  JOIN order_items AS oi USING (order_id)
  WHERE o.status <> 'cancelado'
  GROUP BY mes
),
con_crecimiento AS (
  SELECT mes, ingresos, 100 * (ingresos / LAG(ingresos) OVER (ORDER BY mes) - 1) AS crecimiento
  FROM mensual
)
SELECT STRFTIME(mes, '%Y-%m') AS mes,
       ROUND(ingresos / 1e6, 2) AS ingresos_m,
       ROUND(crecimiento, 1) AS crecimiento_pct
FROM con_crecimiento
WHERE mes >= DATE '2025-01-01' AND mes < DATE '2025-07-01'
ORDER BY mes;
