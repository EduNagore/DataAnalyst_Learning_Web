-- Ingresos por mes y crecimiento frente al mes anterior (enero a junio de 2025).
-- Columnas esperadas: mes, ingresos_m, crecimiento_pct
SELECT STRFTIME(DATE_TRUNC('month', o.order_date), '%Y-%m') AS mes,
       ROUND(SUM(oi.quantity * oi.unit_price) / 1e6, 2) AS ingresos_m
FROM orders AS o
JOIN order_items AS oi USING (order_id)
WHERE o.status <> 'cancelado'
GROUP BY mes
ORDER BY mes;
