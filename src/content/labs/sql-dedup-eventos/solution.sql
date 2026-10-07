-- La unidad de análisis es la sesión: contar sesiones distintas descarta los eventos duplicados.
SELECT COUNT(DISTINCT session_id) AS compras
FROM events
WHERE event_type = 'purchase'
  AND occurred_at >= TIMESTAMP '2024-11-10'
  AND occurred_at <  TIMESTAMP '2024-11-25';
