# El dataset Lumen

Diseño del dataset ficticio sobre el que corre toda la práctica del curso (ver PLAN.md §7.3). Este documento es el contrato que implementa `data-gen/generate.py`.

> **Estado: Fase 1 completada (2026-10-07).** El generador existe, está verificado (integridad referencial, determinismo byte a byte, las 11 verdades plantadas comprobadas sobre los datos reales) y sus salidas están en `public/data/`. Tamaño total ≈ 45 MB (límite 60 MB). Las cifras de filas de abajo son las reales, no una estimación.

## 1. Principios

- **100 % ficticio.** "Lumen" es una empresa de retail omnicanal española inventada; cualquier parecido con una empresa real es casualidad.
- **Determinista.** Una única semilla fija (`config.yaml` → `seed`) determina todo el dataset. Volver a ejecutar el generador con la misma semilla produce byte a byte los mismos archivos Parquet (`checksums.json` lo verifica en CI).
- **Coherente.** Las tablas respetan integridad referencial (no hay `order_id` huérfanos en `order_items`, las fechas de `shipments` son posteriores a las de `orders`, etc.), salvo en la capa `lumen_raw/`, donde los problemas son intencionados y están documentados (ver §4).
- **Con verdades plantadas.** Una decena de hechos conocidos (§5) están cocinados a propósito en los datos para que los labs y casos tengan una respuesta correcta verificable, sin que la web necesite "saber" la respuesta de antemano más que como el resultado de ejecutar la consulta/análisis correcto.
- **Periodo:** 2023-01-01 → 2026-06-30 (3 años y medio). Moneda EUR. Zona horaria de negocio `Europe/Madrid`; los eventos (`web_sessions`, `events`) se registran en UTC a propósito, para que limpiar/convertir zonas horarias sea parte del ejercicio.

## 2. Tablas (capa `lumen/`, Parquet, comprimidas con ZSTD)

| Tabla                    | Filas aprox.                        | Columnas principales                                                                                                                                 |
| ------------------------ | ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `customers`              | 60.000                              | `customer_id`, `signup_date`, `acquisition_channel`, `region`, `province`, `segment`, `marketing_consent`                                            |
| `products`               | 2.000                               | `product_id`, `category_id`, `name`, `price`, `cost`, `brand`                                                                                        |
| `categories`             | ~40                                 | `category_id`, `parent_category_id`, `name`                                                                                                          |
| `stores`                 | 40                                  | `store_id`, `city`, `region`, `size_m2`, `opened_date`                                                                                               |
| `orders`                 | 392.906                             | `order_id`, `customer_id`, `order_date` (UTC), `channel`, `device`, `discount_pct`, `shipping_cost`, `status`, `store_id` (nulo si es online)        |
| `order_items`            | 1.000.000                           | `order_item_id`, `order_id`, `product_id`, `quantity`, `unit_price`                                                                                  |
| `returns`                | ~30.000                             | `return_id`, `order_item_id`, `return_date`, `reason`                                                                                                |
| `shipments`              | ~370.000                            | `shipment_id`, `order_id`, `promised_date`, `actual_date`, `carrier`                                                                                 |
| `inventory_snapshots`    | semanal × producto × tienda/almacén | `snapshot_date`, `product_id`, `location_id`, `stock_qty`                                                                                            |
| `web_sessions`           | ~1.000.000                          | `session_id`, `customer_id` (nulo si anónimo), `started_at` (UTC), `device`, `channel`                                                               |
| `events`                 | ~1.500.000 (muestra)                | `event_id`, `session_id`, `event_type` (`page_view`\|`add_to_cart`\|`checkout`\|`purchase`), `occurred_at` (UTC), `app_version`, `properties` (JSON) |
| `marketing_spend`        | diario × canal                      | `date`, `channel`, `spend_eur`                                                                                                                       |
| `campaigns`              | ~60                                 | `campaign_id`, `channel`, `start_date`, `end_date`, `budget_eur`                                                                                     |
| `experiments`            | ~15                                 | `experiment_id`, `name`, `start_date`, `end_date`, `primary_metric`                                                                                  |
| `experiment_assignments` | por experimento                     | `experiment_id`, `customer_id`, `variant`                                                                                                            |
| `experiment_metrics`     | por experimento × día               | `experiment_id`, `date`, `variant`, `metric_name`, `value`                                                                                           |
| `subscriptions`          | ~25.000 altas históricas            | `subscription_id`, `customer_id`, `plan`, `started_at`, `cancelled_at`, `mrr_eur`                                                                    |
| `support_tickets`        | ~15.000                             | `ticket_id`, `customer_id`, `created_at`, `category`, `text` (español, texto libre), `label` (solo en una muestra etiquetada a mano)                 |
| `calendar`               | diario, 2023-2026                   | `date`, `is_holiday_national`, `is_holiday_regional`, `region`, `event_name` (Black Friday, rebajas de enero/verano, Navidad...)                     |

Diagrama entidad-relación completo: generado en `/datos/` a partir del propio esquema (Fase 1), no mantenido a mano en Markdown para evitar que se desincronice.

