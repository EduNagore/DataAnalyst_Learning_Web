-- Una sesión convierte si tiene algún evento 'purchase' (DISTINCT: ignora eventos duplicados).
WITH compradores AS (
  SELECT DISTINCT session_id FROM events WHERE event_type = 'purchase'
),
sesiones AS (
  SELECT ws.region, ws.device, (c.session_id IS NOT NULL)::INT AS compra
  FROM web_sessions AS ws
  LEFT JOIN compradores AS c ON c.session_id = ws.session_id
  WHERE ws.region IN ('Madrid', 'Andalucía') AND ws.device IN ('mobile', 'desktop')
)
-- GROUPING SETS: el desglose por región y el agregado en una sola consulta.
SELECT COALESCE(region, 'Ambas') AS region, device, COUNT(*) AS sesiones, SUM(compra) AS compras,
       ROUND(100.0 * SUM(compra) / COUNT(*), 1) AS conversion_pct
FROM sesiones
GROUP BY GROUPING SETS ((region, device), (device))
ORDER BY region, device;
