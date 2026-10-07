-- Detalle por año y canal (faltan los subtotales y el total).
-- Columnas esperadas: anio, channel, ingresos_m
SELECT YEAR(o.order_date) AS anio, o.channel,
       ROUND(SUM(oi.quantity * oi.unit_price) / 1e6, 2) AS ingresos_m
FROM orders AS o
JOIN order_items AS oi USING (order_id)
WHERE o.status <> 'cancelado'
GROUP BY anio, o.channel
ORDER BY anio, o.channel;
