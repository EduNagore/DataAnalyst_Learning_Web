-- Ingresos por día de la semana. ¿Total o media del día típico?
SELECT isodow(o.order_date) AS dia_semana, COUNT(DISTINCT CAST(o.order_date AS DATE)) AS dias,
       ROUND(SUM(oi.quantity * oi.unit_price), 0) AS ingresos_medios
FROM orders AS o JOIN order_items AS oi USING (order_id)
WHERE o.status <> 'cancelado' AND year(o.order_date) = 2025
GROUP BY 1;
