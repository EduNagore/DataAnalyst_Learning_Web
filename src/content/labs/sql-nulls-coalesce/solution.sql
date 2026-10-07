-- IS DISTINCT FROM es "distinto de" tratando NULL como un valor más:
-- los pedidos online (store_id NULL) sí son distintos de 'store-01'.
SELECT COUNT(*) AS pedidos
FROM orders
WHERE store_id IS DISTINCT FROM 'store-01';
