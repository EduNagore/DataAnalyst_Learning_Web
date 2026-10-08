# Guía de contenido

Reglas de redacción, fuentes y formato para lecciones, quizzes, labs y casos. Desarrolla el PLAN.md §8-§9. Si algo aquí y en PLAN.md entran en conflicto, gana PLAN.md y se corrige esta guía.

## 1. Estructura obligatoria de una lección

Toda lección (`src/content/lessons/<modulo>/<NN-slug>.mdx`) sigue este orden de secciones (como encabezados `##`, salvo que se indique lo contrario):

1. **Objetivos** — se renderiza automáticamente desde `objectives` del frontmatter; no se repite como prosa en el cuerpo.
2. **Contexto de negocio** (`<BusinessContext>`) — 2-4 frases: la pregunta real de Lumen que motiva el tema. Siempre en primera persona del stakeholder o en tono de pregunta ("¿Por qué ha caído la conversión en marzo?").
3. **Intuición** — el problema que resuelve la técnica, con un ejemplo concreto, sin jerga todavía.
4. **Cómo funciona** — explicación técnica. Fórmulas en KaTeX (`$...$`, `$$...$$`); diagrama Mermaid o gráfico Vega-Lite cuando aporte.
5. **En la práctica** — snippet de lectura (SQL/Python/Excel/DAX) con `<DialectTabs>` si el SQL difiere entre motores, o `<ExcelFn>` si hay una función de hoja de cálculo. Enlace al lab o caso relacionado con `relatedLabs`/`relatedCases`.
6. **Trade-offs y cuándo usarlo / cuándo no** — lista con viñetas, honesta sobre los límites.
7. **Errores comunes** — errores reales que comete un analista, no errores de sintaxis triviales.
8. **Con IA** (opcional; solo si aplica) — cómo acelerar la tarea con un LLM/agente y, siempre, cómo verificar el resultado. Nunca "usa IA para esto" sin el paso de verificación.
9. **En una entrevista** — 2-3 preguntas típicas con pista de respuesta (no la respuesta completa; eso vive en `/entrevistas/`).
10. **Ideas clave** (`<KeyTakeaways>`) — 3-5 bullets, cada uno una frase autocontenida.
11. **Fuentes** — se renderiza automáticamente desde `sources` del frontmatter. No se listan fuentes a mano en el cuerpo.
12. **Mini-quiz** — se renderiza automáticamente desde el YAML de `src/content/quizzes/`; no se incrusta en el MDX.

Longitud objetivo: 1.500-3.000 palabras (sin contar código). Si una lección pide más de 3.000, probablemente son dos lecciones.

## 2. Voz y estilo

- Español de España, directo, sin relleno ni frases de transición vacías ("Como hemos visto anteriormente...", "Es importante destacar que...").
- Segunda persona ("defines la métrica", no "se define la métrica") salvo en el "Contexto de negocio", que puede ir en boca del stakeholder.
- Términos técnicos en inglés **en cursiva la primera vez** que aparecen en una lección, con la traducción entre paréntesis si no es obvia: _"window functions"_ (funciones de ventana). A partir de ahí, se puede usar el término en inglés sin cursiva ni traducción repetida.
- Sin emojis decorativos. Los iconos de estado (✔/✘/⚠) solo en UI de producto (quizzes, labs), nunca en prosa de lección.
- Ejemplos con el dataset **Lumen** siempre que la técnica lo permita; si no hay forma natural de usar Lumen (p. ej. una técnica muy genérica), usar un ejemplo mínimo y decirlo explícitamente ("fuera de Lumen, para no forzarlo:").
- Nunca "obviamente", "simplemente", "es trivial". Si de verdad es trivial, no hace falta decirlo; si no lo es para quien aprende, es falso y desanima.

## 3. Números, fechas y formato

- Prosa: formato español — `1.234,56 €`, `12,5 %`, fechas largas ("12 de marzo de 2026").
- Código (SQL/Python/fórmulas): formato de la herramienta (punto decimal, `1234.56`), nunca mezclado con el formato español dentro de un bloque de código.
- Fechas en ejemplos de Lumen: usar fechas dentro del rango real del dataset (2023-01-01 a 2026-06-30, ver `docs/DATASET.md`). No usar fechas futuras inventadas fuera de ese rango salvo que la lección sea explícitamente sobre forecasting.
- Nombres de función de hoja de cálculo: siempre con `<ExcelFn en="XLOOKUP" es="BUSCARX" />` (o el componente equivalente), nunca solo el nombre en inglés o solo en español.

## 4. Callouts y componentes de contenido

- `<Snapshot date="2026-10">...</Snapshot>` — obligatorio para cualquier afirmación sobre una herramienta, versión, precio o ranking concreto (contenido `volatility: medium|high`). Formato: "A fecha de {mes AAAA}, ...". Nunca afirmar una cifra o un nombre de producto vigente sin este callout o sin cita.
- `<Callout type="warning|info|tip">` — para advertencias puntuales dentro de una sección (p. ej. "cuidado con la zona horaria aquí").
- `<Term>` — primera aparición de un término del glosario; enlaza automáticamente a `/glosario/#<id>`.
- `<DialectTabs>` — cuando el mismo SQL se escribe distinto según el motor (DuckDB, PostgreSQL, BigQuery, Snowflake, T-SQL). El ejemplo ejecutable del lab siempre usa dialecto DuckDB; las demás pestañas son solo lectura.
- `<SourceList>` / `<KeyTakeaways>` — se insertan automáticamente por el layout de lección a partir del frontmatter; no se escriben a mano en el MDX salvo que la lección tenga una razón explícita para desviarse (documentarla en un comentario MDX).

