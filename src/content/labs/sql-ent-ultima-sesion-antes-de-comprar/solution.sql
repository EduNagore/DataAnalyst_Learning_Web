WITH p AS (
  SELECT o.order_id, o.customer_id, o.order_date, SUM(oi.quantity * oi.unit_price) AS importe
  FROM orders AS o JOIN order_items AS oi USING (order_id)
  WHERE o.status <> 'cancelado' AND o.channel = 'online'
    AND o.order_date >= TIMESTAMP '2026-06-01' AND o.order_date < TIMESTAMP '2026-07-01'
  GROUP BY 1, 2, 3
), s AS (
  SELECT customer_id, started_at, channel
  FROM web_sessions
  WHERE customer_id IS NOT NULL AND started_at >= TIMESTAMP '2026-05-01'
)
SELECT COALESCE(s.channel, 'sin_sesion') AS canal, COUNT(*) AS pedidos, ROUND(SUM(p.importe), 0) AS ingresos
FROM p ASOF LEFT JOIN s ON p.customer_id = s.customer_id AND p.order_date >= s.started_at
GROUP BY 1;
