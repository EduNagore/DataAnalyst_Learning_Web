-- Compras reales (sesiones con evento purchase) entre el 10 y el 24 de noviembre de 2024.
SELECT COUNT(*) AS compras
FROM events
WHERE event_type = 'purchase'
  AND occurred_at >= TIMESTAMP '2024-11-10'
  AND occurred_at <  TIMESTAMP '2024-11-25';