## 5. Procedimiento de fuentes (ver PLAN.md §8)

1. Antes de escribir una afirmación técnica no trivial, buscarla en una fuente de nivel 1 o 2 **en el momento de redactar**, no de memoria.
2. Si el dato es `volatility: high` (herramientas, versiones, precios, nombres de producto, rankings de benchmarks, normativa): verificar en la fuente oficial, envolver en `<Snapshot date="AAAA-MM">`, y jamás inventar una cifra. Si no se puede verificar, se elimina la afirmación o se marca explícitamente como opinión de alguien citado.
3. Cada lección: mínimo 2 fuentes en el frontmatter (`sources`), con `type` correcto (`paper|docs|blog|spec|book|video|course`) y `year`.
4. Toda fuente usada en cualquier lección se añade también a `docs/SOURCES.md`, agrupada por tema.
5. `lastReviewed` en el frontmatter es la fecha real en que se verificaron las fuentes de esa lección, no la fecha de creación del archivo.
6. Al editar una lección publicada (no al crearla), añadir una entrada en `src/content/changelog/<AAAA-MM-DD>.md` explicando qué cambió y por qué, y actualizar `lastReviewed`.

## 6. Quizzes (ver PLAN.md §6 y §7.2)

- 6-10 preguntas por lección, mezclando dificultad 1-3 y al menos dos tipos distintos (`single`, `multiple`, `truefalse`, `order`, `numeric`, `sql-output`, `formula-output`, `chart-critique`).
- `explanation` siempre justifica la opción correcta **y** por qué cada opción incorrecta plausible lo es (no basta "es la B").
- `ref` apunta al ancla (`#encabezado-en-kebab-case`) de la sección de la lección donde se explica; `scripts/validate-content.mjs` avisa si el ancla no existe.
- Preguntas `numeric`: `tolerance` explícita siempre (absoluta o `rel:X`), nunca dejar la tolerancia por defecto (1e-9) para cálculos que dependan de redondeo intermedio.
- Id de pregunta: `<modulo>-<NN-slug>-q<n>`, único a nivel global (lo comprueba `validate-content.mjs`).

## 7. Labs (ver PLAN.md §7.4)

- `starter`: firmas/estructura y comentarios guía, nunca una solución a medio hacer.
- `solution`: comentada, explicando el _por qué_ de cada paso no obvio, no solo el _qué_.
- Mínimo 4 checks/tests, al menos 1 oculto (`hidden: true` en Python, `hiddenOnVariant: true` en SQL).
- Mensajes de error de los tests: siempre en español, señalando la causa probable ("¿has comprobado duplicados tras el JOIN?"), nunca solo "assertion failed".
- `businessQuestion` en el frontmatter: una frase, en lenguaje de negocio, no "calcula X con SQL".
- `datasets` (labs Python): nombres de tablas de `lumen/` (`orders`), `extra:<nombre>` para `extra/*.csv` y `raw:<nombre>` para los CSV sucios de `lumen_raw/` (se leen con `load_raw`; ojo: pandas lee `n/a` como nulo por defecto). El test oculto de un lab con `raw:` usa un DataFrame pequeño hecho a mano con los casos límite (no hay variante sucia).
- Verifica los labs Python también en Pyodide (`tests/e2e/all-py-labs.spec.ts`): solo usa API común a las versiones de pandas/Polars/DuckDB que carga Pyodide.
- Cifras en lecciones y quizzes: recalcúlalas con el dataset **actual** (el generador se corrigió el 2026-10-08; ver DATASET.md §8).

## 8. Casos guiados (ver PLAN.md §7.6)

- `brief`: email breve y realista de un stakeholder ficticio de Lumen, con un objetivo concreto y, si aplica, una fecha límite.
- Cada `step` es autocontenido: no debe depender de que el alumno recuerde un número exacto de un paso anterior si ese número no se le mostró explícitamente.
- `modelReport`: el informe que escribiría un analista senior — estructura SCR (situación-complicación-resolución, ver M12), con la recomendación primero (BLUF) y los límites del análisis al final.
- `rubric`: checklist de autoevaluación, no otra lista de "hechos a repetir" — cada item evalúa una decisión o una habilidad de comunicación, no un dato.

## 9. Accesibilidad de gráficos y tablas

- Todo gráfico lleva `alt` describiendo la conclusión, no solo el tipo de gráfico ("Las ventas caen un 12 % en marzo por rotura de stock", no "gráfico de líneas").
- Paleta: ver skill `dataviz` del repositorio de herramientas internas y `docs/SOURCES.md` → Cleveland & McGill, Okabe-Ito. Nunca codificar información solo por color.
- Tablas de datos: cabeceras semánticas (`<th scope="col">`), nunca una tabla de datos maquetada solo con `<div>`.
