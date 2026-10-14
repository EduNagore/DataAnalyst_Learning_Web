# Forecasting de demanda: modelos clásicos y un modelo fundacional

> Pronostica la demanda diaria de Lumen con una línea base estacional, modelos de statsforecast y un modelo fundacional de series temporales, con backtesting en ventana móvil y una comparación honesta.

- **Dificultad:** ★★★ · **Tiempo estimado:** 14 h
- **Habilidades:** series temporales, backtesting, evaluación de previsiones, comunicación de incertidumbre
- **Herramientas:** statsforecast, pandas, DuckDB, matplotlib, pytest
- **Datos:** el dataset sintético Lumen (se descarga con `scripts/download_data.py`).

## Arranque rápido

```bash
uv sync --extra dev && uv run python scripts/download_data.py && uv run pytest
```

Los ficheros con `TODO` son el punto de partida: complétalos y haz pasar las pruebas (`pytest`) cuando existan.

## Objetivo

Construir un sistema de previsión de la demanda con una evaluación rigurosa: ninguna conclusión sobre «qué modelo es mejor» sin un backtesting honesto y una línea base simple contra la que ganar.

## Lo que entregas

- Una serie diaria (o semanal) de ingresos o unidades por región o categoría.
- Un módulo `backtest.py` con validación de origen móvil y métricas (MAE, MAPE o WAPE, sesgo y cobertura de intervalos), con pruebas.
- Una comparación de al menos: ingenuo estacional, ETS/AutoARIMA (statsforecast) y un modelo fundacional (por ejemplo, Chronos-2, de licencia Apache-2.0).
- Un informe con un pronóstico con intervalos, escenarios y un plan de seguimiento.

## Arquitectura

```text
orders + order_items + calendar ─DuckDB─► serie diaria ► descomposición ► backtesting (origen móvil)
        └► ingenuo estacional | ETS | AutoARIMA | modelo fundacional ► métricas y cobertura ► pronóstico + escenarios
```

## Pasos

1. **Serie:** agrega los ingresos por día (pedidos no cancelados) y rellena huecos; incorpora festivos y eventos del calendario.
2. **Descomposición:** tendencia, estacionalidad semanal y anual, efectos de calendario (Black Friday, rebajas).
3. **Línea base:** ingenuo estacional (mismo día de la semana anterior). Es el rival a batir.
4. **Backtesting:** al menos 8 orígenes móviles con horizonte de 28 días (`rolling_origin`); métricas por horizonte.
5. **Modelos:** `statsforecast` (ETS y AutoARIMA) y un modelo fundacional. Respeta su licencia y condiciones de uso.
6. **Intervalos:** evalúa la cobertura real de los intervalos nominales del 80 % y del 95 %.
7. **Comparación honesta:** tabla de métricas, tiempos de cálculo y dónde falla cada modelo (festivos, picos).
8. **Pronóstico:** próximos 28 días con intervalos y dos escenarios (cambio de precio, campaña) con supuestos explícitos.

## Criterios de evaluación

| Criterio                                            | Puntos |
| --------------------------------------------------- | ------ |
| Serie y calendario correctamente preparados         | 1      |
| Backtesting de origen móvil sin fuga de información | 3      |
| Comparación frente a la línea base y entre modelos  | 2      |
| Evaluación de la cobertura de los intervalos        | 1      |
| Comunicación de la incertidumbre y escenarios       | 2      |
| Pruebas del módulo de backtesting                   | 1      |

## Extensiones

- Previsión jerárquica (región, categoría) con reconciliación.
- Previsión de demanda frente a stock disponible (agotamientos).
- Detección de anomalías frente al pronóstico.
- Modelos con variables externas (festivos, precios, campañas).

## Cómo presentarlo en tu portfolio

Muestra primero la tabla de backtesting frente a la línea base, después el gráfico del pronóstico con su banda. Declara la licencia del modelo fundacional y qué harías en producción (seguimiento del error, reentrenamiento). Un modelo sencillo que gana a la línea base con evidencia vale más que uno complejo sin ella.

---

Página del proyecto con más contexto: `/proyectos/forecasting-de-demanda/` en Data Analyst Academy. Verifica las versiones de las librerías y APIs contra su documentación oficial antes de empezar.
