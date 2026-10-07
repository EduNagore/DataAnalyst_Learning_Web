-- Clientes sin ningún pedido, por región.
-- Columnas esperadas: region, sin_pedidos
SELECT c.region, COUNT(*) AS sin_pedidos
FROM customers AS c
GROUP BY c.region;
