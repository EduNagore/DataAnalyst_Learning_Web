-- Pedidos que NO se hicieron en store-01 (los online también cuentan).
SELECT COUNT(*) AS pedidos
FROM orders
WHERE store_id <> 'store-01';
