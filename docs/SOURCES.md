# Fuentes

Bibliografía curada, agrupada por tema. Es el superconjunto de partida (trasladado de PLAN.md §8); cada lección añade aquí cualquier fuente nueva que use, y cada entrada debería acabar enlazada desde al menos una lección en `/fuentes/`. Mientras eso no sea así, esta lista sirve como banco de fuentes verificadas para redactar contenido.

Regla: nivel 1 (primarias) y nivel 2 (expertos reconocidos/blogs técnicos de empresa) se pueden citar directamente; nivel 3 nunca como fuente única (ver PLAN.md §8).

> Todas las URLs deben volver a verificarse en el momento de citarlas en una lección concreta (pueden cambiar o moverse). El workflow `content-freshness.yml` revisa enlaces rotos mensualmente con `lychee`.

## Libros de referencia

- Kohavi, Tang & Xu — _Trustworthy Online Controlled Experiments_ (Cambridge University Press, 2020)
- Hernán & Robins — _Causal Inference: What If_ (CRC Press)
- Huntington-Klein — _The Effect: An Introduction to Research Design and Causality_
- Cunningham — _Causal Inference: The Mixtape_
- Hyndman & Athanasopoulos — _Forecasting: Principles and Practice_ (3.ª ed.; también edición en Python)
- Kimball & Ross — _The Data Warehouse Toolkit_ (3.ª ed.)
- McKinney — _Python for Data Analysis_ (3.ª ed.)
- Wickham — "Tidy Data" (_Journal of Statistical Software_, 2014) y _R for Data Science_ (2.ª ed., solo para los conceptos, no el código R)
- Tufte — _The Visual Display of Quantitative Information_
- Cairo — _How Charts Lie_
- Munzner — _Visualization Analysis & Design_
- Wilkinson — _The Grammar of Graphics_
- Knaflic — _Storytelling with Data_
- Few — _Information Dashboard Design_
- Minto — _The Pyramid Principle_
- Bruce, Bruce & Gedeck — _Practical Statistics for Data Scientists_
- McElreath — _Statistical Rethinking_
- Reis & Housley — _Fundamentals of Data Engineering_
- Huyen — _AI Engineering_

## Estadística, experimentación y causalidad (M13-M15)

- Cleveland & McGill (1984), _Graphical Perception: Theory, Experimentation, and Application to the Development of Graphical Methods_
- Deng et al. (2013) — CUPED
- Johari et al. — "Always Valid Inference" (arXiv:1512.04922)
- Fabijan et al. y Kohavi et al. — pitfalls de experimentación y _sample ratio mismatch_
- Declaración de la ASA sobre p-valores (2016)
- Benjamini & Hochberg (1995) — control de la tasa de falso descubrimiento
- Abadie et al. — control sintético
- Callaway & Sant'Anna (2021) — DiD con adopción escalonada
- Brodersen et al. (2015) — CausalImpact
- Fader, Hardie & Lee (2005) — BG/NBD
- Evan Miller — calculadoras y artículos sobre tamaño de muestra y _peeking_
- Blogs de experimentación de Netflix, Spotify, Airbnb, Booking, Microsoft ExP, Uber
- Ron Kohavi (artículos y curso de experimentación)

## SQL y motores analíticos (M04-M06)

- Documentación oficial: DuckDB, PostgreSQL, BigQuery (incl. sintaxis _pipe_), Snowflake, Databricks SQL, T-SQL
- SQLBI (Marco Russo & Alberto Ferrari) — modelado y DAX

## Python y stack de datos (M07-M09, M21)

- Documentación oficial: pandas (notas de la versión 3.0), Polars (blog y guía de migración a 2.0), Apache Arrow, NumPy, SciPy, statsmodels, scikit-learn
- Documentación oficial: Pyodide, DuckDB-WASM
- Blogs de MotherDuck y DuckDB Labs

## Visualización y BI (M10-M12)

- Datawrapper Academy, FlowingData
- SQLBI para Power BI/DAX; documentación oficial de Microsoft Learn (Power BI, Power Query, Fabric, PBIP/TMDL/PBIR, Copilot)
- Documentación oficial de Tableau, Looker/LookML
- Benn Stancil, Mode/Hex blogs

## Series temporales y forecasting (M17)

- Rob Hyndman (blog)
- Documentación de Nixtla (statsforecast)
- Papers de TimesFM, Chronos, Moirai, TimeGPT (verificar vigencia en cada redacción: es contenido `volatility: high`)

## Analítica por dominio (M18-M20)

- Documentación oficial de Amplitude, Mixpanel, PostHog
- Documentación de Google Meridian, Meta Robyn, PyMC-Marketing
- Cassie Kozyrkov, Randy Au

## Ingeniería analítica y capa semántica (M21-M23)

- Documentación oficial de dbt (Fusion, Core, MetricFlow, Semantic Layer), Cube, LookML
- Open Semantic Interchange — especificación oficial
- Tristan Handy (blog de dbt Labs)
- Apache Iceberg, Delta Lake — documentación oficial

## Gobierno, privacidad y ética (M24)

- AEPD (Agencia Española de Protección de Datos) — guías sobre RGPD/LOPDGDD
- EUR-Lex / Comisión Europea — AI Act (verificar calendario de obligaciones vigente en cada redacción)
- OWASP GenAI Security Project

## IA para analistas (M25-M28)

- Documentación oficial: Anthropic (Claude for Excel, Claude Code), OpenAI, Google (Gemini en Sheets), Microsoft (Copilot en Excel/Power BI)
- Model Context Protocol — especificación oficial (modelcontextprotocol.io)
- Spider 2.0 (Lei et al.), BIRD — benchmarks de text-to-SQL, y los estudios de 2026 sobre errores de anotación en sus leaderboards
- Hamel Husain y Shreya Shankar — evaluación de sistemas con LLM
- Simon Willison — seguridad de agentes, _prompt injection_
- Cube — "Semantic Layer for AI Agents"

## Agentes y arquitecturas (transversal)

- ReAct, Toolformer, Reflexion, "Why Do Multi-Agent LLM Systems Fail?" (MAST)
- Documentación oficial de LangGraph, dbt MCP, servidores MCP de Snowflake/Databricks/BigQuery

## Nivel 3 (nunca como fuente única)

Blogs SEO sin autoría experta, listados "Top 10 herramientas AAAA" sin metodología, Medium/LinkedIn sin autoría experta, contenido generado sin referencias, cifras de salarios o "tendencias 2026" sin fuente primaria identificable.
