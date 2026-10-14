# Análisis completo de un experimento en un notebook marimo

> Analiza un experimento de Lumen de principio a fin: comprobaciones de validez (SRM), potencia, CUPED, análisis secuencial y recomendación, en un notebook reactivo marimo exportado a HTML.

- **Dificultad:** ★★★ · **Tiempo estimado:** 12 h
- **Habilidades:** experimentación, estadística, reducción de varianza, comunicación
- **Herramientas:** marimo, pandas, DuckDB, statsmodels, pytest
- **Datos:** el dataset sintético Lumen (se descarga con `scripts/download_data.py`).

## Arranque rápido

```bash
uv sync --extra dev && uv run python scripts/download_data.py && uv run pytest && uv run marimo edit notebook.py
```

Los ficheros con `TODO` son el punto de partida: complétalos y haz pasar las pruebas (`pytest`) cuando existan.

## Objetivo

Hacer el análisis de un A/B test como lo haría un equipo de experimentación: comprobar primero que el experimento es válido, estimar el efecto con su incertidumbre, aplicar CUPED, explorar segmentos con corrección y terminar con una recomendación de negocio clara.

## Lo que entregas

- Un notebook `notebook.py` de marimo reproducible y exportado a HTML.
- Funciones reutilizables con pruebas en `analysis.py` (SRM, CUPED, intervalos).
- Un resumen de una página para dirección con la decisión y los riesgos.

## Arquitectura

```text
experiments + experiment_assignments + experiment_metrics (Parquet) ─DuckDB─► pandas
        └► SRM ► potencia ► efecto + IC ► CUPED ► segmentos corregidos ► recomendación (HTML)
```

## Pasos

1. **Datos:** descarga las tablas con `python scripts/download_data.py`; elige un experimento de `experiments` y explora sus asignaciones y métricas.
2. **Validez:** implementa `srm_pvalue` y comprueba el reparto observado frente al diseñado. Si hay SRM, investiga la causa antes de seguir.
3. **Potencia y duración:** con la línea base y el efecto mínimo relevante, calcula el tamaño de muestra y compáralo con el obtenido.
4. **Efecto:** diferencia de medias (o proporciones) con intervalo de confianza; explica el resultado en unidades de negocio.
5. **CUPED:** implementa `cuped_adjust` con una covariable previa; compara la anchura del intervalo antes y después.
6. **Segmentos:** analiza al menos tres segmentos con corrección de comparaciones múltiples (Holm o Benjamini-Hochberg) y deja claro que son exploratorios.
7. **Análisis secuencial (opcional):** simula el efecto de mirar cada día y compara con un diseño de duración fija.
8. **Recomendación:** decisión (lanzar, no lanzar, repetir), confianza, riesgos y siguiente paso.
9. **Exporta:** `marimo export html notebook.py -o salida/notebook.html`.

## Criterios de evaluación

| Criterio                                                    | Puntos |
| ----------------------------------------------------------- | ------ |
| Comprobaciones de validez antes de interpretar              | 2      |
| Estimación correcta del efecto con incertidumbre            | 2      |
| CUPED bien aplicado y su ganancia cuantificada              | 2      |
| Tratamiento correcto de segmentos y comparaciones múltiples | 1      |
| Funciones con pruebas que pasan (`pytest`)                  | 1      |
| Recomendación clara y honesta sobre los límites             | 2      |

## Extensiones

- Método delta para una métrica de ratio con aleatorización por usuario.
- Análisis bayesiano del efecto con pérdida esperada.
- Estimación de la potencia por simulación.
- Simulador interactivo con controles de marimo.

## Cómo presentarlo en tu portfolio

Publica el HTML exportado (GitHub Pages), con el titular de la decisión arriba. Destaca que comprobaste el SRM antes de mirar el efecto, cuánto redujo la varianza CUPED y qué harías si el resultado fuera distinto. Consulta la documentación actual de marimo para exportar y para el uso de celdas reactivas.

---

Página del proyecto con más contexto: `/proyectos/analisis-de-experimento-marimo/` en Data Analyst Academy. Verifica las versiones de las librerías y APIs contra su documentación oficial antes de empezar.
