-- Ticket medio por canal: ¿qué estás promediando, pedidos o líneas?
SELECT o.channel, COUNT(DISTINCT o.order_id) AS pedidos,
       ROUND(AVG(oi.quantity * oi.unit_price), 2) AS ticket_medio
FROM orders AS o
JOIN order_items AS oi USING (order_id)
WHERE o.status <> 'cancelado'
GROUP BY o.channel;
