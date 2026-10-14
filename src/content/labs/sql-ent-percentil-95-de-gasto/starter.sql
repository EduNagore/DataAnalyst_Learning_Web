-- Percentiles por segmento: ¿del gasto por cliente o del importe de cada línea?
SELECT c.segment, COUNT(DISTINCT o.customer_id) AS clientes,
       ROUND(quantile_cont(oi.quantity * oi.unit_price, 0.5), 0) AS mediana,
       ROUND(quantile_cont(oi.quantity * oi.unit_price, 0.95), 0) AS p95
FROM orders AS o JOIN order_items AS oi USING (order_id)
JOIN customers AS c USING (customer_id)
WHERE o.status <> 'cancelado'
GROUP BY 1;
