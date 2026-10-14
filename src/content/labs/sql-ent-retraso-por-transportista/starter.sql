-- Envíos por transportista. ¿Y los que llegan tarde?
SELECT carrier, COUNT(*) AS envios,
       ROUND(100.0 * AVG((actual_date >= promised_date)::INT), 1) AS pct_tarde
FROM shipments
GROUP BY carrier;
