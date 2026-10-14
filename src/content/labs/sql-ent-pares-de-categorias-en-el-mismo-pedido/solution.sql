WITH cp AS (
  SELECT DISTINCT oi.order_id, COALESCE(par.name, c.name) AS cat
  FROM order_items AS oi
  JOIN orders AS o USING (order_id)
  JOIN products AS p USING (product_id)
  JOIN categories AS c ON c.category_id = p.category_id
  LEFT JOIN categories AS par ON par.category_id = c.parent_category_id
  WHERE o.status <> 'cancelado' AND year(o.order_date) = 2025
)
SELECT a.cat AS categoria_a, b.cat AS categoria_b, COUNT(*) AS pedidos
FROM cp AS a JOIN cp AS b ON a.order_id = b.order_id AND a.cat < b.cat
GROUP BY 1, 2
ORDER BY pedidos DESC, 1, 2
LIMIT 5;
