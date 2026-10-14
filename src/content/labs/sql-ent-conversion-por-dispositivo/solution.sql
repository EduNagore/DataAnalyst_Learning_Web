WITH compras AS (
  SELECT DISTINCT session_id FROM events WHERE event_type = 'purchase'
)
SELECT s.device, COUNT(*) AS sesiones, COUNT(c.session_id) AS con_compra,
       ROUND(100.0 * COUNT(c.session_id) / COUNT(*), 2) AS conversion_pct
FROM web_sessions AS s
LEFT JOIN compras AS c USING (session_id)
GROUP BY s.device;
