SELECT year(signup_date) AS anio, COUNT(*) AS clientes,
       ROUND(100.0 * AVG(marketing_consent::INT), 1) AS pct_consentimiento
FROM customers
GROUP BY 1;
