-- Tasa de devolución por categoría. Falta la jerarquía y el LEFT JOIN.
SELECT c.name AS categoria,
       COUNT(*) AS lineas,
       COUNT(r.return_id) AS devueltas,
       ROUND(100.0 * COUNT(r.return_id) / COUNT(*), 1) AS tasa_pct
FROM order_items AS oi
JOIN orders AS o USING (order_id)
JOIN products AS p USING (product_id)
JOIN categories AS c ON c.category_id = p.category_id
JOIN returns AS r ON r.order_item_id = oi.order_item_id
WHERE o.status <> 'cancelado'
GROUP BY 1;
