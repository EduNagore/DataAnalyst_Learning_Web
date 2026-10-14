SELECT p.product_id, p.name, COUNT(*) AS devoluciones
FROM returns AS r
JOIN order_items AS oi USING (order_item_id)
JOIN products AS p USING (product_id)
GROUP BY p.product_id, p.name
ORDER BY devoluciones DESC, p.product_id
LIMIT 5;
