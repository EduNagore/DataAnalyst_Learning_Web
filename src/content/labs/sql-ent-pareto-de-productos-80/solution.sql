WITH r AS (
  SELECT oi.product_id, SUM(oi.quantity * oi.unit_price) AS ing
  FROM orders AS o JOIN order_items AS oi USING (order_id)
  WHERE o.status <> 'cancelado' AND year(o.order_date) = 2025
  GROUP BY 1
), c AS (
  SELECT ing / SUM(ing) OVER () AS part,
         SUM(ing) OVER (ORDER BY ing DESC, product_id) / SUM(ing) OVER () AS acum
  FROM r
)
SELECT COUNT(*) FILTER (WHERE acum - part < 0.8) AS productos_para_80,
       COUNT(*) AS productos_con_ventas,
       ROUND(100.0 * COUNT(*) FILTER (WHERE acum - part < 0.8) / COUNT(*), 1) AS pct
FROM c;
