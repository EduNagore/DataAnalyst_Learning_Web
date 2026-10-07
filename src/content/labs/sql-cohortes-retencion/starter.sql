-- Una fila por cohorte (enero-marzo de 2025).
-- Columnas esperadas: cohorte, tamano, retenidos_mes1, retenidos_mes3
SELECT STRFTIME(DATE_TRUNC('month', MIN(order_date)), '%Y-%m') AS cohorte,
       COUNT(DISTINCT customer_id) AS tamano
FROM orders
GROUP BY customer_id;
