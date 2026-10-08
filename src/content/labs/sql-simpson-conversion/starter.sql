-- Conversión por dispositivo, solo agregada (Madrid + Andalucía).
-- Columnas esperadas: region, device, sesiones, compras, conversion_pct
-- Añade el desglose por región (las filas agregadas llevan region = 'Ambas').
WITH compradores AS (
  SELECT DISTINCT session_id FROM events WHERE event_type = 'purchase'
),
sesiones AS (
  SELECT ws.region, ws.device, (c.session_id IS NOT NULL)::INT AS compra
  FROM web_sessions AS ws
  LEFT JOIN compradores AS c ON c.session_id = ws.session_id
  WHERE ws.region IN ('Madrid', 'Andalucía') AND ws.device IN ('mobile', 'desktop')
)
SELECT 'Ambas' AS region, device, COUNT(*) AS sesiones, SUM(compra) AS compras,
       ROUND(100.0 * SUM(compra) / COUNT(*), 1) AS conversion_pct
FROM sesiones
GROUP BY device;
