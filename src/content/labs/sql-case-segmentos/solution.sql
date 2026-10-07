-- CASE evalúa en orden y se detiene en la primera condición verdadera.
SELECT
  CASE
    WHEN date_diff('day', promised_date, actual_date) <= 0 THEN 'a tiempo'
    WHEN date_diff('day', promised_date, actual_date) < 5  THEN 'retraso leve'
    ELSE 'retraso grave'
  END AS puntualidad,
  COUNT(*) AS envios
FROM shipments
GROUP BY puntualidad;
