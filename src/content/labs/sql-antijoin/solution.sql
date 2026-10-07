-- Anti-join: LEFT JOIN y nos quedamos con los clientes sin pareja en orders.
-- (NOT EXISTS sería equivalente; NOT IN fallaría si orders.customer_id tuviera NULL.)
SELECT c.region, COUNT(*) AS sin_pedidos
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL
GROUP BY c.region;
