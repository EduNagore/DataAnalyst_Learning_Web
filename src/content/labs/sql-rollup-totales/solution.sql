-- ROLLUP añade el subtotal por año (channel NULL) y el total general (ambos NULL).
SELECT YEAR(o.order_date) AS anio, o.channel,
       ROUND(SUM(oi.quantity * oi.unit_price) / 1e6, 2) AS ingresos_m
FROM orders AS o
JOIN order_items AS oi USING (order_id)
WHERE o.status <> 'cancelado'
GROUP BY ROLLUP(anio, o.channel)
ORDER BY anio, o.channel;
