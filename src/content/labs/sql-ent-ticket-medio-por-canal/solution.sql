SELECT o.channel, COUNT(DISTINCT o.order_id) AS pedidos,
       ROUND(SUM(oi.quantity * oi.unit_price) / COUNT(DISTINCT o.order_id), 2) AS ticket_medio
FROM orders AS o
JOIN order_items AS oi USING (order_id)
WHERE o.status <> 'cancelado'
GROUP BY o.channel;
