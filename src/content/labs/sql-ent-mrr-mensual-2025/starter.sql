-- MRR mensual. Esto solo mira las altas del mes, no el MRR acumulado ni las bajas.
SELECT strftime(date_trunc('month', started_at), '%Y-%m') AS mes,
       ROUND(SUM(mrr_eur), 0) AS mrr_fin, ROUND(SUM(mrr_eur), 0) AS nuevo, 0 AS perdido
FROM subscriptions
WHERE year(started_at) = 2025
GROUP BY 1
ORDER BY 1;
