SELECT c.region, COUNT(*) AS envios_tarde,
       ROUND(quantile_cont(date_diff('day', s.promised_date, s.actual_date), 0.9), 1) AS p90_dias
FROM shipments AS s
JOIN orders AS o USING (order_id)
JOIN customers AS c USING (customer_id)
WHERE s.actual_date > s.promised_date
GROUP BY 1;
