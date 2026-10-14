SELECT plan, COUNT(*) AS suscripciones, ROUND(SUM(mrr_eur), 2) AS mrr
FROM subscriptions
WHERE started_at <= TIMESTAMP '2026-06-30'
  AND (cancelled_at IS NULL OR cancelled_at > TIMESTAMP '2026-06-30')
GROUP BY plan;
