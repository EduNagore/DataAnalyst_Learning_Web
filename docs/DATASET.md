# El dataset Lumen

Diseño del dataset ficticio sobre el que corre toda la práctica del curso (ver PLAN.md §7.3). Este documento es el contrato que implementa `data-gen/generate.py` en la **Fase 1**; a fecha de escribirlo (F0) el generador todavía no existe — este es su plano.

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
| `orders`                 | 400.000                             | `order_id`, `customer_id`, `order_date` (UTC), `channel`, `device`, `discount_pct`, `shipping_cost`, `status`, `store_id` (nulo si es online)        |
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

| #   | Verdad plantada                                                       | Mecanismo de generación                                                                                                                                      | Dónde se usa                          |
| --- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------- |
| 1   | Estacionalidad semanal + anual, picos en Black Friday/Navidad/rebajas | Multiplicador de demanda por día de la semana y por `calendar.event_name`                                                                                    | Labs de agregación, M17 (forecasting) |
| 2   | Paradoja de Simpson en conversión por dispositivo × región            | Mezcla de tráfico (mobile vs desktop) correlacionada con región, con tasas de conversión condicionales opuestas al agregado                                  | Lab 28, widget `SimpsonExplorer`, M09 |
| 3   | Experimento con _lift_ real conocido                                  | Un experimento con un efecto causal simulado de tamaño fijo (p. ej. +8 % conversión) inyectado en `experiment_metrics` del grupo tratamiento                 | Lab 30, caso #2                       |
| 4   | Experimento con SRM provocado                                         | Un bug de asignación simulado que desequilibra el ratio de `experiment_assignments` (p. ej. 55/45 en vez de 50/50)                                           | Lab 29, caso #3                       |
| 5   | Reducción de varianza con CUPED                                       | Fuerte correlación simulada entre una métrica pre-experimento y la métrica del experimento, en un experimento concreto                                       | Lab 55, widget `CupedDemo`            |
| 6   | Cambio de precio regional en fecha concreta                           | `products`/históricos de precio con un salto de precio en una región (Andalucía) en una fecha fija, sin cambio equivalente en el resto                       | Lab 60-61, caso #4                    |
| 7   | Bug de tracking (eventos duplicados, app v4.2)                        | Para sesiones con `app_version = '4.2.x'` en una ventana de fechas, se duplican eventos `purchase`                                                           | Lab 19, caso #7                       |
| 8   | Retrasos de envío → churn en Lumen+                                   | `shipments.actual_date - promised_date` grande aumenta la probabilidad simulada de `subscriptions.cancelled_at` cercano                                      | Lab 26, lab 59, M15                   |
| 9   | Incrementalidad de campaña < atribución _last-click_                  | Una campaña con gasto alto y atribución _last-click_ alta pero con un "efecto causal verdadero" simulado menor (contrafactual conocido)                      | Lab 31-32, M19                        |
| 10  | Caída de ventas en marzo de 2026 (caso estrella)                      | Combinación simulada de rotura de stock en `inventory_snapshots` de una categoría + cambio de mix de canal en ese mes                                        | Caso #1, lab 41                       |
| 11  | Temas latentes en `support_tickets.text`                              | Generación de texto en español por plantillas por categoría (envío, devoluciones, app, pagos), con una muestra etiquetada a mano para evaluar clasificadores | Labs 68, 69; M28                      |

## 6. `extra/`

Datasets pequeños, no de Lumen, para ilustrar conceptos estadísticos puntuales: cuarteto de Anscombe, _Datasaurus Dozen_, una serie temporal de ejemplo con estacionalidad clara. Cada uno con su fuente y licencia citadas en `docs/SOURCES.md`.

## 7. Cómo regenerar el dataset (Fase 1)

```bash
uv run python data-gen/generate.py --config data-gen/config.yaml
```

El script debe:

1. Fijar la semilla (`numpy.random.default_rng(seed)` + semilla equivalente para `Faker`).
2. Generar las tablas en el orden de sus dependencias (dimensiones antes que hechos).
3. Inyectar cada verdad plantada de la tabla de §5 con sus parámetros explícitos (en `config.yaml`, no mágicos en el código).
4. Escribir `lumen/`, `lumen_raw/`, `lumen_variant/` y `extra/` en `public/data/`.
5. Calcular y escribir `data-gen/checksums.json` (hash SHA-256 por archivo).
6. Un test de CI (Fase 1) regenera el dataset en un runner limpio y compara los checksums: si no coinciden, el build falla (el dataset dejó de ser determinista).

**Límite de tamaño** (PLAN.md §3): el conjunto de `public/data/` debe pesar ≤ 60 MB total, ningún archivo > 25 MB. Si el tamaño generado se acerca al límite, reducir filas de `events`/`web_sessions` (son las tablas más grandes) antes que las demás.
