# Portfolio web con tres casos

> Publica tu portfolio como un sitio estático con tres casos (pregunta, método, resultado y recomendación) construidos con los proyectos anteriores, un perfil claro y enlaces reproducibles.

- **Dificultad:** ★☆☆ · **Tiempo estimado:** 8 h
- **Habilidades:** comunicación, write-ups, GitHub Pages, presentación de resultados
- **Herramientas:** Markdown, Git, GitHub Pages
- **Datos:** el dataset sintético Lumen (se descarga con `scripts/download_data.py`).

## Arranque rápido

```bash
# Elige tu generador de sitios estático y sigue su documentación
```

Los ficheros con `TODO` son el punto de partida: complétalos y haz pasar las pruebas (`pytest`) cuando existan.

## Objetivo

Convertir tu trabajo en una web sencilla que una persona que contrata pueda recorrer en cinco minutos y que demuestre que sabes plantear una pregunta de negocio, elegir un método, comunicar un resultado y recomendar una acción.

## Lo que entregas

- Un sitio estático publicado en GitHub Pages (con el generador que prefieras: Astro, Eleventy, Jekyll, MkDocs…).
- Una página de inicio con una presentación breve, tus tres casos y enlaces.
- Tres páginas de caso con la estructura: **pregunta → datos → método → resultado → recomendación → límites → cómo reproducirlo**.
- Un README en tu perfil de GitHub que enlace al portfolio.

## Arquitectura

```text
Proyectos anteriores ─► casos escritos (Markdown) ─► sitio estático ─► GitHub Pages
                           └► repositorios reproducibles enlazados
```

## Pasos

1. **Elige tres casos** de entre los proyectos 1-7 que cubran señales distintas (análisis y comunicación, rigor estadístico o causal, ingeniería o IA responsable).
2. **Escribe cada caso** con la plantilla `templates/caso.md`: titular con la conclusión, un gráfico clave y una recomendación.
3. **Presenta tu perfil:** quién eres, qué tipo de problemas te interesa resolver, qué herramientas usas y cómo contactarte.
4. **Construye el sitio** con el generador elegido; accesible, rápido y legible en el móvil.
5. **Publica** en GitHub Pages y comprueba los enlaces.
6. **Revisa con la lista** `checklist-portfolio.md` y pide una revisión externa.
7. **Prepara tu relato oral:** dos minutos por caso.

## Criterios de evaluación

| Criterio                                        | Puntos |
| ----------------------------------------------- | ------ |
| Cada caso empieza por la conclusión y la recomendación | 3 |
| Gráficos claros con títulos que comunican          | 2      |
| Enlaces a repositorios reproducibles               | 2      |
| Sitio accesible, rápido y sin errores              | 1      |
| Perfil claro y honesto (sin inflar herramientas)   | 1      |
| Los límites y la incertidumbre se reconocen         | 1      |

## Extensiones

- Un cuarto caso con IA responsable (proyecto 6 o 7).
- Una entrada de blog sobre un error que cometiste y cómo lo detectaste.
- Versión en inglés de los casos.
- Estadísticas anónimas de visitas respetando la privacidad.

## Cómo presentarlo en tu portfolio

El propio sitio es el portfolio: en el CV, un único enlace; en LinkedIn, tres frases con los resultados de cada caso. Evita datos confidenciales o personales de empleadores o clientes anteriores; usa datos abiertos o sintéticos.

---

Página del proyecto con más contexto: `/proyectos/portfolio-web/` en Data Analyst Academy. Verifica las versiones de las librerías y APIs contra su documentación oficial antes de empezar.
