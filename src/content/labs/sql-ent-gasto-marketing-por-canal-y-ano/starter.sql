-- Gasto por canal. Falta desglosar por año.
SELECT channel, ROUND(SUM(spend_eur), 0) AS gasto
FROM marketing_spend
GROUP BY 1;
