-- Clientes por año de alta. Falta el porcentaje con consentimiento.
SELECT year(signup_date) AS anio, COUNT(*) AS clientes
FROM customers
GROUP BY 1;
