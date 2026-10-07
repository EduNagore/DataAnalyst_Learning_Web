-- Sesiones que llegan a cada paso del embudo.
-- Columnas esperadas: event_type, sesiones
SELECT event_type, COUNT(*) AS sesiones
FROM events
GROUP BY event_type;
