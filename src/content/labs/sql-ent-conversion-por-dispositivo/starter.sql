-- Conversión por dispositivo. ¿Estás contando sesiones o eventos?
SELECT s.device, COUNT(*) AS sesiones, COUNT(*) FILTER (WHERE e.event_type = 'purchase') AS con_compra,
       ROUND(100.0 * COUNT(*) FILTER (WHERE e.event_type = 'purchase') / COUNT(*), 2) AS conversion_pct
FROM web_sessions AS s
JOIN events AS e USING (session_id)
GROUP BY s.device;
