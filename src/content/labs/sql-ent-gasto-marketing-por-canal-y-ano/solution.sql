SELECT year(date) AS anio, channel, ROUND(SUM(spend_eur), 0) AS gasto
FROM marketing_spend
GROUP BY 1, 2;
