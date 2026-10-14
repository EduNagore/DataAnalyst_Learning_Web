# Estudio causal: impacto de un cambio de precio

> Estima con diferencias en diferencias, un control sintético sencillo y análisis de robustez el efecto de la subida de precios en una región de Lumen, y comunica el resultado con sus supuestos.

- **Dificultad:** ★★★ · **Tiempo estimado:** 14 h
- **Habilidades:** inferencia causal, diferencias en diferencias, control sintético, análisis de robustez
- **Herramientas:** pandas, DuckDB, statsmodels, matplotlib, pytest
- **Datos:** el dataset sintético Lumen (se descarga con `scripts/download_data.py`).

## Arranque rápido

```bash
uv sync --extra dev && uv run python scripts/download_data.py && uv run pytest
```

Los ficheros con `TODO` son el punto de partida: complétalos y haz pasar las pruebas (`pytest`) cuando existan.

## Objetivo

Responder con rigor a «¿cuál fue el efecto causal de la subida de precios en Andalucía sobre unidades e ingresos?» cuando no hubo experimento. Es un proyecto que demuestra pensamiento causal y honestidad sobre los supuestos.

## Lo que entregas

- Un informe en Markdown o notebook con el diseño, los resultados y los límites.
- Funciones con pruebas (`did.py`): panel regional mensual, estimador de diferencias en diferencias y control sintético.
- Gráficos de tendencias previas, del efecto estimado y de las pruebas placebo.

## Arquitectura

```text
orders + order_items + customers ─DuckDB─► panel región-mes
        └► tendencias previas ► DiD (regresión con efectos fijos) ► control sintético ► placebos y robustez ► informe
```

## Pasos

1. **Panel:** construye ingresos y unidades por región y mes a partir de los pedidos no cancelados (`build_panel`).
2. **Contexto:** identifica la región tratada, la fecha de la subida y las regiones candidatas a control.
3. **Tendencias previas:** compara la evolución previa de tratada y controles; documenta lo que ves.
4. **DiD:** estima el efecto con una regresión con efectos fijos de región y de mes y errores estándar agrupados; interpreta en %.
5. **Control sintético:** busca pesos no negativos que sumen 1 para reproducir la serie previa de la tratada; estima el efecto como la diferencia posterior.
6. **Robustez:** placebos en fechas falsas y en regiones no tratadas, otros controles, ventanas distintas, efecto de anticipación.
7. **Informe:** efecto en unidades e ingresos con intervalo, margen si es posible, supuestos y qué lo invalidaría.

## Criterios de evaluación

| Criterio                                                   | Puntos |
| ---------------------------------------------------------- | ------ |
| Panel correcto y comprobado                                | 1      |
| Evidencia sobre tendencias previas y elección de controles | 2      |
| DiD bien especificado e interpretado                       | 2      |
| Control sintético correcto                                 | 2      |
| Pruebas de robustez y placebos                             | 2      |
| Comunicación de supuestos y límites                        | 1      |

## Extensiones

- Estimadores robustos para adopción escalonada (por ejemplo, el enfoque de Callaway y Sant'Anna).
- Efecto por categoría de producto y elasticidad.
- Intervalos por inferencia aleatoria (permutación sobre regiones).
- Análisis de margen incluyendo costes.

## Cómo presentarlo en tu portfolio

Estructura el informe como pregunta, diseño, resultado y límites. Un gráfico con tratadas frente a sintético y el efecto con su intervalo vale más que una tabla de regresión. Menciona qué supuesto sería más peligroso (tendencias paralelas, otras intervenciones simultáneas) y cómo lo comprobaste.

---

Página del proyecto con más contexto: `/proyectos/estudio-causal-del-cambio-de-precio/` en Data Analyst Academy. Verifica las versiones de las librerías y APIs contra su documentación oficial antes de empezar.
