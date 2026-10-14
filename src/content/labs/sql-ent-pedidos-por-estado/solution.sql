SELECT status, COUNT(*) AS pedidos,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM orders
GROUP BY status;
