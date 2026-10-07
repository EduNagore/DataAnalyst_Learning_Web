WITH primera AS (
  SELECT customer_id, DATE_TRUNC('month', MIN(order_date)) AS cohorte
  FROM orders
  GROUP BY customer_id
),
activo AS (
  SELECT DISTINCT customer_id, DATE_TRUNC('month', order_date) AS mes
  FROM orders
)
SELECT STRFTIME(p.cohorte, '%Y-%m') AS cohorte,
       COUNT(DISTINCT p.customer_id) AS tamano,
       COUNT(DISTINCT CASE WHEN DATE_DIFF('month', p.cohorte, a.mes) = 1 THEN p.customer_id END) AS retenidos_mes1,
       COUNT(DISTINCT CASE WHEN DATE_DIFF('month', p.cohorte, a.mes) = 3 THEN p.customer_id END) AS retenidos_mes3
FROM primera AS p
JOIN activo AS a USING (customer_id)
WHERE p.cohorte >= DATE '2025-01-01' AND p.cohorte <= DATE '2025-03-01'
GROUP BY p.cohorte
ORDER BY p.cohorte;
