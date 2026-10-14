-- Pedidos con y sin descuento. Cuidado: un pedido tiene varias líneas.
SELECT CASE WHEN o.discount_pct > 0 THEN 'con_descuento' ELSE 'sin_descuento' END AS grupo,
       COUNT(*) AS pedidos,
       ROUND(AVG(oi.quantity * oi.unit_price), 2) AS ticket_medio,
       ROUND(AVG(oi.quantity), 2) AS unidades_por_pedido
FROM orders AS o JOIN order_items AS oi USING (order_id)
WHERE o.status <> 'cancelado'
GROUP BY 1;
