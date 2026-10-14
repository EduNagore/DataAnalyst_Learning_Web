# Dashboard en Power BI como proyecto PBIP en Git

> Construye un modelo en estrella con medidas DAX, inteligencia de tiempo y seguridad por filas, guárdalo como proyecto PBIP (TMDL y PBIR) versionado en Git y revisa el diseño con una lista de comprobación.

- **Dificultad:** ★★☆ · **Tiempo estimado:** 12 h
- **Habilidades:** modelo en estrella, DAX, inteligencia de tiempo, diseño de dashboards, control de versiones
- **Herramientas:** Power BI Desktop, DAX, Power Query, Git
- **Datos:** el dataset sintético Lumen (se descarga con `scripts/download_data.py`).

## Arranque rápido

```bash
python scripts/download_data.py
```

Los ficheros con `TODO` son el punto de partida: complétalos y haz pasar las pruebas (`pytest`) cuando existan.

## Objetivo

Crear un dashboard ejecutivo de Lumen de calidad profesional y guardarlo como **proyecto de Power BI Desktop (PBIP)**, de modo que modelo e informe sean ficheros de texto que se pueden revisar, comparar y versionar en Git. Alternativa si no puedes usar Power BI Desktop: Tableau Public o Looker Studio (adapta las medidas y los criterios).

## Lo que entregas

- Un proyecto PBIP en Git: carpeta del modelo semántico (TMDL) y carpeta del informe (PBIR).
- Un modelo en estrella con tabla de fechas propia y relaciones uno-a-muchos.
- Al menos 12 medidas DAX en una carpeta de medidas, con inteligencia de tiempo (año anterior, acumulado del año, media móvil).
- Una página ejecutiva (5-8 indicadores) y una página de análisis.
- Seguridad a nivel de fila (RLS) por región, probada.
- Una nota de diseño con la lista de comprobación aplicada y capturas.

## Arquitectura

```text
Parquet/CSV de Lumen ─Power Query─► modelo en estrella ─DAX─► informe (PBIR) ─► Servicio de Power BI (opcional)
        └──────────────── proyecto PBIP en Git (TMDL + PBIR) ───────────────┘
```

## Pasos

1. **Datos:** descarga las tablas con `python scripts/download_data.py` y cárgalas con Power Query (conserva los nombres de columna en inglés y renombra las tablas en español).
2. **Modelo en estrella:** `Ventas` (grano: línea de pedido), `Clientes`, `Productos`, `Fechas`, `Regiones`. Oculta claves y columnas técnicas.
3. **Tabla de fechas:** continua, con año, trimestre, mes, semana ISO y marca de festivos. Márcala como tabla de fechas.
4. **Medidas:** usa `measures.dax` como guía: ingresos, ingresos netos de devoluciones, pedidos, ticket medio, clientes activos, margen, comparaciones con el año anterior y acumulados.
5. **Diseño:** página ejecutiva con KPI y variaciones frente al año anterior, tendencia mensual, desglose por región y categoría; títulos que dicen la conclusión; paleta apta para daltonismo.
6. **Seguridad:** rol por región con filtro DAX; prueba con «Ver como».
7. **Guarda como PBIP:** `Archivo > Guardar como > Proyecto de Power BI`, añade `.gitignore` para la caché local y haz commits con mensajes claros.
8. **Revisión:** aplica `checklist-dashboard.md` y corrige.

## Criterios de evaluación

| Criterio                                                                       | Puntos |
| ------------------------------------------------------------------------------ | ------ |
| Modelo en estrella correcto, con tabla de fechas                               | 2      |
| Medidas DAX correctas y bien organizadas (comprobadas contra una consulta SQL) | 3      |
| Diseño claro: jerarquía, color, accesibilidad                                  | 2      |
| RLS funcionando y probada                                                      | 1      |
| Proyecto PBIP limpio en Git, con historial legible                             | 1      |
| Nota de diseño con decisiones y límites                                        | 1      |

## Extensiones

- Modelo compuesto o Direct Lake si dispones de capacidad de Fabric.
- Funciones DAX definidas por el usuario para reutilizar lógica.
- Pipeline de despliegue con revisión de cambios en el repositorio.
- Una versión del mismo dashboard en Tableau o Looker Studio para comparar enfoques.

## Cómo presentarlo en tu portfolio

Muestra capturas de la página ejecutiva y del modelo en estrella, enlaza al repositorio PBIP (la diferencia entre ficheros de texto impresiona más que un `.pbix` opaco), explica tres decisiones (grano, tabla de fechas, medidas frente a columnas calculadas) y cuenta cómo validaste que las cifras cuadran con SQL. Comprueba en la documentación de Microsoft el estado actual de los formatos PBIP, TMDL y PBIR.

---

Página del proyecto con más contexto: `/proyectos/dashboard-power-bi-pbip/` en Data Analyst Academy. Verifica las versiones de las librerías y APIs contra su documentación oficial antes de empezar.
