SELECT i.product_id, p.name, SUM(i.stock_qty) AS stock_total
FROM inventory_snapshots AS i
JOIN products AS p USING (product_id)
WHERE i.snapshot_date = (SELECT MAX(snapshot_date) FROM inventory_snapshots)
GROUP BY i.product_id, p.name
ORDER BY stock_total, i.product_id
LIMIT 10;
