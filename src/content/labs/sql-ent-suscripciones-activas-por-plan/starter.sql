-- Suscripciones por plan. Falta quedarte solo con las activas.
SELECT plan, COUNT(*) AS suscripciones, ROUND(SUM(mrr_eur), 2) AS mrr
FROM subscriptions
GROUP BY plan;
