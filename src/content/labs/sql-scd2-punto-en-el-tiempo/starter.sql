-- Ingresos por segmento de cliente EN EL MOMENTO de la compra.
-- Columnas esperadas: segmento, ingresos, pedidos
WITH historial AS (
  SELECT * FROM (VALUES
    ('c1', 'nuevo',    DATE '2025-01-01', DATE '2025-04-01'),
    ('c1', 'habitual', DATE '2025-04-01', DATE '9999-12-31'),
    ('c2', 'nuevo',    DATE '2025-01-01', DATE '9999-12-31')
  ) AS t(cliente, segmento, valido_desde, valido_hasta)
),
pedidos AS (
  SELECT * FROM (VALUES
    ('p1', 'c1', DATE '2025-02-10', 100),
    ('p2', 'c1', DATE '2025-05-05', 200),
    ('p3', 'c2', DATE '2025-06-01',  50)
  ) AS t(pedido, cliente, fecha, importe)
)
SELECT h.segmento, SUM(p.importe) AS ingresos, COUNT(*) AS pedidos
FROM pedidos AS p
JOIN historial AS h ON h.cliente = p.cliente
GROUP BY h.segmento
ORDER BY h.segmento;
