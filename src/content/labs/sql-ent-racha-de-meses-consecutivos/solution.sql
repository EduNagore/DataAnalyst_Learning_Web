WITH m AS (
  SELECT DISTINCT customer_id, CAST(date_trunc('month', order_date) AS DATE) AS mes
  FROM orders
  WHERE status <> 'cancelado'
), g AS (
  SELECT customer_id, mes,
         date_diff('month', DATE '2020-01-01', mes)
           - ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY mes) AS grupo
  FROM m
), r AS (
  SELECT customer_id, grupo, COUNT(*) AS racha FROM g GROUP BY 1, 2
)
SELECT COUNT(DISTINCT customer_id) FILTER (WHERE racha >= 3) AS clientes_con_racha_3,
       MAX(racha) AS racha_maxima
FROM r;
