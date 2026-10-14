SELECT CASE WHEN o.discount_pct > 0 THEN 'con_descuento' ELSE 'sin_descuento' END AS grupo,
       COUNT(DISTINCT o.order_id) AS pedidos,
       ROUND(SUM(oi.quantity * oi.unit_price) / COUNT(DISTINCT o.order_id), 2) AS ticket_medio,
       ROUND(SUM(oi.quantity) * 1.0 / COUNT(DISTINCT o.order_id), 2) AS unidades_por_pedido
FROM orders AS o JOIN order_items AS oi USING (order_id)
WHERE o.status <> 'cancelado'
GROUP BY 1;
