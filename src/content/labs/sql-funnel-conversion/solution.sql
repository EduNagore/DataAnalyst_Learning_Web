-- La unidad de análisis es la sesión: COUNT(DISTINCT session_id) ignora eventos duplicados.
SELECT event_type, COUNT(DISTINCT session_id) AS sesiones
FROM events
GROUP BY event_type;
