SELECT COALESCE(par.name, c.name) AS categoria,
       ROUND(SUM(oi.quantity * oi.unit_price), 0) AS ingresos,
       ROUND(SUM(oi.quantity * p.cost), 0) AS coste,
       ROUND(100.0 * (SUM(oi.quantity * oi.unit_price) - SUM(oi.quantity * p.cost)) / SUM(oi.quantity * oi.unit_price), 1) AS margen_pct
FROM order_items AS oi
JOIN orders AS o USING (order_id)
JOIN products AS p USING (product_id)
JOIN categories AS c ON c.category_id = p.category_id
LEFT JOIN categories AS par ON par.category_id = c.parent_category_id
WHERE o.status <> 'cancelado' AND year(o.order_date) = 2025
GROUP BY 1;
