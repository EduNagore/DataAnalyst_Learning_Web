WITH meses AS (
  SELECT CAST(m AS DATE) AS mes FROM generate_series(DATE '2025-01-01', DATE '2025-12-01', INTERVAL 1 MONTH) AS t(m)
)
SELECT strftime(mes, '%Y-%m') AS mes,
       ROUND(COALESCE(SUM(s.mrr_eur) FILTER (WHERE s.started_at < mes + INTERVAL 1 MONTH
             AND (s.cancelled_at IS NULL OR s.cancelled_at >= mes + INTERVAL 1 MONTH)), 0), 0) AS mrr_fin,
       ROUND(COALESCE(SUM(s.mrr_eur) FILTER (WHERE s.started_at >= mes AND s.started_at < mes + INTERVAL 1 MONTH), 0), 0) AS nuevo,
       ROUND(COALESCE(SUM(s.mrr_eur) FILTER (WHERE s.cancelled_at >= mes AND s.cancelled_at < mes + INTERVAL 1 MONTH), 0), 0) AS perdido
FROM meses CROSS JOIN subscriptions AS s
GROUP BY mes
ORDER BY mes;
