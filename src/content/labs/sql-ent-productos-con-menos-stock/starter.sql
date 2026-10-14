-- Productos con menos stock. ¿De qué fecha?
SELECT i.product_id, p.name, SUM(i.stock_qty) AS stock_total
FROM inventory_snapshots AS i
JOIN products AS p USING (product_id)
GROUP BY i.product_id, p.name
ORDER BY stock_total, i.product_id
LIMIT 10;