## 3. Capa `lumen_variant/`

Mismo esquema exacto que `lumen/`, generada con una **semilla distinta** y ~5 % del tamaño. Los checks ocultos de los labs SQL (`hiddenOnVariant: true`) re-ejecutan la consulta del alumno aquí y comparan contra la solución ejecutada sobre esta misma variante, para que una respuesta con el número correcto "a mano" (copiado de la solución o memorizado) no pase el lab.

## 4. Capa `lumen_raw/` (CSV/JSON "sucios")

Subconjunto de las tablas anteriores (sobre todo `customers`, `orders`, `events`) con problemas de calidad **intencionados y documentados**, para los labs de limpieza (M08, labs 20 y 43):

- Duplicados exactos y casi-duplicados (mismo pedido con `order_id` repetido).
- Nulos en columnas que en `lumen/` están siempre rellenas.
- Fechas en formatos mezclados (`2024-03-01`, `01/03/2024`, `1 de marzo de 2024`).
- Categorías/regiones inconsistentes en mayúsculas/espacios (`"Madrid"`, `"madrid "`, `"MADRID"`).
- Importes con coma decimal en vez de punto (`"1234,56"` como string).
- IDs huérfanos (`order_items` con `product_id` que no existe en `products`).
- Eventos duplicados por un bug real de la app v4.2 (ver verdad plantada #6).

## 5. Verdades plantadas

Documentadas aquí con su mecanismo exacto; la web nunca las revela salvo en la solución del lab/caso correspondiente.

| #   | Verdad plantada                                                       | Mecanismo de generación                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Dónde se usa                          |
| --- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------- |
| 1   | Estacionalidad semanal + anual, picos en Black Friday/Navidad/rebajas | Multiplicador de demanda por día de la semana y por `calendar.event_name`                                                                                                                                                                                                                                                                                                                                                                                                      | Labs de agregación, M17 (forecasting) |
| 2   | Paradoja de Simpson en conversión por dispositivo × región            | El tráfico mobile se concentra en la región de conversión ALTA (Madrid) y el desktop en la de conversión BAJA (Andalucía); mobile convierte peor que desktop en **cada** región, pero al agregar Madrid+Andalucía el orden se invierte. Visible comparando esas dos regiones, no las 16 a la vez (se diluye). Verificado: agregado mobile 6,2 % vs desktop 3,7 %, con Madrid (mobile 7,2 % / desktop 12,0 %) y Andalucía (mobile 1,7 % / desktop 2,5 %) ambas con mobile peor. | Lab 28, widget `SimpsonExplorer`, M09 |
| 3   | Experimento con _lift_ real conocido                                  | Un experimento con un efecto causal simulado de tamaño fijo (p. ej. +8 % conversión) inyectado en `experiment_metrics` del grupo tratamiento                                                                                                                                                                                                                                                                                                                                   | Lab 30, caso #2                       |
| 4   | Experimento con SRM provocado                                         | Un bug de asignación simulado que desequilibra el ratio de `experiment_assignments` (p. ej. 55/45 en vez de 50/50)                                                                                                                                                                                                                                                                                                                                                             | Lab 29, caso #3                       |
| 5   | Reducción de varianza con CUPED                                       | Fuerte correlación simulada entre una métrica pre-experimento y la métrica del experimento, en un experimento concreto                                                                                                                                                                                                                                                                                                                                                         | Lab 55, widget `CupedDemo`            |
| 6   | Cambio de precio regional en fecha concreta                           | `products`/históricos de precio con un salto de precio en una región (Andalucía) en una fecha fija, sin cambio equivalente en el resto                                                                                                                                                                                                                                                                                                                                         | Lab 60-61, caso #4                    |
| 7   | Bug de tracking (eventos duplicados, app v4.2)                        | Para sesiones con `app_version = '4.2.x'` en una ventana de fechas, se duplican eventos `purchase`                                                                                                                                                                                                                                                                                                                                                                             | Lab 19, caso #7                       |
| 8   | Retrasos de envío → churn en Lumen+                                   | `shipments.actual_date - promised_date` grande aumenta la probabilidad simulada de `subscriptions.cancelled_at` cercano                                                                                                                                                                                                                                                                                                                                                        | Lab 26, lab 59, M15                   |
| 9   | Incrementalidad de campaña < atribución _last-click_                  | Una campaña con gasto alto y atribución _last-click_ alta pero con un "efecto causal verdadero" simulado menor (contrafactual conocido)                                                                                                                                                                                                                                                                                                                                        | Lab 31-32, M19                        |
| 10  | Caída de ventas en marzo de 2026 (caso estrella)                      | Rotura de stock de Electrónica del 2026-03-01 al 2026-03-21 (`inventory_snapshots.stock_qty` cae de ~212 a ~1 unidad en los 4 centros): los `order_items` de esa categoría casi desaparecen en la ventana, lo que además desplaza el _mix_ de categorías del periodo                                                                                                                                                                                                           | Caso #1, lab 41                       |
| 11  | Temas latentes en `support_tickets.text`                              | Generación de texto en español por plantillas por categoría (envío, devoluciones, app, pagos), con una muestra etiquetada a mano para evaluar clasificadores                                                                                                                                                                                                                                                                                                                   | Labs 68, 69; M28                      |

## 6. `extra/`

Tres datasets externos reales (no sintéticos, no de Lumen), copiados en `data-gen/lumen/vendor/` desde una fuente pública verificada para no depender de red en el build, y citados en `docs/SOURCES.md`:

- `anscombe.csv` — el cuarteto de Anscombe (44 filas).
- `datasaurus_dozen.csv` — el _Datasaurus Dozen_ (1.846 filas, 13 formas).
- `airline_passengers.csv` — pasajeros aéreos mensuales 1949-1960 (144 filas), la serie clásica de Box & Jenkins.

## 7. Cómo regenerar el dataset

```bash
uv run python data-gen/generate.py                     # usa data-gen/config.yaml y escribe en public/data/
uv run python data-gen/generate.py --config otra.yaml --out otra/ruta --checksums otro.json
```

El script (`data-gen/generate.py` + el paquete `data-gen/lumen/`):

1. Fija la semilla; cada tabla deriva su propio generador determinista con `lumen.rng.sub_rng(seed, "nombre_tabla")` (ver `lumen/rng.py`) — así generar solo una tabla para depurar no cambia los números de las demás.
2. Genera las tablas en el orden de sus dependencias (dimensiones → transacciones → comportamiento → crecimiento), inyectando cada verdad plantada de §5 con sus parámetros explícitos en `config.yaml` (nunca mágicos en el código).
3. Repite todo el proceso con `variant_seed` y `scale.variant` (0.05) para `lumen_variant/`.
4. Corrompe una muestra de `customers`/`orders`/`events` del dataset principal (`lumen.raw_variant`) para `lumen_raw/`.
5. Comprueba, antes de escribir, que las columnas de cada tabla coinciden exactamente con `lumen/schema_doc.py` (si no, falla con un error claro en vez de desincronizarse en silencio).
6. Escribe `lumen/` y `lumen_variant/` como Parquet (ZSTD), `lumen_raw/` y `extra/` como CSV, y `data-gen/checksums.json` (SHA-256 por archivo).

**Verificado (2026-10-07)**: regenerar dos veces produce `checksums.json` idéntico byte a byte; las 11 verdades plantadas se comprobaron con consultas DuckDB directas sobre el Parquet generado. Tiempo de generación completo: ~15 s. Tamaño total: ~45 MB (límite 60 MB, PLAN.md §3); ningún archivo individual supera los 17 MB (límite 25 MB). **Pendiente**: un job de CI que regenere el dataset en un runner limpio y compare `checksums.json` (para detectar si algún cambio futuro rompe el determinismo).

### Filas por tabla (`lumen/`, escala 1.0)

| Tabla               | Filas                        |     | Tabla                  | Filas     |
| ------------------- | ---------------------------- | --- | ---------------------- | --------- |
| customers           | 60.000                       |     | web_sessions           | 1.000.000 |
| products            | 2.000                        |     | events                 | ~1,7 M    |
| stores              | 40                           |     | marketing_spend        | 7.662     |
| orders              | 392.906                      |     | campaigns              | 60        |
| order_items         | ~1,01 M                      |     | experiments            | 15        |
| returns             | ~71.000 (7 % de order_items) |     | experiment_assignments | 300.000   |
| shipments           | ~365.000                     |     | experiment_metrics     | 1.074     |
| inventory_snapshots | ~1,46 M                      |     | subscriptions          | 25.000    |
| calendar            | 1.277                        |     | support_tickets        | 15.000    |

## 8. Limitaciones conocidas del dataset (a tener en cuenta al escribir contenido)

- `web_sessions`/`events` y `orders` se generan **de forma independiente**: no cuadran entre sí (las sesiones y las compras de `events` no se corresponden con filas de `orders`). Úsalos para analizar el funnel y la conversión dentro de la web, no para reconciliar con ingresos.
- El negocio crece muy deprisa (pedidos: 2023 ≈ 18 k, 2024 ≈ 77 k, 2025 ≈ 168 k, 2026-H1 ≈ 129 k) porque las altas de clientes siguen una rampa creciente y no se pide antes del alta. Evita comparar años de forma ingenua y avisa del crecimiento en cualquier ejemplo interanual.
- La paradoja de Simpson (#2) se manifiesta comparando Madrid y Andalucía, no las 16 regiones a la vez.
- El calendario de festivos regionales es una simplificación ilustrativa.
- **Pedidos más allá del calendario (corregido el 2026-10-08).** El generador relocaliza al principio del alta del cliente los pedidos que la precederían; los que quedaban después del 30-jun-2026 se recortaban a esa fecha y apilaban ~7.100 pedidos el último día (10 veces un día normal). Ahora esos pedidos (y sus líneas, envíos y devoluciones) se descartan al final de `build_lumen`, sin alterar el resto de la generación aleatoria: solo cambia junio de 2026 (−7.094 pedidos). Por eso la tabla `orders` tiene 392.906 filas y no 400.000.
