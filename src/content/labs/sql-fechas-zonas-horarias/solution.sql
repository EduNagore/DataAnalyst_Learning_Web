-- 1) Declaramos que el valor ingenuo está en UTC; 2) lo pasamos a hora de Madrid;
-- 3) nos quedamos con la fecha local.
SELECT COUNT(*) AS compras
FROM events
WHERE event_type = 'purchase'
  AND CAST(TIMEZONE('Europe/Madrid', TIMEZONE('UTC', occurred_at)) AS DATE) = DATE '2026-06-30';
