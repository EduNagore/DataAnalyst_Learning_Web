-- Compras (event_type = 'purchase') del 30 de junio de 2026 en HORA DE MADRID.
-- Ojo: así cuenta por fecha UTC, que no es la del negocio.
SELECT COUNT(*) AS compras
FROM events
WHERE event_type = 'purchase'
  AND CAST(occurred_at AS DATE) = DATE '2026-06-30';
