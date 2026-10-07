-- Sesiones web de junio de 2025 (completo).
SELECT COUNT(*) AS sesiones_junio
FROM web_sessions
WHERE started_at BETWEEN '2025-06-01' AND '2025-06-30';
