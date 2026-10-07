-- Límite semiabierto: >= inicio del mes, < inicio del mes siguiente.
SELECT COUNT(*) AS sesiones_junio
FROM web_sessions
WHERE started_at >= TIMESTAMP '2025-06-01'
  AND started_at <  TIMESTAMP '2025-07-01';
