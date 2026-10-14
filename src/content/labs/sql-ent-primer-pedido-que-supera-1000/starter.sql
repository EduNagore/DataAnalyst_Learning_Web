-- Año en que se alcanza 1.000 €. Aquí miras el total, no cuándo se cruzó el umbral.
SELECT year(MAX(o.order_date)) AS anio, COUNT(*) AS clientes
FROM (
  SELECT o.customer_id, MAX(o.order_date) AS order_date, SUM(oi.quantity * oi.unit_price) AS total
  FROM orders AS o JOIN order_items AS oi USING (order_id)
  WHERE o.status <> 'cancelado'
  GROUP BY 1
  HAVING SUM(oi.quantity * oi.unit_price) >= 1000
) AS o;
